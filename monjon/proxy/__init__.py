#! /usr/bin/env python
#
#

# tcp proxy
#
#


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


