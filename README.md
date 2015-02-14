monjon
======
Network debugger

[![Code Health](https://landscape.io/github/da4089/monjon/master/landscape.svg?style=flat)](https://landscape.io/github/da4089/monjon/master)

monjon is a suite of programs for debugging network communication in
programs.

monjon
  A GUI frontend for debugging network communications issues.

monjon-cli
  A CLI frontend for monjon, suitable for use in a terminal session.

monjon-robot
  A Robot Framework remote protocol server, for integration of monjon
  in system or integration test suites.

monjon-proxy
  A backend process that intercepts network communication between
  client and server applications, and allows it to be single-stepped,
  have breakpoints and watchpoints set, and be examined in the monjon
  frontends.

monjon-wrapper
  A backend process that intercepts network communication system calls
  made by a slaved application, and allows their traffic to be
  single-stepped, etc.  Normally controlled by a monjon frontend.


