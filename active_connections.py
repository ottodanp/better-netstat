from net import get_netstat
from util import display_connections, display_loop, maximize_terminal

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started"]


def callback() -> None:
    connections = get_netstat()
    display_connections(connections, DISPLAY_HEADERS)


def main() -> None:
    display_loop(
        sleep_time=5,
        callback=callback
    )


if __name__ == '__main__':
    maximize_terminal()
    main()
