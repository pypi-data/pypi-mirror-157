A python wrapper for UO-NetDot's RESTful API.

> ⚠ Disclaimer: From 0.2.0 onward, this API wrapper does not ensure support for the [de facto Open Source version of NetDot (GitHub)](https://github.com/cvicente/Netdot).

[![PyPI version](https://badge.fury.io/py/netdot.svg)](https://badge.fury.io/py/netdot)

# Install 

This package is deployed to pypi.org.
Download it with `pip`:

    pip install netdot

# Interactive Usage (Python interpreter)

> ℹ Many methods of `netdot.Repository` and `netdot.dataclasses` are actually runtime-generated code.
> So, using the Repository interactively at the interpreter allows using features like tab completion and ['`help()`' function (discussed in Appendix below)](#appendix-using-help-in-interpreter) to learn more. 

Before getting into building a massive integration/tool, you might jump in and get some experience.
Thankfully, we have the [Python interpreter](https://docs.python.org/3/tutorial/interpreter.html) where we can jump in and do some testing!

    # Enter the Python interpreter by running just "python" in your shell
    $ python
    Python 3.6.15 (default, Sep 10 2021, 00:26:58) 
    ... omitted for brevity...
    >>> import netdot
    >>>

> ℹ The Python interpreter is often referred to as 'a REPL' (Read-Eval-Print-Loop).
> If you are unfamiliar with the Python interpreter, aka 'REPL', you might want to get started by reading ["Using the REPL (in VSCode)" documentation](https://www.learnpython.dev/01-introduction/02-requirements/05-vs-code/04-the-repl-in-vscode/).

With the netdot package imported, you can proceed with setting up a connecting and downloading some data!

## Connecting in the interpreter: `netdot.connect()`

We have enabled interpreter-usage as a first-class feature.
In particular, you will want to use the `connect` function like the following.

> `netdot.connect()` returns a `netdot.Repository` instance.

    >>> import netdot
    >>> repo = netdot.connect()
    What is the URL of the NetDot server? [https://nsdb.uoregon.edu]: ('enter' to use default)
    NetDot username: myusername
    NetDot password: ********** (using getpass module, to securely collect password)

That `repo` can be used for some interactive viewing of NetDot's data.

### Example: Lookup IP Address in interpreter

As an example, you can use this API to lookup an IP Address.

    >>> ipaddr = repo.get_ipblock_by_address('128.223.61.69')

Lets assume we want to determine who all may depend on this IP Address.
We'll see if we can discover useful information from the `used_by` field of this IP Address, or its Subnet...

    >>> ipaddr.used_by
    None
    >>> subnet = ipaddr.get_parent()
    >>> subnet.used_by
    'Network & Telecom Services'
    >>> ip_container = subnet.get_parent()
    >>> ip_container.used_by
    'University of Oregon (3582)'

This demonstrates programatic read-access to the Address Space in NetDot.

> ℹ Similar to `get_parent`, you'll notice you can `get_children` if you would like to!

# Primary Interface: `netdot.Repository`

> `netdot.Repository` is the type of object that gets returned from the `netdot.connect()` function.

The `netdot.Repository` class is the primary interface of this package.
It provides many methods to download data from NetDot (e.g. get_site, get_device, get_devices_by_site, get_all_sites...)

> ⚠ TODO: ... Work in progres!!
> 
> There are many NetDot entities yet to be added to this `netdot.Repository` interface!
>
> In the meantime, consider using the Legacy Interface for anything not found here.

# Legacy Interface: `netdot.Client.Connect()`

The legacy `netdot.Client.Connect()` class is still available at this time!
This can be used to access all aspects of the NetDot RESTful API.

See the legacy example code that was provided with this Connect class:

> ⚠ This example has been untested for a very long time!

    #!/usr/bin/env python2.7
    import sys
    import os
    import netdot

    uname = 'my_user'
    pword = 'my_pass'
    server = "https://netdot.localdomain/netdot"
    debug = 1

    dot = netdot.Client.Connect(uname, pword, server, [debug])

    # Direct GET/POST/DELETE calls
    r = dot.get('/host?name=my-server-name')
    r = dot.post('/host', host)

    name = dot.get_host_by_name('foo')
    cname = dot.add_cname_to_record('foo','bar.foo.example.com')
    ipid = dot.get_host_by_ipid('11111')
    rrid = dot.get_host_by_rrid('11111')

    ipblock =  dot.get_ipblock("184.171.96.0/24")
    user = dot.get_person_by_username('mary')
    user_id = dot.get_person_by_id('111')

    host = {
        'name':'my-server', 
        'subnet':'192.168.1.0/24', 
        'ethernet':'XX:XX:XX:XX:XX:XX',
        'info':'My Server'
    }
    r = dot.create_host(host)

    print r

# Appendix: Using `help()` in interpreter

When in the interpreter session, it can be very useful to run `help(netdot.Repository)` to learn more about the Repository's capabilities.

> ℹ If you've already established a connection via `repo = netdot.connect()`, then you can run `help(repo)` instead!

    >>> help(netdot.Repository)
    class Repository(builtins.object)
    |  Work with Netdot API using Python objects.
    |  
    |  Methods defined here:
    |  
    |  __init__(self, netdot_url, user, password, parallelization_factor=11, **kwargs)
    |      Initialize self.  See help(type(self)) for accurate signature.
    |  
    |  get_asset(repo:netdot_sites_manager.netdot.repository.Repository, id:int) -> ~T
    |      Get info about a Asset from Netdot.
    |      
    |      Args: ... trimmed for brevity...