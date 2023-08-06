from concurrent.futures import __annotations__
import concurrent.futures
import asyncio
import aiohttp
import inspect
import sys
import traceback
import threading
import importlib
import time
from typing import Optional
import json

from .httpClient import HTTPClient
from . import utils
from .decorators import Command, Event
from .models.context import BaseContext, ButtonContext, SelectMenuContext
from .models.user import User
from .container import Container
from .errors import CommandNotFound, ComponentNotFound

class MaintainSocketAlive(threading.Thread):
    def __init__(self, *args, **kwargs):
        socket = kwargs.pop('socket')
        interval = kwargs.pop('interval')
        threading.Thread.__init__(self, *args, **kwargs)
        self.socket = socket
        self.interval = interval / 1000
        self.daemon = True
        self._stop_event = threading.Event()
        self._last_ack = time.perf_counter()
        self._last_recv = time.perf_counter()
        self._last_send = time.perf_counter()
        self.latency = float('inf')
        self.main_id = threading.get_ident()

    def run(self):
        while not self._stop_event.wait(self.interval):
            if self._last_recv + 60 < time.perf_counter():
                func = self.socket.close(4000)
                f = asyncio.run_coroutine_threadsafe(func, self.socket.loop)
                try:
                    f.result()
                except Exception:
                    pass
                finally:
                    self.stop()
                    return

            coro = self.socket.send_heartbeat(self.payload())
            f = asyncio.run_coroutine_threadsafe(coro, self.socket.loop)
            try:
                total = 0
                while True:
                    try:
                        f.result(10)
                        break
                    except concurrent.futures.TimeoutError:
                        total += 10
                        try:
                            frame = sys._current_frames()[self.main_id]
                        except KeyError:
                            pass
            except Exception:
                self.stop()
                traceback.print_exc()
            else:
                self._last_send = time.perf_counter()

    def payload(self):
        return {
            "op": 1,
            "d": None
        }

    def stop(self):
        self._stop_event.set()

    def tick(self):
        self._last_recv = time.perf_counter()

    def ack(self):
        ack_time = time.perf_counter()
        self._last_ack = ack_time
        self.latency = ack_time - self._last_send


