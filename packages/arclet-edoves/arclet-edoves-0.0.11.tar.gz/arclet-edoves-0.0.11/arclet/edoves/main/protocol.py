import asyncio
from abc import ABCMeta, abstractmethod
from asyncio import Event
from typing import TYPE_CHECKING, Optional, Union, Type, TypeVar, Dict, Generic
from arclet.letoderea.utils import search_event
from .medium import BaseMedium

from ..utilles.security import UNDEFINED, EDOVES_DEFAULT
from ..utilles.data_source_info import DataSourceInfo
from ..utilles import IOStatus
from .exceptions import ValidationFailed, DataMissing
from .typings import TData
from .context import ctx_module

TM = TypeVar("TM", bound=BaseMedium)

if TYPE_CHECKING:
    from .scene import EdovesScene
    from .config import TemplateConfig
    from .interact import InteractiveObject
    from .module import BaseModule
    from .server_docker import BaseServerDocker
    from .monomer import Monomer


class AbstractProtocol(metaclass=ABCMeta):
    scene: "EdovesScene"
    medium: TData
    storage: Dict[Type["InteractiveObject"], "InteractiveObject"]
    __identifier: str = UNDEFINED

    def __init__(self, scene: "EdovesScene", identifier: str = None):
        self.scene = scene
        if not identifier and self.__identifier == UNDEFINED:
            raise ValidationFailed
        else:
            self.__identifier = identifier
        self.storage = {}
        self.medium_ev: Event = asyncio.Event()

    @property
    def identifier(self):
        return self.__identifier

    @property
    def current(self):
        return list(self.storage.values())[-1]

    def verify(self, other: Union[str, "InteractiveObject"]):
        if other.metadata.identifier == EDOVES_DEFAULT:
            return
        if isinstance(other, str) and other != self.__identifier:
            raise ValidationFailed
        if other.metadata.identifier != self.__identifier:
            other.metadata.state = IOStatus.CLOSED
            raise ValidationFailed

    async def get_medium(
            self,
            event_type: Optional[str] = None,
            medium_type: Optional[Type[TM]] = None
    ) -> Union[TM, TData]:
        if not self.medium:
            await self.medium_ev.wait()
        self.medium_ev.clear()
        if medium_type and not isinstance(self.medium, medium_type):
            return medium_type.create(self.scene.edoves.self, Dict, event_type)(self.medium)
        return self.medium

    def set_medium(self, medium: Union[TM, TData]):
        self.medium = medium
        self.medium_ev.set()

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}>"
        )


class ModuleProtocol(AbstractProtocol):
    storage: Dict[Type["BaseModule"], "BaseModule"]
    medium: BaseMedium

    async def broadcast_medium(self, event_type: str, medium_type: Optional[Type[TM]] = None):
        medium = await self.get_medium(event_type, medium_type)
        for m in self.storage.values():
            if m.metadata.state in (IOStatus.ESTABLISHED, IOStatus.MEDIUM_WAIT):
                with ctx_module.use(m):
                    await m.import_event(search_event(event_type)(medium=medium))


class MonomerProtocol(AbstractProtocol):
    storage: Dict[str, "Monomer"]


class NetworkProtocol(ModuleProtocol):
    storage: Dict[Type["BaseServerDocker"], "BaseServerDocker"]
    source_information: DataSourceInfo
    config: "TemplateConfig"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "source_information"):
            raise DataMissing
        return super(NetworkProtocol, cls).__new__(cls)

    def __init__(self, scene: "EdovesScene", config: "TemplateConfig"):
        self.config = config
        super().__init__(scene, self.source_information.instance_identifier)

    @abstractmethod
    async def parse_raw_data(self, data: TData):
        """将server端传入的原始数据封装"""
        raise NotImplementedError

    @abstractmethod
    async def medium_transport(self, action: str):
        """将来自其他模块的medium传出给server"""
        raise NotImplementedError
