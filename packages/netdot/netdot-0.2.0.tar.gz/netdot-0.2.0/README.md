# Netdot Client for Python

A python wrapper for NetDot REST API.

[![PyPI version](https://badge.fury.io/py/netdot.svg)](https://badge.fury.io/py/netdot)

See `examples/example.py` in the project's git repository for details on how to use netdot.

> TODO: Write some real documentation on how to use this "`netdot` python client".


# For Developers

|                           | Notes/Description                              | 
|---------------------------|------------------------------------------------|
| **Primary Contact**       | rleonar7@uoregon.edu |
| **Backup Contact**        | nts-neteng@network-services.uoregon.edu |
| **Git Repository**        | [git.uoregon.edu/../netdot-python-client (authorization required)](https://git.uoregon.edu/projects/ISN/repos/netdot-python-client)
| **Jenkins CICD Pipeline**      | [netdot-python-client-CICD (authorization required)](https://is-nts-jenkins.uoregon.edu/job/netdot-python-client-CICD/)

## Using `netdot` from source code

This is simple to do using the `pip --editable` flag:

    # run this from the directory where setup.py lives
    pip install --editable .

> E.g., Try adding code that raises exception from the `Client.py::_login()` method and run `pytest` again to see proof.

> NOTE: Now, if you need to update `requirements.txt`, it is a good idea to ignore the 'netdot' package, e.g. via `grep --invert-match`:
>
>     pip freeze | grep --invert-match "netdot" > requirements.txt`


## Deploying a new version of `netdot` to PyPI

There is a [Jenkins pipeline (authorization required)](https://is-nts-jenkins.uoregon.edu/job/netdot-python-client-CICD/) that defines the Continuous Integration and Deployment (CICD) solution for this project (see [Jenkinsfile](Jenkinsfile) and the [Jenkinsfile Readme](README-Jenkinsfile.md)).
For this project, 'deployment' is essentially 'deploying a new version to PyPI.'

The deployment process is directly-tied to the BitBucket Pull Request process for the [Netdot Python Client repository (authorization required)](https://git.uoregon.edu/projects/ISN/repos/netdot-python-client).
When a Pull Request for `netdot-python-client` repository merges, Jenkins will (attempt to) automatically deploy that latest version to the [netdot PyPI project](https://pypi.org/project/netdot/).

1. Create a git feature branch with your new feature/changes.
2. Update the `netdot/__init__.py` `__version__` variable per [semantic versioning](https://semver.org/)
    - (MAJOR) If you add any 'required arguments' to an **existing interface**, you must increment the MAJOR version. 
    - (MINOR) If you add only 'optional arguments' to an existing interface, increment the MINOR version.
        - e.g. adding a new `--optional-argument`
        - e.g. adding a new positional argument option, `{get}` -> `{get, post}`
    - (PATCH) If you don't change the interface in any way, increment the PATCH version.
3. Create a pull request in the [Netdot Python Client repo (authorization required)](https://git.uoregon.edu/projects/ISN/repos/buildtools/browse).
4. Get `approval` (with help from a colleague) and then `merge` the pull request.
5. Patiently watch the [ntsbuildtools PyPI project](https://pypi.org/project/netdot/) until your new release appears!


## Automated Tests

This project contains integration/unit tests that are run via `pytest`.

Before the tests can execute, the `netdot` package needs to be made available via `pip install --editable .`, as discussed above.

    $ pip install --editable .
    $ pytest
    > ====== test session starts ======
    > ... omitted for brevity...
    > ====== 2 passed in 1.04s ========


## References

* ["Building and Testing an API Wrapper in Python"](https://semaphoreci.com/community/tutorials/building-and-testing-an-api-wrapper-in-python)

* ["Controlling [Jenkinsfile] flow with Stage, Lock, and ***Milestone***"](https://www.jenkins.io/blog/2016/10/16/stage-lock-milestone/)
