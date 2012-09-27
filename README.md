gitbugz
=======

An experimental simple collection of python scripts for adding commit information from Git to FogBugz On Demand.

It is designed to post edits in a post-receive hook in git using ZeroMQ to a mini-service.
This is to make sure that the post-receive hook in git stays fast. Editing cases via the xml API is
pretty slow - logging in, editing a case and logging out takes more than ten seconds, at least from Sweden.

This is my first attempt at writing software in Python and I selected ZeroMQ as a transport because of
the convenience in the API and also because I was curious to use it.

Requirements:

ZeroMQ Python bindings - pyzmq
Fogbugz Python bindings
Beautifulsoup4 is needed by the Fogbugz Python bindings

easy_install pyzmq
easy_install beautifulsoup4
easy_install fogbugz

If you are using Python 2.6 or earlier you might also need:

easy_install argparse
