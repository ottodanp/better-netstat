from threading import Thread
from typing import List

from net import Connection, get_netstat
from util import display_connections, display_loop, maximize_terminal, _Getch

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started"]


class ConnectionViewer:
    _running: bool
    _paused: bool
    _connections: List[Connection] = []
    _display_thread: Thread

    def __init__(self):
        self._running = True
        self._paused = False
        self._display_thread = Thread(
            target=display_loop,
            args=(5, self.display_callback, lambda: self.running, lambda: self.paused)
        )

    def _update_connections(self) -> None:
        self._connections = get_netstat()

    def _input_listener(self) -> None:
        getch = _Getch()
        while self.running:
            i = getch()
            if i == "q":
                print("Shutting Down...")
                self._running = False

            elif i == "p":
                self._paused = not self._paused
                print("Paused...") if self.paused else print("Resumed...")

    def display_callback(self) -> None:
        self._update_connections()
        display_connections(self._connections, DISPLAY_HEADERS)

    def begin_display(self) -> None:
        self._display_thread.start()
        self._input_listener()

    @property
    def running(self) -> bool:
        return self._running

    @property
    def paused(self) -> bool:
        return self._paused


if __name__ == '__main__':
    maximize_terminal()
    viewer = ConnectionViewer()
    viewer.begin_display()
