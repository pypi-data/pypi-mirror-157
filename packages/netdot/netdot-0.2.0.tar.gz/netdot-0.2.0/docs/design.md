This document is a place to discuss design decisions that support this Python NetDot API wrapper.

> ⚠ Disclaimer: From 0.2.0 onward, this API wrapper may not support the [de facto Open Source version of NetDot (GitHub)](https://github.com/cvicente/Netdot).
>
> From 0.2.0 onward, this API wrapper has been built to support [UO's NetDot implementation (access restricted)](https://nsdb.uoregon.edu).

# API Wrapper Layers

We consider this API wrapper to have a layered design, portrayed in the table below.

| Layer | Title       | Description                                                                  |
| ----- | ----------- | ---------------------------------------------------------------------------- |
| 2     | Repository  | Work with well-typed NetDot [Data classes](#data-classes-netdotdataclasses). |
| 1     | Client      | Work with Python dictionaries.                                               |
| 0     | RESTful API | Work directly with the XML bytes provided by HTTP.                           |

These are software layers, which implies dependencies between layers occur only in the following ways:

* Client: depends on RESTful API.
* Repository: depends on Client.

# Repository and Data Classes

The primary interface of this API wrapper is the `Repository` class.
That Repository will operate based on well-typed Data classes -- implemented using [Python `dataclasses`](https://docs.python.org/3/library/dataclasses.html)

## Repository class: `netdot.Repository`

Being the primary interface of this API wrapper, we have the following goals for our `Repository` class:

* use **consistent naming** for methods and attributes*,
* provide complete and accurate **docstrings** for every method*,
* handle API errors when possible, and emit a useful WARNING log message, and
* when an unhandleable errors rise, use the semantically-appropriate error, e.g. ValueError, TypeError, NetdotError. 

> *: We have actually fully encoded the first two details using some [runtime generated code (discussed below)](#repository-generate-functions).

### Repository class conventions

Below are the naming conventions 

| Naming Convention        | Example Method                 | Discussion                                                                                                |
| ------------------------ | ------------------------------ | --------------------------------------------------------------------------------------------------------- |
| `get_<D>(id)`            | `get_site(14)`                 | Get a site by its ID.                                                                                     |
| `get_all_<D>s()`         | `get_all_devices()`            | Get ALL devices from NetDot.                                                                              |
| `get_<A>s_by_<B>(other)` | `get_devices_by_site(my_site)` | Get all of devices that have site 'my_site' associated to it. (`A` has a foreign key relationship to `B`) |

> TODO: `get_<A>s_by_<B>_xlink` is currently unavailable.
>
> | `get_<A>s_by_<B>_xlink(other_id)` | `get_devices_by_site_xlink(14)` | Same, but instead based on id.                                                                            |

> The symbols `D`, `A`, and `B` used above could be ANY of the dataclasses from the `netdot.dataclasses` package.

## Data Classes: `netdot.dataclasses`


> ⚠ TODO: ... Work in progres!!
> 
> There are many dataclasses to be added, e.g. we've [converted netdot schema to python](assets/converted_netdot_schema.py), but we need to actually finish implementing and testing all of these.
>
> Feel free to make a pull request with a [new Data class in `netdot.dataclass`](#appendix-create-a-subclass-of-netdotapidataclass)!

The `netdot.dataclasses` package contains all the Python dataclasses that represent NetDot objects.
These dataclasses are roughly based on the [UO NSDB NetDot's Relationships (access restricted)](https://is-nsdb.uoregon.edu/help/database-rels.html).
In addition, we did need to experiment with the REST API directly to determine what fields are actually being returned.

### Data Class Conventions

* All data classes are subclasses of the `NetdotAPIDataclass` base class.
* These classes have fields with names matching what is returned from the RESTful API.
  *  `_xlink` suffix if they are related to another Data class.

> ⚠ TODO: Document the field/method naming conventions, similar to Repository class conventions.  

# Generated code

We realized when implementing our various [naming conventions](#netdotdataclass-generate-functions-dataclass-coding-conventions) that the code had become very generic.
In fact, we were copy-pasteing a LOT of code between Data classes and Repository methods.
As a result, some methods and field names had typoes -- it was transforming into a monsterous code base!

So, rather than spending time copy-pasting all the code, we decided to implement all the generic logic we could in 'generate functions.'

> ℹ Using a generated code solution automatically ensures that our code follow conventions *perfectly, every time, (without any typoes)*.

## Repository 'generate functions'

The Repository class's  are codified by the '`generate_...`' functions in the `netdot.repository` module.

> TODO: discuss each of the `generate_...` functions.

> ✅ In addition to enforcing method naming conventions, the '`generate_...`' functions will also *generate the docstrings for every method*!


### `netdot.dataclass` 'generate functions' Dataclass Coding Conventions

These are the conventions we use to try and make this library most useful to the most people.

> Most of the conventions we had originally documented here are acutally encoded in NetdotAPIDataclass's 'generate' classmethods now -- generating Python code rules! 🤘

> Using consistent conventions makes this API wrapper MUCH easier to interoperate with.

* Follow PEP 8 for class naming.
* These are mutable dataclasses.
    > TODO: should we make them immutable? (and just return new copies from `with_` methods).
    > Pro: Enables using them with Set() data collection type.

> TODO: discuss each of the `generate_...` functions.

# Client

The Client is a simple API wrapper that enables working with [NetDot's RESTful API](api.md), but as Python dictionaries.

From the high level perspective, this layer converts 'NetDot XML data' into 'Python dictionaries' (for HTTP GET requests).
Additionally, this layer converts from dictionaries to 'NetDot XML data' (for HTTP POST requests)!

> ℹ The Client is implemented using a [`requests` HTTP Sesssion (`requests` docs)](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects).

> TODO: Discuss Client_v1 history... or cleanup Client_v1 entirely...

# Appendix: Create a Subclass of NetdotAPIDataclass

To support maximum interoperability, it is best if all our dataclasses extend from NetdotAPIDataclass (as well as CSVDataclass to ease exporting data as CSVs for data-pipeline integrations).

Here is the boilerplate code you'd start to define the `Device` dataclass in "dataclasses/device.py". 

    from dataclasses import dataclass
    from netdot_sites_manager.csv_util import CSVDataclass
    from netdot_sites_manager.netdot.dataclasses.base import NetdotAPIDataclass

    @dataclass()
    class Device(NetdotAPIDataclass, CSVDataclass):
        NETDOT_MENU_URL_PATH = 'management' # [1] Choose from [management, contacts, cable_plant, advanced, reports, export, help]
        NETDOT_TABLE_NAME = 'Device' # [2] Appropriate capitalization pulled from Netdot [1]
        
    
> \[1\]: This value is used to recreate URLs for the object, so we can have a generic `web_url()` method.
>
> \[2\]: Appropriate capitalization can be inferred by loading NetDot then looking at "Advanced -> Browse Tables".
> The table name will be printed in the top right corner, e.g. for accessright table we see: "AccessRight ( 3506 records)"
