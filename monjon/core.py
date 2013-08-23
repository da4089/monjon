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

import select, socket


class Breakpoint:
    """Base class for breakpoints."""

    def __init__(self, dispatcher, index, source, event, condition):
        self._dispatcher = dispatcher
        self._name = index
        self._source = source
        self._event = event
        self._condition = condition
        return

    def get_name(self):
        """Returns the index number for this breakpoint."""
        return self._name

    def get_source(self):
        """Return the source for this breakpoint."""
        return self._source

    def get_event(self):
        """Return the event for this breakpoint."""
        return self._event

    def get_condition(self):
        """Return the condition for this breakpoint."""
        return self._condition

    def clear(self):
        """Clear this breakpoint."""
        return self._dispatcher.clear_breakpoint(self)

    __help__ = """Help for breakpoint.

    clear()
        Deletes this breakpoint.

    get_name()
        Returns the index number in the global breakpoints table for
        this breakpoint.
        
    get_source()
        Returns the event source for which this breakpoint is defined.

    get_event()
        Returns the name of the event that can trigger this breakpoint.

    get_condition()
        Returns the conditional expresssion that must evaluate to True
        for this breakpoint to break the flow of execution.  The
        default condition is 'True' (which will always break)."""


class Watchpoint:
    """Base class for watchpoint."""

    def __init__(self):
        self._source = None
        self._property = None
        self._condition = None
        return

    __help__ = """Help for watchpoint."""


class Listener:
    """Callback interface for dispatcher clients."""

    def on_break(self, breakpoint, event):
        return

    def on_watch(self, watchpoint, value, event):
        return

    def on_set_breakpoint(self, breakpoint):
        return

    def on_clear_breakpoint(self, breakpoint):
        return


class EventSource:
    """Base class for event sources."""

    def __init__(self):
        self._name = None
        self._state = None
        return

    def get_sockets(self):
        return []

    def on_readable(self, socket):
        return

    def on_writeable(self, socket):
        return

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state
        return

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        return

    __help__ = """Help for event source."""


class Packet:
    """A network packet."""

    def __init__(self, bytes, connection):
        self._bytes = bytes
        self._connection = connection
        return

    def get_connection(self):
        """Return reference to the Connection that delivered this Packet."""
        return self._connection

    def get_payload(self):
        """Get the content of this packet."""
        return self._bytes

    def dump(self):
        """Return a formatted dump of the packet's content.

        Print 16 bytes per line, in two groups of 8, showing hex
        values of each byte.  Follow this by a character-oriented
        view, with non-printable characters replaced by a dot. """

        # Result string.
        s = ""

        # String-oriented "preview" assembled and appended to each line.
        p = "|"

        # Index into packet's byte array.
        i = 0

        # Length of packet.
        l = len(self._bytes)

        while i < l:
            if i % 16 == 0:
                # Print offset into packet at start of each line of 16 bytes. 
                s += "%04x   " % i

            b = self._bytes[i]
            s += "%02x " % b
            p += chr(b) if b >= 32 and b < 127 else "."

            if i % 16 == 15:
                # At the end of each row, print the string preview,
                # and then reset it ready for the next line.
                s += "  %s|\n" % p
                p = "|"

            elif i % 8 == 7:
                # Insert an extra gap between the groups of eight bytes.
                s += "  "

            i += 1

        # At the end of the packet, if it's not an exact multiple of
        # 16 bytes in length, pad out the hex bytes display with
        # spaces, and then append the string preview aligned with the
        # other rows.
        if l % 16 != 0:
            for i in range(16 - (l % 16)):
                s += "   "
                p += " "

            s += "  %s|\n" % p

        return s

    __help__ = """A packet."""


class Connection:
    def __init__(self):
        self._listener = None
        self._src = None
        self._dst = None
        self._proto = None
        self._from_c = []
        self._to_c = []

        
        return


class Event:
    """Debugger event.

    Created by Listeners and Sessions, Events are queued and processed
    by the Dispatcher.  If running, each Event is matched against the
    configured Breakpoints, and if all pass, the Event is dispatched
    without returning control to the user.  If a breakpoint fails, or
    if single-stepping, control returns to the user after processing
    each Event."""

    def __init__(self, source, eventType=None):
        """Create an event.

        'source' is the initiating event source.
        'eventType' is the name of an event type."""

        self._source = source
        self._type = eventType
        self._buffer = None
        self._action = None
        self._context = None
        return

    def get_description(self):
        """Get a description of this event, suitable for printing."""

        # FIXME: replace with class hierarchy
        if self._type == "accept":
            # context is (socket, address) tuple
            return "connection from %s:%u accepted" % self._context[1]

        return "event"

    def get_source(self):
        """Return the source for this event."""
        return self._source

    def set_type(self, eventType):
        """Set the type of this event.

        'eventType' is the name of an event type."""
        self._type = eventType
        return

    def get_type(self):
        """Return the type of this event."""
        return self._type

    def set_action(self, action):
        """Set the action to be performed for this event.

        'action' callable to be executed."""
        self._action = action
        return

    def get_action(self):
        """Return the action for this event."""
        return self._action

    def perform_action(self):
        """Perform the action for this event."""
        self._action(self)
        return

    def set_context(self, context):
        """Set a context associated with this event.

        'context' a string buffer."""
        self._context = context
        return

    def get_context(self):
        """Get the Context associated with this event."""
        return self._context

    __help__ = "Help for events."""


