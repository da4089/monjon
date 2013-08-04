# -*- python -*-
########################################################################
#HEADER_BEGIN
# Copyright 2013, David Arnold.
#
# This file is part of Monjon.
#
# Monjon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Monjon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Monjon.  If not, see <http://www.gnu.org/licenses/>.
#HEADER_END
########################################################################

import socket
import monjon.core


class Listener(monjon.core.EventSource):
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

    def GetSockets(self):
        """Get the sockets for this listener."""
        return [self.socket]
    
    def OnReadable(self, socket):
        """Callback when socket is readable."""

        assert socket == self.socket

        # accept
        s = self.socket.accept()

        # create TCP session obj
        session = TCPSession(sock, {})
    
        # run breakpoints (accept, new?)
        
        return

    def __str__(self):
        return "TCP:%u -> %s:%u" % (self.localPort, self.remoteHost, self.remotePort)


class TCPSession(monjon.core.EventSource):
    """ """

    def __init__(self, socket, bps):
        self._client = socket

        # Not yet connected to server
        self._server = None

        # Initialise breakpoint lists
        self._bps = {}
        self._bps.update(bps)

        # Run the connect breakpoint(s), if any

        
        return

    def ConnectToServer(self, host, port):
        return

    def SendToClient(self, buf):
        return

    def SendToServer(self, buf):
        return

    def ReceiveFromClient(self, length):
        return

    def ReceiveFromServer(self, length):
        return

    def Close(self):
        return

    def GetSockets(self):
        # FIXME
        return []

    def OnReadable(self):
        return

    def OnWritable(self):
        return





class UDPListener(Listener):
    """Listens on a single UDP socket.

    Inbound datagrams are allocated to a session based on their source
    IP and port number.  For each such session, we create a new socket
    to act as the outbound endoint.

    In this way, any return traffic to the outbound endpoint can be
    forwarded back to the correct originator."""
    pass

