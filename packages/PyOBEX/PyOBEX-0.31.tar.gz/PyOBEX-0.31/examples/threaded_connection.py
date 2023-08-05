#!/usr/bin/env python3

# Note: This example lets you handle long connection delays by performing the
# connection in a thread. However, since the connection operation blocks, there
# is no way to terminate the operation from within the thread itself.

import sys
import threading

import bluetooth

from PyOBEX import client, responses


class CallerException(Exception):

    pass


class Caller:

    def __init__(self, timeout=10):

        self.timeout = timeout
        self.result = None
        self.has_result = False

    def _call(self, func, args):

        self.result = func(*args)
        self.has_result = True

    def __call__(self, func, args=()):

        self.has_result = False
        thread = threading.Thread(target=self._call, args=(func, args))
        thread.start()
        thread.join(self.timeout)
        if self.has_result:
            return self.result
        raise CallerException("timed out")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write(
            "Usage: %s <device bluetooth address>\n" % sys.argv[0])
        sys.exit(1)

    device_address = sys.argv[1]

    services = bluetooth.find_service(uuid="1106", address=device_address)
    if not services:
        sys.stderr.write("No file transfer service on the device.\n")
        sys.exit(1)

    port = services[0]["port"]

    c = client.BrowserClient(device_address, port)

    call = Caller()

    try:
        result = call(c.connect)
        if isinstance(result, responses.ConnectSuccess):
            print(call(c.listdir))
            call(c.disconnect)

    except CallerException:
        sys.stderr.write("Connection timed out.\n")

    sys.exit()
