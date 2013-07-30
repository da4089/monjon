#! /usr/bin/env python
#
#

# tcp proxy
#
#


class Listener:
    """Listens for connection attempts, and creates a Session for them."""
    pass

class TCPListener(Listener):

    def __init__(self):
        self._socket = None


    def get_dispatchers(self):
        if self._socket:
            return [self._socket]
        return []

    def __str__(self):
        return "TCP Listener"


class UDPListener(Listener):
    """Listens on a single UDP socket.

    Inbound datagrams are allocated to a session based on their source
    IP and port number.  For each such session, we create a new socket
    to act as the outbound endoint.

    In this way, any return traffic to the outbound endpoint can be
    forwarded back to the correct originator."""
    pass

    
class Session:

    def get_dispatchers(self):
        """Return list of asyncore dispatcher instances to be
        monitored for this session."""
        
        return []
    
    pass


class TCPSession(Session):
    pass


class UDPSession(Session):
    pass



class Protocol:

    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def create_listener(self, *args):
        return None


class TCPProtocol(Protocol):

    def create_listener(self, port, interface=None, *args):
        l = TCPListener()
        l.set_port(port)
        if interface:
            l.set_interface(interface)
        return l


class Proxy:


    def add_listener(self, listener):
        return

    
