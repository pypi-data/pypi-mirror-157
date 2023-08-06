import datetime as dt
import json
import os
import sys
from contextlib import contextmanager
from typing import Any, Dict

from . import __version__


class Step:
    """Class that represents a processing step.
    """

    def __init__(self, skipped: bool = False, **kwargs):
        self.start_time = None
        self.end_time = None
        self.elapsed = None
        self.skipped = skipped
        self.extra = kwargs

    def start(self):
        """Signal the step has started.
        """
        self.start_time = dt.datetime.now()

    def end(self):
        """Signal the step has ended.
        """
        self.end_time = dt.datetime.now()
        self.elapsed = (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert this step to a dictionary.
        """
        return {
            'start_time': None if self.skipped else self.start_time.isoformat(),
            'end_time': None if self.skipped else self.end_time.isoformat(),
            'elapsed': None if self.skipped else self.elapsed,
            'skipped': self.skipped,
            **self.extra
        }


class Stats:
    """Class used to collect run statistics.
    """

    def __init__(self):
        self.workdir = os.path.abspath(os.getcwd())
        self.call = None

        self.start_time = None
        self.end_time = None
        self.elapsed = None

        self.steps = {}
        self.step_order = []

        self.version = __version__

    def start(self):
        """Start collecting statistics.

        Sets start time, the command line call.
        """
        self.start_time = dt.datetime.now()
        self.call = ' '.join(sys.argv)

    def end(self):
        """End collecting statistics.
        """
        self.end_time = dt.datetime.now()
        self.elapsed = (self.end_time - self.start_time).total_seconds()

    @contextmanager
    def step(self, key: str, skipped: bool = False, **kwargs):
        """Register a processing step.

        Any additional keyword arguments are passed to the constructor of `Step`.
        """
        step = Step(skipped=skipped, **kwargs)
        self.steps[key] = step
        self.step_order.append(key)
        if not skipped:
            step.start()
        yield
        if not skipped:
            step.end()

    def save(self, path: str) -> str:
        """Save statistics as JSON to path.
        """
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        return path

    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary, so that it is easily parsed
        by the report-rendering functions.
        """
        return {
            'version': self.version,
            'workdir': self.workdir,
            'call': self.call,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'elapsed': self.elapsed,
        }