class ClientReceiveEvent(Event):
    def __init__(self, source):
        super().__init__(source, "client_recv")
        self._packet = None
        return

    def get_description(self):
        return "received %u bytes from server" % len(self._packet.get_payload())

    def set_packet(self, packet):
        """(Re)set the received packet."""
        self._packet = packet
        return

    def get_packet(self):
        """Get the received packet."""
        return self._packet

    __help__ = """Help for client receive event."""
    
class ServerReceiveEvent(Event):
    def __init__(self, source):
        super().__init__(source, "server_recv")
        self._packet = None
        return

    def get_description(self):
        return "received %u bytes from client" % len(self._packet.get_payload())

    def set_packet(self, packet):
        """(Re)set the received packet."""
        self._packet = packet
        return

    def get_packet(self):
        """Get the received packet."""
        return self._packet

    __help__ = """Help for server receive event."""

class AcceptEvent(Event):
    def __init__(self, source):
        super().__init__(source, "accept")
        self._connection = None
        return

    def get_connection(self):
        """Get the Connection created by this accept event."""
        return self._connection

    __help__ = """Help for accept event."""


class CloseEvent(Event):
    def __init__(self):
        super().__init__(self, source, "close")
        return

    __help__ = """Help for close event."""


class Dispatcher:
    """Processor for debugger events.

    The Dispatcher is the heart of monjon.  It works basically as a
    main loop, in two phases: in the first phase, it creates a set of
    Events by calling select() (or similar); in the second phase,
    these Events are processed.
    """

    def __init__(self):
        # Queue of events to be processed
        self._queue = []

        # Source identifiers
        self._nextSource = 0

        # Table of {id: source}
        self._sources = {}

        # Table of {socket: source}
        self._sourceSockets = {}

        # Breakpoint identifiers
        self._nextBreakpoint = 0

        # Table of {source: {event_type: breakpoint}}
        self._breakpoints = {}

        # Table of {id: breakpoint}
        self._breakpointIds = {}

        # Watchpoint
        self._watchpoints = {}

        # Listener
        self._listener = None

        # Loop control.
        self._run = False
        return

    def register_source(self, source):
        """Register an event source with with the dispatcher.

        Once registered, events occuring on the source will be
        dispatched by the dispatcher."""

        # Allocate identifier and update source.
        self._sources[self._nextSource] = source
        source.set_name(self._nextSource)
        self._nextSource += 1

        # Associate its sockets with the source.
        for s in source.get_sockets():
            self._sourceSockets[s] = source
        return

    def deregister_source(self, source):
        """Remove a source from the dispatcher."""

        # Remove sockets from table.
        for s in source.get_sockets():
            if s in self._sourceSockets.keys():
                del self._sourceSockets[s]

        # Remove from sources table.
        name = source.get_name()
        del self._sources[name]
        return

    def get_sources(self):
        """Return a reference to the sources table."""

        # FIXME: make read-only
        return self._sources

    def set_breakpoint(self, source, event, condition):
        """Set a breakpoint for an event on a source matching a condition."""

        if source not in self._breakpoints.keys():
            self._breakpoints[source] = {}

        bp = Breakpoint(self, self._nextBreakpoint, source, event, condition)
        self._breakpoints[source][event] = bp
        self._breakpointIds[self._nextBreakpoint] = bp
        self._nextBreakpoint += 1

        if self._listener:
            self._listener.on_set_breakpoint(bp)
        return

    def clear_breakpoint(self, breakpoint):
        """Remove a breakpoint from the dispatcher."""

        if self._listener:
            self._listener.on_clear_breakpoint(breakpoint)

        del self._breakpointIds[breakpoint.get_name()]
        del self._breakpoints[breakpoint.get_source()][breakpoint.get_event()]
        return

    def get_breakpoints(self):
        """Return a reference to the breakpoints table."""

        # FIXME: make read-only
        return self._breakpointIds

    def set_watchpoint(self, source, condition, value):
        return

    def set_listener(self, listener):
        """Set the listener for this source.

        The listener must implement the Listener interface."""
        self._listener = listener
        return

    def queue_event(self, event):
        """Queue an event for processing."""
        self._queue.append(event)
        return

    def run(self):
        """Gather and process events until breakpoint or C-c"""

        self._run = True
        
        try:
            while self._run and self.step():
                pass
        except KeyboardInterrupt:
            pass

        return

    def stop(self):
        self._run = False
        return

    def step(self):
        """Process one event, first gathering more if required."""

        try:
            while len(self._queue) < 1:
                #FIXME: this should be plugged in from cli/gui/robot/etc
                l = self._sourceSockets.keys()
                r, w, x = select.select(l, l, [], 0)

                for sock in r:
                    source = self._sourceSockets.get(sock)
                    if source:
                        source.on_readable(sock)

                for sock in w:
                    source = self._sourceSockets.get(sock)
                    if source:
                        source.on_writeable(sock)

        except KeyboardInterrupt:
            # We got a C-c during select: just return to the command
            # prompt, and we'll get the events next time
            return False

        # Process first waiting event
        event = self._queue.pop(0)
        self.dispatch(event)
        return True

    def dispatch(self, event):
        # Check for breakpoints
        source = event.get_source()
        eventType = event.get_type()
        
        if source in self._breakpoints.keys():
            if eventType in self._breakpoints[source].keys():
                if True: # FIXME: evaluate conditional
                    self.do_break(self._breakpoints[source][eventType], event)

        event.perform_action()
        return

    def do_break(self, breakpoint, event):
        # Run watchpoints
        for wp in self._watchpoints:
            self._listener.on_watch(wp, event)

        # Run breakpoint
        self._listener.on_break(breakpoint, event)
        return
        
