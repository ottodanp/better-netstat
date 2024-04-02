from typing import List

from net import Connection, get_netstat
from util import display_connections, display_loop, maximize_terminal

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started"]


class ConnectionViewer:
    _running: bool
    _connections: List[Connection]

    def __init__(self):
        self._running = True

    def update_connections(self) -> None:
        self._connections = get_netstat()

    def display_callback(self) -> None:
        display_connections(self._connections, DISPLAY_HEADERS)

    def begin_display(self) -> None:
        display_loop(
            sleep_time=5,
            callback=self.display_callback,
            condition_callback=self.running
        )

    @property
    def running(self) -> bool:
        return self._running


if __name__ == '__main__':
    maximize_terminal()
    viewer = ConnectionViewer()
    viewer.begin_display()
