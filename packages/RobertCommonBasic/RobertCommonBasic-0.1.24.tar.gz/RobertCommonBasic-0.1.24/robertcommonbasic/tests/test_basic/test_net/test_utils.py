from robertcommonbasic.basic.net.utils import *


def test_ip():
    print(get_host_name())
    print(get_host_ip())
    adds = get_host_ips()
    for addr in adds:
        print(addr)

test_ip()