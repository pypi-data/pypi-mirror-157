"""Default values to be used throughout this package.
"""
import dataclasses
import textwrap
from datetime import datetime


def empty_list():
    """Dataclass field definition. 

    Shorthand for 'default to an empty list' for dataclass attribute(s).

    Returns:
        dataclasses.field: A dataclass field that will default to empty list.
    """
    return dataclasses.field(default_factory=list)


# 11 seems about optimal for is-nsdb.uoregon.edu today (May 1, 2022)
PARALLELIZATION_FACTOR = 11

def managed_by_jenkins_comment(message=''):
    """A standard string indicating 'Created/Updated by automation...'

    > Useful in place of a Description/Comment/Info field.

    Returns:
        str: A discussion of this automation tool, as well as the current time.
    """
    timestamp_str = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S %Z')
    jenkins_job_url = 'https://is-nts-jenkins.uoregon.edu/job/Netdot%20Sync%20with%20GIS/'
    return textwrap.dedent(
        f'''⚠ NOTICE: Managed by "NetDot Sync with GIS" NTS Jenkins Pipeline.
                {jenkins_job_url}
            {message}
            Last Created/Updated at {timestamp_str}.
            '''
    )
