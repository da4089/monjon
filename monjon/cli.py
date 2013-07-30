#

import os, readline, sys, time
import monjon.proxy

class CLI:

    def __init__(self):

        # Global namespace
        #
        # Mostly contains "command" functions, plus the table of listeners.
        self.globals = {}
        self.globals["exit"] = self.exit
        self.globals["history"] = self.history
        self.globals["listen"] = self.listen
        self.globals["run"] = self.run

        # Table of listeners, which is installed in the global namespace.
        self.listeners = {}
        self.globals["l"] = self.listeners
        self.nextListener = 1

        # Configuration and history directories.
        self.confdir = os.path.expanduser("~/.monjon")
        self.histfile = os.path.join(self.confdir, "history")
        return


    def main(self):

        # Blurb
        print("monjon 1.0b1")
        print("Copyright (C) 2013, David Arnold")
        print("Enter 'help()' for assistance with usage.")

        # Load readline history, if we have one.
        if os.path.exists(self.histfile):
            readline.read_history_file(self.histfile)

        # Main loop.
        while True:
            try:
                x = input("(monjon) ")

            except EOFError:
                print("Use exit() to exit debugger.")
                continue

            except KeyboardInterrupt:
                print("Use exit() to exit debugger.")
                continue

            try:
                exec(x, self.globals)

            except SystemExit:
                break

            except:
                print(sys.exc_info())
            
        return
        

    def exit(self):
        """Exit the debugger."""

        if os.path.isdir(self.confdir):
            readline.write_history_file(self.histfile)

        sys.exit(0)


    def help(self):
        print("help")
        return


    def history(self):
        """Print history of commands."""

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

        if protocol.lower() == "tcp":
            l = monjon.proxy.TCPListener()
        elif protocol.lower() == "udp":
            l = monjon.proxy.UDPListener()
        else:
            print("Undefined protocol '%s': expecting 'tcp' or 'udp'." % protocol)
            return

        self.listeners[self.nextListener] = l
        print("=> l[%u] = %s" % (self.nextListener, l))
            
        self.nextListener += 1
        return


    def run(self):
        """Start or resume execution."""

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
