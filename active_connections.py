from net import get_netstat
from util import display_connections

DISPLAY_HEADERS = ["Protocol", "Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID",
                   "Process Name", "Network Relationship", "Process Started"]


def main() -> None:
    connections = get_netstat()
    display_connections(connections, DISPLAY_HEADERS)


if __name__ == '__main__':
    main()
