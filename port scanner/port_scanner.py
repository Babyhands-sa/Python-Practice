import socket
import ipaddress
from common_ports import ports_and_services


def get_open_ports(target, port_range, verbose=False):
    if not isinstance(target, str) or target.strip() == "":
        return "Error: Invalid hostname"

    target = target.strip()
    if "://" in target:
        target = target.split("://", 1)[1]
        target = target.split("/", 1)[0]

    is_ip = True
    for letter in target:
        if letter not in "0123456789.":
            is_ip = False

    if is_ip:
        try:
            ip = str(ipaddress.IPv4Address(target))
        except ValueError:
            return "Error: Invalid IP address"
    else:
        try:
            ip = socket.gethostbyname(target)
        except (OSError, UnicodeError):
            return "Error: Invalid hostname"

    if not isinstance(port_range, (list, tuple)) or len(port_range) != 2:
        raise ValueError("Enter a start port and end port")
    start = port_range[0]
    end = port_range[1]
    if type(start) is not int or type(end) is not int:
        raise ValueError("Ports must be whole numbers")
    if start < 1 or end > 65535 or start > end:
        raise ValueError("Enter a valid port range from 1 to 65535")

    open_ports = []
    for port in range(start, end + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
        except OSError:
            pass

    if verbose == False:
        return open_ports

    name = target
    if is_ip:
        try:
            name = socket.gethostbyaddr(ip)[0]
        except OSError:
            name = ""

    if name == "":
        text = "Open ports for " + ip
    else:
        text = "Open ports for " + name + " (" + ip + ")"

    text = text + "\nPORT     SERVICE"
    for port in open_ports:
        if port in ports_and_services:
            service = ports_and_services[port]
        else:
            service = "unknown"
        spaces = " " * (9 - len(str(port)))
        text = text + "\n" + str(port) + spaces + service
    return text
