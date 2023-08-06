import asyncio
from typing import Type, Dict, Callable, Optional, Set
from arclet.letoderea.entities.delegate import EventDelegate, Subscriber
from arclet.letoderea.utils import run_always_await

from .interact import InteractiveObject
from .typings import TProtocol, TMProtocol
from ..utilles import IOStatus
from ..utilles.security import UNKNOWN, IdentifierChecker
from .behavior import BaseBehavior
from .event import BasicEvent
from .component import MetadataComponent, Component


class ModuleMetaComponent(MetadataComponent, metaclass=IdentifierChecker):
    io: "BaseModule"
    protocol: TProtocol
    identifier: str = UNKNOWN
    name: str
    usage: str
    description: str


class MediumHandlers(Component):
    io: "BaseModule"

    def add_handler(self, event_type: Type[BasicEvent], handler: Subscriber):
        _may_delegate = getattr(
            self,
            event_type.__name__,
            None
        )
        if not _may_delegate:
            delegate = EventDelegate(event_type)
            delegate += handler
            self.__setattr__(
                event_type.__name__,
                delegate
            )
        else:
            _may_delegate += handler

    def remove_handler(self, event_type: Type[BasicEvent]):
        delattr(
            self,
            event_type.__name__
        )

    def __repr__(self):
        return (
            f"[{self.__class__.__name__}: " +
            f"{' '.join([f'{k}={v}' for k, v in self.__dict__.items() if isinstance(v, EventDelegate)])}]"
        )


class ModuleBehavior(BaseBehavior):
    io: "BaseModule"
    invoke_list: Set[str] = {}

    def activate(self):
        data = self.get_component(ModuleMetaComponent)
        data.protocol.verify(self.interactive_object)
        data.state = IOStatus.ESTABLISHED

    async def invoke(self, method_name: str, time: float):
        if method_name not in self.invoke_list:
            self.invoke_list.add(method_name)
            await asyncio.sleep(time)
            await run_always_await(self.__getattribute__(method_name))

    async def invoke_repeating(self, method_name: str, time: float, repeating_rate: float):
        if method_name not in self.invoke_list:
            self.invoke_list.add(method_name)
            await asyncio.sleep(time)
        while method_name in self.invoke_list:
            await run_always_await(self.__getattribute__(method_name))
            await asyncio.sleep(repeating_rate)

    def cancel_invoke(self, method_name: Optional[str] = None):
        if not method_name:
            self.invoke_list.clear()
        else:
            self.invoke_list.remove(method_name)

    def is_invoke(self, method_name: str):
        return method_name in self.invoke_list

    def add_handler(self, event_type: Type[BasicEvent], *reaction: Callable):
        handlers = self.get_component(MediumHandlers)

        def __wrapper(_reaction):
            handlers.add_handler(event_type, Subscriber(_reaction))

        if not reaction:
            return __wrapper
        for r in reaction:
            __wrapper(r)

    async def handler_event(self, event: BasicEvent):
        delegate: EventDelegate = self.get_component(MediumHandlers)[event.__class__.__name__]
        if not delegate:
            return
        self.io.metadata.state = IOStatus.PROCESSING
        await delegate.executor(event)
        self.io.metadata.state = IOStatus.ESTABLISHED


class BaseModule(InteractiveObject):
    prefab_metadata = ModuleMetaComponent
    prefab_behavior = ModuleBehavior
    prefab_handlers = MediumHandlers
    metadata: prefab_metadata
    behavior: prefab_behavior
    handlers: MediumHandlers
    local_storage: Dict = {}

    __slots__ = ["handlers"]

    def __init__(self, protocol: TMProtocol):
        metadata = self.prefab_metadata(self)
        metadata.protocol = protocol
        super().__init__(metadata)
        self.handlers = MediumHandlers(self)
        if self.local_storage.get(self.__class__):
            for k, v in self.local_storage.pop(self.__class__).items():
                self.get_component(self.prefab_behavior).add_handler(k, *v)

    @property
    def name(self):
        return getattr(self.metadata, "name", self.__class__.__name__)

    @property
    def usage(self):
        return getattr(self.metadata, "usage", None)

    @property
    def description(self):
        return getattr(self.metadata, "description", None)

    def change_behavior(self, behavior: Type[prefab_behavior]):
        self.behavior = behavior(self)

    @classmethod
    def inject_handler(__module_self__, event_type: Type[BasicEvent], *reaction: Callable):
        if not __module_self__.local_storage.get(__module_self__):
            __module_self__.local_storage.setdefault(__module_self__, {})
        __module_self__.local_storage[__module_self__].setdefault(event_type, reaction)

    def add_handler(__module_self__, event_type: Type[BasicEvent], *reaction: Callable):
        try:
            return __module_self__.behavior.add_handler(event_type, *reaction)
        except AttributeError:
            if not __module_self__.local_storage.get(__module_self__.__class__):
                __module_self__.local_storage.setdefault(__module_self__.__class__, {})
            __module_self__.local_storage[__module_self__.__class__].setdefault(event_type, reaction)

    async def import_event(self, event: BasicEvent):
        await self.get_component(ModuleBehavior).handler_event(event)
