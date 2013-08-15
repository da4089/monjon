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


class Help:
    """A simple string wrapper, used to create help objects in the
    global namespace."""

    def __init__(self, s):
        self.__help__ = s
        return

    def __repr__(self):
        return self.__help__


class CLI:
    """Monjon command-line user interface."""

    def __init__(self):

        # Functions
        self.functions = {}
        self.functions["breakpoint"] = self.breakpoint
        self.functions["exit"] = self.exit
        self.functions["help"] = self.help
        self.functions["history"] = self.history
        self.functions["listen"] = self.listen
        self.functions["load"] = self.load
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
        self.globals["variables"] = self.variables
        # Events
        self.globals["accept"] = accept
        self.globals["client_recv"] = client_recv
        self.globals["server_recv"] = server_recv
        self.globals["close"] = close
        # Protocols
        self.globals["tcp"] = tcp
        self.globals["udp"] = udp

        self.globals.update(self.functions)

        # Configuration and history directories.
        self.confdir = os.path.expanduser("~/.monjon")
        self.histfile = os.path.join(self.confdir, "history")

        # Debugger core
        self.dispatcher = monjon.core.Dispatcher()
        self.dispatcher.set_listener(self)

        # Install table of event sources in namespace.
        self.globals["s"] = self.dispatcher.get_sources()

        # Install table of breakpoints in namespace.
        self.globals["b"] = self.dispatcher.get_breakpoints()

        return

    def main(self):
        """Main function, started when process starts."""

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
        """Main loop."""

        normal = "(monjon) "
        nested = "     ... "
        isIndented = False
        command = ""

        while True:
            # Get next line of input.
            try:
                x = input(nested if isIndented else normal)
            except EOFError:
                print("Use exit() to exit monjon.")
                continue
            except KeyboardInterrupt:
                print("Use exit() to exit monjon.")
                continue

            # Check for continuation lines.
            if x.strip() == "":
                isIndented = False
            elif x[-1] == ":":
                isIndented = True
                command += "\n" + x
                continue
            elif isIndented:
                command += "\n" + x
                continue
            else:
                command = x

            # Execute the assembled command string.
            try:
                exec(command, self.globals)
            except SystemExit:
                break
            except:
                print(traceback.format_exc())

            # Clear the command that was just executed.
            command = ""

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


    def on_break(self, breakpoint, event):
        """Callback from core when breakpoint is hit."""

        print("b[%u]: %s" % (breakpoint.get_name(), event.get_description()))
        self.globals["e"] = event
        self.dispatcher.stop()
        return

    def on_set_breakpoint(self, breakpoint):
        """Callback from core when new breakpoint is created."""

        if breakpoint.get_condition().strip() == 'True':
            cond = "always"
        else:
            cond = "if %s" % breakpoint.get_condition()

        print("b[%u] => %s on s[%u] %s" % (breakpoint.get_name(),
                                           breakpoint.get_event(),
                                           breakpoint.get_source().get_name(),
                                           cond))
        return

    def on_clear_breakpoint(self, breakpoint):
        """Callback from core when breakpoint is cleared."""

        print("b[%u] cleared" % breakpoint.get_name())
        return

    def on_watch(self, watchpoint, value, event):
        """Callback from core when watchpoint is hit."""

        print("Callback for watchpoint")


    ####################################################################
    # Commands

    def breakpoint(self, *args):
        """CLI command to set a breakpoint."""

        if len(args) < 2:
            raise TypeError("breakpoint() missing required arguments")
        
        if isinstance(args[0], monjon.proxy.Listener):
            # Listener
            # FIXME: should this be in monjon.core, not monjon.proxy?
            self.dispatcher.set_breakpoint(args[0], args[1], "True")

        elif isinstance(args[0], monjon.core.EventSource):
            # Session of some sort
            self.dispatcher.set_breakpoint(args[0], args[1], "True")

        else:
            print("Can't handle generic breakpoints yet")

        return

    def exit(self):
        """CLI command to exit the debugger."""

        if os.path.isdir(self.confdir):
            readline.write_history_file(self.histfile)

        sys.exit(0)


    def help(self, *args):
        """CLI command to show online help."""

        if not args:
            args = ["intro"]

        for arg in args:
            if isinstance(arg, str):
                if arg in self.globals:
                    print("    %s\n" % self.globals[arg].__help__)
                else:
                    print("No help available for %s" % arg)

            elif hasattr(arg, "__help__"):
                print("    %s\n" % arg.__help__)

            else:
                print("No help available for %s" % arg)
                print(type(arg))
            
        return


    def history(self):
        """CLI command to print history of previously-executed commands."""

        n = readline.get_current_history_length()
        for i in range(n):
            print(readline.get_history_item(i))

        return


    def load(self, filename):
        """CLI command to load a Python file into the global namespace."""

        # Check file exists.
        if not os.path.isfile(filename):
            print("Cannot import '%s': not a file." % filename)
            return

        # Read file.
        f = open(filename)
        s = f.read()
        f.close()

        # Execute the assembled command string.
        try:
            exec(s, self.globals)
        except SystemExit:
            pass
        except:
            print(traceback.format_exc())

        return
        
            
    def listen(self,
               localPort=0,
               remoteHost=None,
               remotePort=0,
               protocol="tcp"):
        """CLI command to create a proxy session."""

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
        self.dispatcher.register_source(l)

        # Print source name.
        print("s[%u] => %s" % (l.get_name(), l))
        
        return


    def run(self):
        """CLI command to run until breakpoint or interrupt."""

        # Remove any event reference in the global namespace.
        # There'll be one if we're running after a breakpoint.
        if "e" in self.globals.keys():
            del self.globals["e"]

        return self.dispatcher.run()


    def step(self):
        """CLI command to execute until the next event."""
        return self.dispatcher.step()
        

    ####################################################################
    # Help

    breakpoint.__help__ = '''Break execution.

    breakpoint(source, event[, condition])
    breakpoint(event[, condition])

    Break the flow of execution when the specified event occurs for
    the specified source, and condition evaluates true.

    Supported event names are: all, none, accept, server_recv,
    client_recv, close.

    Condition is a Python conditional expression.  If it evaluates to
    True, execution will break.  Otherwise, execution will continue.
    The default condition is "True".'''

    commands = Help('''List of built-in functions (commands).

    breakpoint([source, ]event[, condition])
        Break flow of execution for event matching condition from
        source.
            
    exit()
        Exit monjon.

    history()
        Show the history of previous commands.

    listen(localPort[, remoteHost[, remotePort[, protocol]]])
        Listen for connections on "localPort", and forward to
        "remoteHost" on "remotePort".
            
    run()
        Begin processing events continuously, stopping only for
        breakpoints or if interrupted by the user.

    step()
        Process the next queued event, and then return to the prompt.
        If no events are queued, wait until one occurs.''')

    exit.__help__ = '''Exit the debugger.

    This will close all active network connections.'''

    help.__help__ = '''Show online help.

    Help is available for all commands, and debugger-provided objects.'''

    history.__help__ = '''Show history of previous commands.'''
    
    intro = Help('''Introduction to Monjon.

    Monjon is a debugger for the network communication between
    programs.  It intercepts network traffic and exposes it to its
    user, who can examine and alter the data.
    
    Enter "help(commands)" for a list of available commands.
    Enter "help(variables)" for a list of available variables.''')

    licence = Help('''GPLv3 goes here''')

    listen.__help__ = '''Listen for connections and forward to destination.

    Parameters:
    localPort
    - TCP or UDP port number.
    remoteHost
    - Destination host name or IP address.
    remotePort
    - Destination TCP or UDP port number.  Defaults to same
      as "localPort".
    protocol
    - TCP or UDP; defaults to TCP.

    Listen for connections on "localPort", and forward to
    "remoteHost" on "remotePort".  "protocol" defaults to
    "tcp", but can be overridden by specifying "udp".

    The result is an active Listener, which is added to the
    global sources dictionary: "s".  For example

    (monjon) listen(1234, "localhost", 5678)
    s[0] => <TCP Listener: 1234 -> localhost:5678>
    (monjon) print(s[0].get_sessions())
    []
    (monjon)

    '''

    load.__help__ = '''Load a Python file.

      load("/path/to/file.py")

    The Monjon command line uses the Python programming language to
    allow users to create complex sequences of commands.  In order to
    use this ability, you need to be able to load Python source code.
    
    This function loads the specified Python file into the global
    namespace.  Classes and functions defined in this file will then
    be available to use from the command line.

    Any commands in the file outside of function or class definitions
    are executed during the loading process.'''
    
    run.__help__ = '''Begin processing events continuously, stopping
    only for breakpoints or if interrupted by the user.

    You can interrupt a running session using Control-C.

    Unlike a program debugger, there is no difference between running
    and continuing, so use run() to restart execution following a
    breakpoint as well.'''

    step.__help__ = '''Execute until the next event only.'''

    variables = Help("""

    'b' is a dictionary containing active breakpoints.  When a new
    breakpoint is created, it's added to this dictionary, and its
    index number printed for future reference.

    'e' is the triggering event for a breakpoint or watchpoint.  This
    event is made available only until run() or step() is called after
    a break.
    
    's' is a dictionary containing active event sources.  Event sources
    include configured forwarding ports, and active connected
    sessions.

    'w' is a dictionary containing active watchpoints.""")

########################################################################
# FIXME vim magic
