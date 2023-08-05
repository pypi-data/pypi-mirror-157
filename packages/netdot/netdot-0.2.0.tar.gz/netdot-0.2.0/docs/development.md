This document discusses setting up local development for this project on your own personal Linux box. 

> We use [Python Hatch](https://hatch.pypa.io/latest/) for this project.

## Prerequisites

### Python 3.6

Today, UO is still using Python 3.6.
So, install Python 3.6, along with distutils.

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install python3.6 python3.6-distutils python3.6-venv

It is wise to update pip at this time.

    python3.6 -m pip install --upgrade pip

### Hatch

We use Hatch to manage our development environment (and build process).

> What is Hatch? "Hatch is a modern, extensible Python project manager."

You can easily [install Hatch](https://hatch.pypa.io/latest/install/) using pip.

    pip install hatch

## Getting Started

Once you have [installed Hatch](#hatch), we can jump right into our development environment using the following command.

    hatch --env dev shell

At this point, running `pip freeze` should reveal that all dependencies are installed for you!

### Any Issues?

If there are issues during environment set up, it is generally best to start over from scratch.
This can be simply done by running `hatch env prune`.

> ℹ This will remove all Hatch-managed environments and restart fresh.
> 
> ℹ You will have to `exit` from any/all Hatch shells that you may have opened -- otherwise the prune will fail.


## Automated Testing

pytest is used to automatically test this project.
All tests are contained in the "tests" directory.

To run all the automated tests for this project, you can simply, "`run` the `test` script provided by our Hatch `dev` environment":  `hatch run dev:test`

    hatch run dev:test
    ===================== test session starts =====================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-1.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    ... omitted for brevity...
