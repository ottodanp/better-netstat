from datetime import datetime
from typing import Optional

from util import *


class Connection:
    _protocol: str
    _local_address: str
    _foreign_address: str
    _local_port: int
    _foreign_port: int
    _state: str
    _process_name: str
    _pid: int
    _relationship: str
    _process: Optional[Process]
    _process_started: float
    _flag: str
    _total_interactions: int = 0
    _total_data: int = 0

    def __init__(self, protocol: str, local_address: str, foreign_address: str, local_port: int, foreign_port: int,
                 state: str, pid: int, process: Optional[Process]):
        self._protocol = protocol
        self._local_address = local_address
        self._foreign_address = foreign_address
        self._local_port = local_port
        self._foreign_port = foreign_port
        self._state = state
        self._pid = pid
        self._process = process
        self._relationship = "LISTENER" if self._state == "LISTEN" else addr_relationship(self._foreign_address)
        self._process_name = self._process.name() if self._process else "UNKNOWN"
        self._process_started = float(self._process.create_time()) if self._process else -1
        self._flag = f"{self._local_address}:{self._local_port} -> {self._foreign_address}:{self._foreign_port}"

    def __iter__(self) -> List[str]:
        started = (
            datetime.fromtimestamp(self._process_started)
            .strftime("%Y-%m-%d %H:%M:%S")
            .split(" ")[1]
        ) if self._process_started != -1 else ""
        started = "" if started == "00:00:00" else started

        yield from [PROTOCOLS[self._protocol], self._local_address, self._local_port, self._foreign_address,
                    self._foreign_port, STATES[self._state], self._pid, self._process_name,
                    RELATIONSHIPS[self._relationship], started, self._total_interactions, self._total_data]

    @property
    def protocol(self) -> str:
        return self._protocol

    @protocol.setter
    def protocol(self, protocol: str) -> None:
        self._protocol = protocol

    @property
    def local_address(self) -> str:
        return self._local_address

    @local_address.setter
    def local_address(self, local_address: str) -> None:
        self._local_address = local_address

    @property
    def foreign_address(self) -> str:
        return self._foreign_address

    @foreign_address.setter
    def foreign_address(self, foreign_address: str) -> None:
        self._foreign_address = foreign_address

    @property
    def local_port(self) -> int:
        return self._local_port

    @local_port.setter
    def local_port(self, local_port: int) -> None:
        self._local_port = local_port

    @property
    def foreign_port(self) -> int:
        return self._foreign_port

    @foreign_port.setter
    def foreign_port(self, foreign_port: int) -> None:
        self._foreign_port = foreign_port

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, state: str) -> None:
        self._state = state

    @property
    def process_name(self) -> str:
        return self._process_name

    @process_name.setter
    def process_name(self, process_name: str) -> None:
        self._process_name = process_name

    @property
    def pid(self) -> int:
        return self._pid

    @pid.setter
    def pid(self, pid: int) -> None:
        self._pid = pid

    @property
    def relationship(self) -> str:
        return self._relationship

    @relationship.setter
    def relationship(self, relationship: str) -> None:
        self._relationship = relationship

    @property
    def process(self) -> Optional[Process]:
        return self._process

    @process.setter
    def process(self, process: Optional[Process]) -> None:
        self._process = process

    @property
    def process_started(self) -> float:
        return self._process_started

    @process_started.setter
    def process_started(self, process_started: float) -> None:
        self._process_started = process_started

    @property
    def flag(self) -> str:
        return self._flag

    @flag.setter
    def flag(self, flag: str) -> None:
        self._flag = flag

    @property
    def total_interactions(self) -> int:
        return self._total_interactions

    @total_interactions.setter
    def total_interactions(self, total_interactions: int) -> None:
        self._total_interactions = total_interactions

    @property
    def total_data(self) -> int:
        return self._total_data

    @total_data.setter
    def total_data(self, total_data: int) -> None:
        self._total_data = total_data
