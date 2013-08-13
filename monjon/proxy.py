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

    def __init__(self, dispatcher, localPort, remoteHost, remotePort):
        self.dispatcher = dispatcher

        # Local port.
        self.localPort = localPort

        # Create, bind and listen on socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

        # List of sessions accepted from the listener
        self._sessions = []
        return

    def GetSockets(self):
        """Get the sockets for this listener."""
        return [self.socket]

    def GetSessions(self):
        """Get the active sessions for this listener."""
        return self._sessions

    def OnReadable(self, sock):
        """Callback when socket is readable."""

        assert sock == self.socket
        print("OnReadable")

        # Accept connection.
        #
        # We have to do this here, because otherwise this socket
        # continues to show up as readable, which means we continue to
        # generate events for it.  An alternative would be to remove
        # it from the select() set, but that's harder, so for now we
        # just accept() here, and pass the socket through to the event
        # action.
        s, a = self.socket.accept()

        # Create and queue event
        e = monjon.core.Event(self, "accept")
        e.SetAction(self.DoAccept)
        e.SetContext(s)
        self.dispatcher.QueueEvent(e)
        return

    def DoAccept(self, event):
        # Retrieve the newly accept()ed socket
        s = event.GetContext()

        # Create TCP session object.
        session = TCPSession(self.dispatcher,
                             s,
                             self.remoteHost,
                             self.remotePort)

        # Save in list of sessions.
        self._sessions.append(session)
        return

    def OnWritable(self, sock):
        print("OnWritable")
        return

    def __repr__(self):
        return "<TCP Listener: %u -> %s:%u>" % (self.localPort,
                                                self.remoteHost,
                                                self.remotePort)


class TCPSession(monjon.core.EventSource):
    """ """

    def __init__(self, dispatcher, sock, remoteHost, remotePort):
        self._dispatcher = dispatcher
        self._client = sock
        self._remoteHost = remoteHost
        self._remotePort = remotePort

        self._sourceHost, self._sourcePort = self._client.getpeername()

        # Not yet connected to server.
        self._server = None

        # Connect to remote target.
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to:  %s:%s" % (self._remoteHost, self._remotePort))
        self._server.connect((self._remoteHost, self._remotePort))

        # Add to event loop.
        self._dispatcher.RegisterSource(self)
        return

    def ConnectToServer(self, host, port):
        return

    def SendToClient(self, event):
        buf = event.GetContext()
        self._client.send(buf)
        print("S->C %u bytes" % len(buf))
        return

    def SendToServer(self, event):
        buf = event.GetContext()
        self._server.send(buf)
        print("C->S %u bytes" % len(buf))
        return

    def Close(self, event):
        # Remove from event loop
        self._dispatcher.DeregisterSource(self)

        # Close both sockets
        self._client.close()
        self._client = None
        
        self._server.close()
        self._server = None

        print("closed")
        return

    def GetSockets(self):
        return [self._client, self._server]

    def OnReadable(self, sock):
        if sock == self._client:
            buf = self._client.recv(8192)
            if buf:
                e = monjon.core.Event(self, "server_recv")
                e.SetContext(buf)
                e.SetAction(self.SendToServer)
            else:
                # Zero-length read, so client has closed session
                e = monjon.core.Event(self, "close")
                e.SetAction(self.Close)
        else:
            buf = self._server.recv(8192)
            if buf:
                e = monjon.core.Event(self, "client_recv")
                e.SetContext(buf)
                e.SetAction(self.SendToClient)
            else:
                # Zero-length read, so server has closed session
                e = monjon.core.Event(self, "close")
                e.SetAction(self.Close)

        # Queue event for dispatch
        self._dispatcher.QueueEvent(e)
        return

    def OnWritable(self, sock):
        #print("TCPSession::OnWritable()")
        return

    def __repr__(self):
        return "<TCP Session: %s:%hu -> %s:%hu>" % (self._sourceHost,
                                                    self._sourcePort,
                                                    self._remoteHost,
                                                    self._remotePort)


class UDPListener(Listener):
    """Listens on a single UDP socket.

    Inbound datagrams are allocated to a session based on their source
    IP and port number.  For each such session, we create a new socket
    to act as the outbound endoint.

    In this way, any return traffic to the outbound endpoint can be
    forwarded back to the correct originator."""
    pass

