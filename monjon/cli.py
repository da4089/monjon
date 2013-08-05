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

        self.globals.update(self.functions)

        # Table of listeners, which is installed in the global namespace.
        self.listeners = {}
        self.globals["l"] = self.listeners
        self.nextListener = 1

        # Configuration and history directories.
        self.confdir = os.path.expanduser("~/.monjon")
        self.histfile = os.path.join(self.confdir, "history")

        # Debugger core
        self.dispatcher = monjon.core.Dispatcher()
        return



    def main(self):

        # Blurb
        print(BLURB)

        # Load readline history, if we have one.
        if os.path.exists(self.histfile):
            readline.read_history_file(self.histfile)

        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

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
                #print(sys.exc_info())
            
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


    ####################################################################
    # Commands
    
    def breakpoint(self, *args):
        """Break execution.

        breakpoint(listener, event[, condition])
        breakpoint(socket, event[, condition])
        breakpoint(event[, condition])

        Events are: all, none, accept, read, write, shutdown, reset.

        Condition is a Python conditional expression.  If it evaluates
        to True, execution will break.  Otherwise, execution will
        continue.  The default condition is 'True'."""

        pass
        
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

        # Register in the local namespace
        self.listeners[self.nextListener] = l
        print("=> l[%u] = %s" % (self.nextListener, l))
        self.nextListener += 1

        # Hook it into the event loop
        self.dispatcher.RegisterSource(l)
        return


    def run(self):
        """Execute until breakpoint or C-c."""
        return self.dispatcher.Run()


    def step(self):
        """Execute until the next event only."""
        return self.dispatcher.Step()
        

    ####################################################################
    # Help methods

    def commands(self):
        """List of built-in functions (commands)."""
        print(self.commands.__doc__)
        
    def intro(self):
        """Introduction to monjon."""
        print(self.intro.__doc__)

    def licence(self):
        """Licence text goes here."""
        print(self.licence.__doc__)

        
########################################################################
# FIXME vim magic
