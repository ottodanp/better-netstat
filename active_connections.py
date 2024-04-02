from threading import Thread, Lock
from typing import List

from net import Connection, get_netstat
from util import display_connections, display_loop

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started"]

pause = Lock()


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
            args=(5, self.display_callback, pause)
        )

    def _update_connections(self) -> None:
        self._connections = get_netstat()

    def _input_listener(self) -> None:
        while self.running:
            i = input()
            if i == "q":
                print("Shutting Down...")
                self.stop()

            elif i == "p":
                print("Paused")
                with pause:
                    input("Press Enter to Resume")

    def display_callback(self) -> None:
        self._update_connections()
        display_connections(self._connections, DISPLAY_HEADERS)

    def start(self) -> None:
        self._display_thread.start()
        self._input_listener()

    def stop(self) -> None:
        self._running = False
        self._display_thread.running = False

    @property
    def running(self) -> bool:
        return self._running

    @property
    def paused(self) -> bool:
        return self._paused
