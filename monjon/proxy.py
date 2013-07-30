#! /usr/bin/env python

import socket


class Listener:
    """Listens for connection attempts, and creates a Session for them."""
    pass

class TCPListener(Listener):

    def __init__(self, localPort, remoteHost, remotePort):
        # Local port.
        self.localPort = localPort

        # Create, bind and listen on socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0", self.localPort))
        self.socket.listen(5)

        # Get actual local port number (in case 'localPort' was zero).
        host, port = self.socket.getsockname()
        self.localPort = port

        # Check that at least one of remote host and port are
        # specified, since otherwise we try to connect to
        # localhost:localport.
        if remotePort == 0 and remoteHost == None:
            print("Cannot use default remote host and default remote port")
            self.socket.close()
            raise AttributeError

        if not remoteHost:
            self.remoteHost = "localhost"
        else:
            self.remoteHost = remoteHost

        if not remotePort:
            self.remotePort = self.localPort
        else:
            self.remotePort = remotePort

        return

    def __str__(self):
        return "TCP:%u -> %s:%u" % (self.localPort, self.remoteHost, self.remotePort)


class UDPListener(Listener):
    """Listens on a single UDP socket.

    Inbound datagrams are allocated to a session based on their source
    IP and port number.  For each such session, we create a new socket
    to act as the outbound endoint.

    In this way, any return traffic to the outbound endpoint can be
    forwarded back to the correct originator."""
    pass