class Socket:
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None, gateway_version: int = 8) -> None:
        self.loop: asyncio.AbstractEventLoop = loop if loop is not None else asyncio.get_event_loop()
        self.session: aiohttp.BaseConnector = None
        self.headers = {}
        self.thread_id = None
        self.unchecked_decorators = {"events": [], "commands": []}
        self._closed = False
        self.__container = Container()
        self.__handler = None
        self.__gateway = None
        self.__token = None
        self.__http: HTTPClient = None
        self.__gateway_version = gateway_version

    def event(self, name: str):
        """
        Decorator to add an event to listen for.
        ```
        import discsocket
        socket = discsocket.Socket()
        @socket.event('ready')
        async def ready_listener():
            print(f"{socket.user.username} is online")
        ```
        """

        def predicate(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Event function must be a coroutine function.")
            self.unchecked_decorators["events"].append(Event(name, func))
        return predicate

    def command(self, name: str, _type: int):
        """
        Decorator to add a command to listen for.
        ```
        import discsocket
        socket = discsocket.Socket()
        @socket.command('ping', discsocket.utils.SLASH)
        async def ping(ctx):
            await ctx.callback('pong')
        ```
        """

        def predicate(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Command function must be a coroutine function.")
            self.unchecked_decorators["commands"].append(Command(name, func, _type))
        return predicate

    async def send_heartbeat(self, payload):
        await self.__gateway.send_json(payload)

    async  def _before_connect(self):
        self.headers = {"Authorization": "Bot {}".format(self.__token)}
        self.session = aiohttp.ClientSession()
        self.__http = HTTPClient(self.session, self.headers, self.__gateway_version)
        self.user = User(await self.__http.make_request('GET', 'users/@me'))

    async def on_command_error(self, command, exception):
        print(f"Exception in command {command}:")
        raise exception

    async def on_error(self, meth_name, exc):
        print(f"Exception in {meth_name}:")
        raise exc

    async def _run_coro(self, coro, context=None):
        try:
            if context is None:
                await coro()
            else:
                await coro(context)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            try:
                if type(context) != dict:
                    name = context.command if context.command is not None else context.unique_id
                else:
                    name = context['event_name']
                await self.on_error(name,e)
            except asyncio.CancelledError:
                pass    

    def _schedule_task(self, coro, context=None):
        if context is None:
            wrapped = self._run_coro(coro)
        else:
            wrapped = self._run_coro(coro, context)
        return asyncio.create_task(wrapped)

    def dispatch_command(self, data):
        context = BaseContext(self.__http, data)
        match context.type:
            case utils.SLASH:
                coro = self.__container.commands.get(context.command, None)
            case utils.MESSAGE:
                coro = self.__container.message_commands.get(context.command, None)
            case utils.USER:
                coro = self.__container.user_commands.get(context.command, None)

        if coro is None:
            asyncio.create_task(self.on_command_error(context.command, CommandNotFound("Command {} was not found".format(context.command))))

        return self._schedule_task(coro.func, context)

    def dispatch_component(self, data):
        match data['data']['component_type']:
            case 2:
                context = ButtonContext(self.__http, data)
            case 3:
                context = SelectMenuContext(self.__http, data)

        component = self.__container.components.get(context.unique_id, None)
        if component is None:
            print('.')
            return self._schedule_task(self.on_command_error(context.unique_id, ComponentNotFound(f"No component with unique id {context.unique_id} was found"))) 
        return self._schedule_task(component.func, context)

    async def run_component_command(self, context):
        component = self.__container.components.get(context.unique_id, None)
        if component is None:
            t =  asyncio.create_task(self.on_error(context.unique_id, ComponentNotFound(f"No component with unique_id {context.unique_id} was found")))

    async def connect(self):
        await self._before_connect()
        async with self.session.ws_connect('wss://gateway.discord.gg/') as gateway:
            async for message in gateway:
                self.__gateway = gateway
                msg = json.loads(message.data)
                op, t, d = msg['op'], msg['t'], msg['d']
                
                if self.__handler:
                    self.__handler.tick()

                match op:
                    case utils.HELLO:
                        await gateway.send_json(
                            {
                                "op": utils.IDENTIFY,
                                "d": {
                                    "token": self.__token,
                                    "intents": 513,
                                    "properties": {
                                        "$os": "Windows",
                                        "$browser": "discsocket {}".format(utils.__version__),
                                        "$device": "discsocket {}".format(utils.__version__)
                                    },
                                    "compress": False,
                                    "large_threshold": 250
                                }
                            }
                        )

                        self.__handler = MaintainSocketAlive(socket=self, interval=d['heartbeat_interval'])
                        await gateway.send_json(self.__handler.payload())
                        self.__handler.start()
                        
                    case utils.HEARTBEAT:
                        try:
                            if self.__handler:
                                await gateway.send_json(self.__handler.payload())
                        except Exception:
                            traceback.print_exc()

                    case utils.HEARTBEAT_ACK:
                        if self.__handler:
                            self.__handler.ack()

                match t:
                    case 'INTERACTION_CREATE':
                        if d['type'] == 2:
                            self.dispatch_command(d)
                        elif d['type'] == 3:
                            if d['data']['component_type'] == 2:
                                await self.run_component_command(ButtonContext(self.__http, d))

                if t is not None:
                    listeners = self.__container.events.get(t.lower(), None)
                    if listeners is not None:
                        for listener in listeners:
                            if len((inspect.signature(listener.func)).parameters) > 0:
                                d['event_name'] = t.lower()
                                self._schedule_task(listener.func, d)
                            else:
                                self._schedule_task(listener.func)

                    try:
                        listener = self.__getattribute__('on_' + t.lower())
                        if len(inspect.signature(listener).parameters) > 0:
                            self._schedule_task(listener, d)
                        else:
                            self._schedule_task(listener)
                    except AttributeError:
                        pass

    def add_extension(self, path_to_extension: str):
        """
            Loads an extension into the socket.

            ```
            import discsocket
            import pathlib

            socket = discsocket.Socket()

            for ext in [f'{p.parent}.{p.stem} for p in pathlib.Path('extensions').glob('*.py)]:
                socket.add_extension(ext)
            ```
        """
        
        extension = importlib.import_module(path_to_extension)
        func = getattr(extension, 'init_ext')

        func(self)

    def add_ext(self, ext):
        attrs = ext._insert()
        for attr in attrs:
            if isinstance(attr, Command):
                self.__container.add_command(attr)
            elif isinstance(attr, Event):
                self.__container.add_event(attr)

    def run(self, token: str):
        for _type in ['events', 'commands']:
            if len(self.unchecked_decorators[_type]) > 0:
                for item in self.unchecked_decorators[_type]:
                    if isinstance(item, Event):
                        self.__container.add_event(item)
                    elif isinstance(item, Command):
                        self.__container.add_command(item)

        self.__token = token
        self.loop.create_task(self.connect())
        self.loop.run_forever()
