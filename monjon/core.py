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


class Listener:
    """Callback interface for dispatcher clients."""

    def OnBreak(self, breakpoint, context):
        return

    def OnWatch(self, watchpoint, value, context):
        return


class EventSource:

    def __init__(self):
        self._state = None
        return

    def SetBreakpoint(self, event, condition, context):
        """Set a breakpoint on this source.

        Each source maintains a set of breakpoints.  When an event is
        dispatched, the breakpoint conditionals for its source are
        evaluated.  If a match occurs, the listener is invoked."""
        return

    def SetWatchpoint(self, condition, value, context):
        """Set a watchpoint on this source.

        A watchpoint reports the value of a property of the source to
        its listener when its condition is met.  What properties are
        available depends on the type of event source.

        A watchpoint is evaluated for each event, but (unlike a
        breakpoint) does not interrupt execution."""
        return

    def SetListener(self, listener, context):
        """Set the listener for this source.

        The listener must implement the Listener interface."""
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


class Event:
    """Debugger event.

    Created by Listeners and Sessions, Events are queued and processed
    by the Dispatcher.  If running, each Event is matched against the
    configured Breakpoints, and if all pass, the Event is dispatched
    without returning control to the user.  If a breakpoint fails, or
    if single-stepping, control returns to the user after processing
    each Event."""

    def __init__(self):
        self._source = None
        self._event = None
        return

    def Dispatch(self):
        """Continue execution."""
        pass

    def Match(self, breakpoint):
        """Returns True if breakpoint matches this event."""
        pass


class Dispatcher:
    """Processor for debugger events.

    The Dispatcher is the heart of monjon.  It works basically as a
    main loop, in two phases: in the first phase, it creates a set of
    Events by calling select() (or similar); in the second phase,
    these Events are processed.
    """

    def __init__(self):
        self._queue = []
        self._sources = {}
        return

    def RegisterSource(self, source):
        """Register an event source with with the dispatcher.

        Once registered, events occuring on the source will be
        dispatched by the dispatcher."""

        for s in source.GetSockets():
            self._sources[s] = source
        return

    def DeregisterSource(self, source):
        """Remove a source from the dispatcher."""

        for s in source.GetSockets():
            if s in self._sources.keys():
                print("Removing %s from sources" % str(s))
                del self._sources[s]
        return

    def SetBreakpoint(self, source, event, condition):
        return

    def SetWatchpoint(self, source, condition, value):
        return

    def QueueEvent(self, event):
        """Queue an event for processing."""
        self._queue.append(event)
        return

    def Run(self):
        """Gather and process events until breakpoint or C-c"""

        try:
            while self.Step():
                pass
        except KeyboardInterrupt:
            pass

        return

    def Step(self):
        """Process one event, first gathering more if required."""

        try:
            while len(self._queue) < 1:
                #FIXME: this should be plugged in from cli/gui/robot/etc
                l = self._sources.keys()
                r, w, x = select.select(l, l, [], 0)

                for sock in r:
                    source = self._sources.get(sock)
                    if source:
                        source.OnReadable(sock)

                for sock in w:
                    source = self._sources.get(sock)
                    if source:
                        source.OnWritable(sock)

        except KeyboardInterrupt:
            # We got a C-c during select: just return to the command
            # prompt, and we'll get the events next time
            return False

        # Process first waiting event
        event = self._queue.pop(0)
        event.Dispatch()
        return True


class Breakpoint:
    def __init__(self):
        self._source = None
        self._event = None
        self._condition = None
        return


class Watchpoint:
    def __init__(self):
        self._source = None
        self._property = None
        self._condition = None
        return
