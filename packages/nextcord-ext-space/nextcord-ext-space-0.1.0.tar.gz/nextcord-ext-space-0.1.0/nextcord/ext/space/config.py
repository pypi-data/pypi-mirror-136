import typing
from dataclasses import dataclass

from .flags import EventFlags, OpFlags
from .gateway import SpaceShuttle
from .dawn import Earth
from .recorders.base import BaseRecorder
from .http import Meteor, Pitch

@dataclass
class Configuration:
    recorder: BaseRecorder
    event_flags: EventFlags = EventFlags.all()
    op_flags: OpFlags = OpFlags.all()
    gw_cls: SpaceShuttle = SpaceShuttle
    anal_cls: Earth = Earth
    httpclient_cls: Pitch = Pitch
    session_cls: Meteor = Meteor
    
Config = Configuration