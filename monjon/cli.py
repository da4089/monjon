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

import os, readline, select, sys, time, traceback, types
import monjon.proxy
import monjon.core


BLURB = """monjon 1.0b1
Copyright (C) 2013 David Arnold.

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.  For
more details, type 'help(licence)'

Type 'help()' for general assistance with usage."""


# Event constants
accept = "accept"
client_recv = "client_recv"
server_recv = "server_recv"
close = "close"

# Protocol constants
tcp = "tcp"
udp = "udp"


class CLI:

    def __init__(self):

        # Functions
        self.functions = {}
        self.functions["breakpoint"] = self.breakpoint
        self.functions["exit"] = self.exit
        self.functions["help"] = self.help
        self.functions["history"] = self.history
        self.functions["listen"] = self.listen
        self.functions["run"] = self.run
        self.functions["step"] = self.step

        # Global namespace
        #
        # Contains help keywords, functions and global variables
        # (eg. listeners, sockets, etc)
        self.globals = {}
        self.globals["commands"] = self.commands
        self.globals["intro"] = self.intro
        self.globals["licence"] = self.licence
        self.globals["license"] = self.licence

        self.globals["accept"] = accept
        self.globals["client_recv"] = client_recv
        self.globals["server_recv"] = server_recv
        self.globals["close"] = close
        self.globals["tcp"] = tcp
        self.globals["udp"] = udp

        self.globals.update(self.functions)

        # Configuration and history directories.
        self.confdir = os.path.expanduser("~/.monjon")
        self.histfile = os.path.join(self.confdir, "history")

        # Debugger core
        self.dispatcher = monjon.core.Dispatcher()
        self.dispatcher.SetListener(self)

        # Install table of event sources in namespace.
        self.globals["s"] = self.dispatcher.GetSources()

        # Install table of breakpoints in namespace.
        self.globals["b"] = self.dispatcher.GetBreakpoints()

        return

    def main(self):

        # Blurb
        print(BLURB)

        # Load readline history, if we have one.
        if os.path.exists(self.histfile):
            readline.read_history_file(self.histfile)

        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

        # Run main loop.
        self.loop()
        return

    def loop(self):
        # Main loop.
        while True:
            try:
                x = input("(monjon) ")
            except EOFError:
                print("Use exit() to exit monjon.")
                continue

            except KeyboardInterrupt:
                print("Use exit() to exit monjon.")
                continue

            try:
                exec(x, self.globals)

            except SystemExit:
                break

            except:
                print(traceback.format_exc())
            
        return


    def complete(self, name, state):
        """Perform tab-completion against the command dictionary."""

        matches = []
        for c in self.functions.keys():
            if c[:len(name)] == name:
                matches.append(c)

        if state > len(matches):
            return None
        else:
            return matches[state]


    def OnBreak(self, breakpoint, event):
        print("BREAK")
        self.globals["e"] = event
        self.dispatcher.Stop()
        return

    def OnSetBreakpoint(self, breakpoint):
        if breakpoint.GetCondition().strip() == 'True':
            cond = "always"
        else:
            cond = "if %s" % breakpoint.GetCondition()

        print("b[%u] => %s on s[%u] %s" % (breakpoint.GetName(),
                                           breakpoint.GetEvent(),
                                           breakpoint.GetSource().GetName(),
                                           cond))
        return

    def OnClearBreakpoint(self, breakpoint):
        print("b[%u] cleared" % breakpoint.GetName())
        return

    def OnWatch(self, watchpoint, value, event):
        print("Callback for watchpoint")


    ####################################################################
    # Commands

    def breakpoint(self, *args):
        """Break execution.

        breakpoint(source, event[, condition])
        breakpoint(event[, condition])

        Break the flow of execution when the specified event occurs
        for the specified source, and condition evaluates true.

        Supported event names are: all, none, accept, server_recv,
        client_recv, close.

        Condition is a Python conditional expression.  If it evaluates
        to True, execution will break.  Otherwise, execution will
        continue.  The default condition is 'True'."""

        if len(args) < 2:
            raise TypeError("breakpoint() missing required arguments")
        
        if isinstance(args[0], monjon.proxy.Listener):
            # Listener
            # FIXME: should this be in monjon.core, not monjon.proxy?
            self.dispatcher.SetBreakpoint(args[0], args[1], "True")

        elif isinstance(args[0], monjon.core.EventSource):
            # Session of some sort
            self.dispatcher.SetBreakpoint(args[0], args[1], "True")

        else:
            print("Can't handle generic breakpoints yet")

        return


    def exit(self):
        """Exit the debugger."""

        if os.path.isdir(self.confdir):
            readline.write_history_file(self.histfile)

        sys.exit(0)


    def help(self, *args):
        """Online help."""

        if not args:
            args = ["intro"]

        for arg in args:
            if isinstance(arg, str):
                if arg in self.globals:
                    print(self.globals[arg].__doc__)
                else:
                    print("No help available for %s" % arg)

            elif isinstance(arg, (types.FunctionType, types.MethodType)):
                print(arg.__doc__)

            else:
                print("No help available for %s" % arg)
                print(type(arg))
            
        return


    def history(self):
        """Print history of previously-executed commands."""

        n = readline.get_current_history_length()
        for i in range(n):
            print(readline.get_history_item(i))

        return


    def listen(self,
               localPort=0,
               remoteHost=None,
               remotePort=0,
               protocol="tcp"):
        """Listen for connections and forward to destination.

        Parameters:
        'localPort' TCP or UDP port number.

        'remoteHost' Destination host name or IP address.

        'remotePort' Destination TCP or UDP port number.  Defaults to
        same as 'localPort'.

        'protocol' TCP or UDP; defaults to TCP.

            Listen for connections on 'localPort', and forward to
            'remoteHost' on 'remotePort'.  'protocol' defaults to
            'tcp', but can be overridden by specifying 'udp'.

            The result is an active Listener, which is added to the
            global sources dictionary: 's'.  For example

            (monjon) listen(1234, "localhost", 5678)
            s[0] => <TCP Listener: 1234 -> localhost:5678>

            (monjon) print(s[0].GetSessions())
            []

            (monjon)

        
        Help for 'listen'"""

        # Create the listener
        if protocol.lower() == "tcp":
            l = monjon.proxy.TCPListener(self.dispatcher,
                                         localPort, remoteHost, remotePort)
        elif protocol.lower() == "udp":
            l = monjon.proxy.UDPListener(self.dispatcher,
                                         localPort, remoteHost, remotePort)
        else:
            print("Undefined protocol '%s': expecting 'tcp' or 'udp'." % protocol)
            return

        # Hook it into the event loop
        self.dispatcher.RegisterSource(l)

        # Print source name.
        print("s[%u] => %s" % (l.GetName(), l))
        
        return


    def run(self):
        """Begin processing events continuously, stopping only for
        breakpoints or if interrupted by the user.

        You can interrupt a running session using Control-C.

        Unlike a program debugger, there's no difference between
        running and continuing, so use run() to restart execution
        following a breakpoint as well."""

        # Remove any event reference in the global namespace.
        # There'll be one if we're running after a breakpoint.
        if "e" in self.globals.keys():
            del self.globals["e"]

        return self.dispatcher.Run()


    def step(self):
        """Execute until the next event only."""
        return self.dispatcher.Step()
        

    ####################################################################
    # Help methods

    def commands(self):
        """List of built-in functions (commands).

        breakpoint([source, ]event[, condition])
            Break flow of execution for event matching condition from
            source.
            
        exit()
            Exit monjon.

        history()
            Show the history of previous commands.

        listen(localPort[, remoteHost[, remotePort[, protocol]]])
            Listen for connections on 'localPort', and forward to
            'remoteHost' on 'remotePort'.
            
        run()
            Begin processing events continuously, stopping only for
            breakpoints or if interrupted by the user.

        step()
            Process the next queued event, and then return to the
            prompt.  If no events are queued, wait until one occurs.
        """
        print(self.commands.__doc__)
        
    def intro(self):
        """Introduction to monjon.

        Enter "help(commands)" for a list of available commands.
        """
        print(self.intro.__doc__)

    def licence(self):
        """Licence text goes here."""
        print(self.licence.__doc__)

    
########################################################################
# FIXME vim magic
