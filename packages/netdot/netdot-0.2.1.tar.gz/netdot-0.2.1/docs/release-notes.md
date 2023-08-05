This project follows [Semantic Versioning](https://semver.org/).

> Notice: Major version zero (0.y.z) is for initial development. Anything MAY change at any time. 
> This public API should **not** be considered stable.

> ⚠ Disclaimer: From 0.2.0 onward, this API wrapper does not ensure support for the [de facto Open Source version of NetDot (GitHub)](https://github.com/cvicente/Netdot).

## 0.2.1

* Fix for REGRESSION: The `netdot.Client.Connection` class is missing!
  * Re-added `Connection` directly to client.py for now. 
  * Aliased `netdot.client` module to also be available as it was formerly named, `netdot.Client` (pep8 suggests lowercase module names instead of CamelCase).
    * Using `__all__` in "netdot/\_\_init\_\_.py" 


## 0.2.0 

> 🐛 REGRESSION: The `netdot.Client.Connection` class is MISSING!

> ⚠ We have not ensured support for the [de facto Open Source version of NetDot (GitHub)](https://github.com/cvicente/Netdot).

* Introducing a new layer of abstraction -- a Repository and many Python dataclasses.
    * See more info in the [User Guide](user-guide.md)
* Provide technical documentation in "docs/" directory (following NTS's standards).
    * See [the README.md in the "docs/" directory](README.md) for an overview.

## 0.1.0

* Provide Python Netdot Client, as originally authored by Francisco Gray.
