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
    """Help for breakpoint.

    Clear()
        Deletes this breakpoint.

    GetName()
        Returns the index number in the global breakpoints table for
        this breakpoint.
        
    GetSource()
        Returns the event source for which this breakpoint is defined.

    GetEvent()
        Returns the name of the event that can trigger this breakpoint.

    GetCondition()
        Returns the conditional expresssion that must evaluate to True
        for this breakpoint to break the flow of execution.  The
        default condition is 'True' (which will always break).
    """

    def __init__(self, dispatcher, index, source, event, condition):
        self._dispatcher = dispatcher
        self._name = index
        self._source = source
        self._event = event
        self._condition = condition
        return

    def GetName(self):
        """Returns the index number for this breakpoint."""
        return self._name

    def GetSource(self):
        """Return the source for this breakpoint."""
        return self._source

    def GetEvent(self):
        """Return the event for this breakpoint."""
        return self._event

    def GetCondition(self):
        """Return the condition for this breakpoint."""
        return self._condition

    def Clear(self):
        """Clear this breakpoint."""
        return self._dispatcher.ClearBreakpoint(self)


class Watchpoint:
    """Help for watchpoint."""
    def __init__(self):
        self._source = None
        self._property = None
        self._condition = None
        return


class Listener:
    """Callback interface for dispatcher clients."""

    def OnBreak(self, breakpoint, event):
        return

    def OnWatch(self, watchpoint, value, event):
        return

    def OnSetBreakpoint(self, breakpoint):
        return

    def OnClearBreakpoint(self, breakpoint):
        return


class EventSource:
    """Help for EventSource."""

    def __init__(self):
        self._name = None
        self._state = None
        return

    def GetSockets(self):
        return []

    def OnReadable(self, socket):
        return

    def OnWritable(self, socket):
        return

    def GetState(self):
        return self._state

    def SetState(self, state):
        self._state = state
        return

    def GetName(self):
        return self._name

    def SetName(self, name):
        self._name = name
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

    def GetDescription(self):
        """Get a description of this event, suitable for printing."""

        # FIXME: replace with class hierarchy
        if self._type == "accept":
            # context is new socket
            return ""
        return

    def GetSource(self):
        """Return the source for this event."""
        return self._source

    def SetType(self, eventType):
        """Set the type of this event.

        'eventType' is the name of an event type."""
        self._type = eventType
        return

    def GetType(self):
        """Return the type of this event."""
        return self._type

    def SetAction(self, action):
        """Set the action to be performed for this event.

        'action' callable to be executed."""
        self._action = action
        return

    def GetAction(self):
        """Return the action for this event."""
        return self._action

    def PerformAction(self):
        """Perform the action for this event."""
        self._action(self)
        return

    def SetContext(self, context):
        """Set a context associated with this event.

        'context' a string buffer."""
        self._context = context
        return

    def GetContext(self):
        """Get the Context associated with this event."""
        return self._context



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

    def RegisterSource(self, source):
        """Register an event source with with the dispatcher.

        Once registered, events occuring on the source will be
        dispatched by the dispatcher."""

        # Allocate identifier and update source.
        self._sources[self._nextSource] = source
        source.SetName(self._nextSource)
        self._nextSource += 1

        # Associate its sockets with the source.
        for s in source.GetSockets():
            self._sourceSockets[s] = source
        return

    def DeregisterSource(self, source):
        """Remove a source from the dispatcher."""

        # Remove sockets from table.
        for s in source.GetSockets():
            if s in self._sourceSockets.keys():
                del self._sourceSockets[s]

        # Remove from sources table.
        name = source.GetName()
        del self._sources[name]
        return

    def GetSources(self):
        """Return a reference to the sources table."""

        # FIXME: make read-only
        return self._sources

    def SetBreakpoint(self, source, event, condition):
        """Set a breakpoint for an event on a source matching a condition."""

        if source not in self._breakpoints.keys():
            self._breakpoints[source] = {}

        bp = Breakpoint(self, self._nextBreakpoint, source, event, condition)
        self._breakpoints[source][event] = bp
        self._breakpointIds[self._nextBreakpoint] = bp
        self._nextBreakpoint += 1

        if self._listener:
            self._listener.OnSetBreakpoint(bp)
        return

    def ClearBreakpoint(self, breakpoint):
        """Remove a breakpoint from the dispatcher."""

        if self._listener:
            self._listener.OnClearBreakpoint(breakpoint)

        del self._breakpointIds[breakpoint.GetName()]
        del self._breakpoints[breakpoint.GetSource()][breakpoint.GetEvent()]
        return

    def GetBreakpoints(self):
        """Return a reference to the breakpoints table."""

        # FIXME: make read-only
        return self._breakpointIds

    def SetWatchpoint(self, source, condition, value):
        return

    def SetListener(self, listener):
        """Set the listener for this source.

        The listener must implement the Listener interface."""
        self._listener = listener
        return

    def QueueEvent(self, event):
        """Queue an event for processing."""
        self._queue.append(event)
        return

    def Run(self):
        """Gather and process events until breakpoint or C-c"""

        self._run = True
        
        try:
            while self._run and self.Step():
                pass
        except KeyboardInterrupt:
            pass

        return

    def Stop(self):
        self._run = False
        return

    def Step(self):
        """Process one event, first gathering more if required."""

        try:
            while len(self._queue) < 1:
                #FIXME: this should be plugged in from cli/gui/robot/etc
                l = self._sourceSockets.keys()
                r, w, x = select.select(l, l, [], 0)

                for sock in r:
                    source = self._sourceSockets.get(sock)
                    if source:
                        source.OnReadable(sock)

                for sock in w:
                    source = self._sourceSockets.get(sock)
                    if source:
                        source.OnWritable(sock)

        except KeyboardInterrupt:
            # We got a C-c during select: just return to the command
            # prompt, and we'll get the events next time
            return False

        # Process first waiting event
        event = self._queue.pop(0)
        self.Dispatch(event)
        return True

    def Dispatch(self, event):
        # Check for breakpoints
        source = event.GetSource()
        eventType = event.GetType()
        
        if source in self._breakpoints.keys():
            if eventType in self._breakpoints[source].keys():
                if True: # FIXME: evaluate conditional
                    self.Break(self._breakpoints[source][eventType], event)

        event.PerformAction()
        return

    def Break(self, breakpoint, event):
        # Run watchpoints
        for wp in self._watchpoints:
            self._listener.OnWatch(wp, event)

        # Run breakpoint
        self._listener.OnBreak(breakpoint, event)
        return
        
