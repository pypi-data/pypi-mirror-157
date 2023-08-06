from __future__ import annotations
from collections.abc import Iterable

import datetime as dt
import sys
import traceback
from abc import ABC, abstractmethod
from multiprocessing.context import ForkProcess
from typing import Union, List, Any, Dict, Optional, Callable

import numpy as np
import pandas as pd


class BaseResult:
    """Base class for the internal representation of experimental observations and export to a dictionary of values.

    Each observation will be a collection of named values arising from a single run of an experiment.

    The basic attributes of start/end times, error states, and argument values are handled in this class. Subclasses
    must call super().__init__ in order to initialise these values properly.

    """

    def __init__(self):
        """Base constructor of the BaseResult class. Please call this in the constructor of your subclass.

        """
        self.execution_id = None
        self.start = pd.NaT
        self.end = pd.NaT
        self.errored = False
        self.force_stopped = False
        self.error_message = None
        self.args = None

    def to_dict(self) -> Dict[str, Any]:
        """Export the result values to a dictionary.

        Returns:
            Dict[str, Any]: dictionary of values derived from this result.
        """
        d = {}
        for k, v in self.__dict__.items():
            if k != 'args':
                d[k] = v
            else:
                for i, a in enumerate(v):
                    d[f'arg{i}'] = a
        return d


class BaseExperiment(ForkProcess, ABC):
    """Base class for experiments.

    This class encapsulates the core logic of running an experiment and logging results in a way that allows for
    concurrent experiments running in threads and for
    """

    def __init__(
            self,
            build_fn,
            *ranges: Union[List[Union[int, float]], Union[int, float]],
            **kwargs: Any
    ):
        """Constructor for the experiment base class.

        Args:
            *ranges (Union[List[Union[int, float]], Union[int, float]]): single constant values or ranges to randomly
            sample for the experiment.

        Keyword Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.
        """

        self.build_fn = build_fn
        self._ranges = ranges

        self._force_stop = False

        self._seed = kwargs.get('seed', np.random.randint(1989))

        # observation values
        self._return = self._init_result()
        self.queue = None
        ForkProcess.__init__(self)

    def __str__(self):
        ranges_str = ', '.join(f'arg{i}: {r}' for i, r in enumerate(self._ranges))
        return f"Domain: {ranges_str}\n  Seed: {self._seed}"

    def _attach_queue(self, queue):
        self.queue = queue

    @abstractmethod
    def copy(self, seed: int) -> BaseExperiment:
        """Make a copy of the experiment so multiple copies of the experiment can be run in parallel.

        Args:
            seed (int): random seed to set in numpy when selecting experiment arg values.

        Returns:
            BaseExperiment: an independent copy of this experiment.

        """
        pass

    def _generate_params(self) -> List[Union[int, float]]:

        np.random.seed(self._seed)
        args = []
        for rng in self._ranges:
            # Is it a constant value? If so, just add it to the args.
            if not hasattr(rng, '__len__') or isinstance(rng, str):
                args.append(rng)
            # Is it a range? This is either a list or tuple of length 2
            elif isinstance(rng, (list, tuple)) and len(rng) == 2:
                arg = int(np.random.randint(rng[0], rng[1] + 1))
                args.append(arg)
            # Is it a set of discrete elements? If so pick one at random
            elif isinstance(rng, set):
                args.append(np.random.choice(rng))
            # Otherwise error
            else:
                raise ValueError(f'Received a bad parameter range def: {rng}. '
                                 f'Should be a constant val, list of size 2 or a set')

        return args

    @abstractmethod
    def _init_result(self) -> BaseResult:
        """Initialise a result object for this experiment.

        Notes:
            If you're logging more stuff please subclass ExperimentResult and initialise it in this
            method's implementation.

        Returns:
            BaseResult: the result object filled with initial values.

        """
        return BaseResult()

    def run(self) -> None:
        """Run the experiment thread.

        """
        args = self._generate_params()

        self._return.args = args
        self._return.start = dt.datetime.utcnow()

        # noinspection PyBroadException
        # ^ That's sort of the point...
        try:
            runnable = self.build_fn(*args)
            # Run the experiment's core logic
            # You should log other aspects of the experiment inside this method's implementation
            self._job(runnable)
            self._return.end = dt.datetime.utcnow()
            self.queue.put(self._return.to_dict())

        except Exception:
            # If there's an exception, catch it and log its content.
            self._return.end = dt.datetime.utcnow()
            self._return.errored = True
            self._return.error_message = ''.join(traceback.format_exception(*sys.exc_info()))
            self.queue.put(self._return.to_dict())

    @abstractmethod
    def _job(self, runnable) -> None:
        """Internal method that runs the experiment. Can contain anything you want to run and log to the result object
        at self._return.

        Args:
            runnable (Any): the function or query etc to run

        """
        # modify the _return attribute
        pass

    def join(self, timeout: Optional[float] = None, force: Optional[bool] = False) -> None:
        """Wait until the experiment (process) terminates. This can be forced by passing in force=True.

        Args:
            timeout (Optional[int]): floating point number specifying a timeout for the experiment in seconds.
            force (Optional[bool]): whether to force

        """
        self._force_stop = force
        self._return.force_stopped = force
        ForkProcess.join(self, timeout)

    def should_stop(self):
        """This method can be used as a callback to check for cancellation inside the _job method and whatever it
        might call.

        Returns:
            bool: whether to force stop the experiment.
        """
        return self._force_stop


class BaseMeasurementSet:
    """Base class for standard measurement sets. Standard measurement sets are the set of standard measurements that
    characterise the performance of a given Finbourne application.

    Standard measurement sets should have a set of methods ending with _measurement for each individual standard
    measurement which output a Convener instance or a tuple of Convener instances.

    Each measurement method must be documented with a docstring.
    """

    def __init__(self, work_dir):
        """Base constructor of the measurement set

        Args:
            work_dir: the working directory to use in the conveners of the standard measurement set.

        """

        self.work_dir = work_dir
        self._validate()

    def get_measurements(self) -> Dict[str, Callable]:
        """Get a dictionary of all the measurement methods of this class.

        Returns:
            Dict[str, Callable]: the dictionary of measurement names and methods.

        """
        return {m: getattr(self, m) for m in dir(self) if m.endswith('_measurement')}

    def list_conveners(self, **kwargs) -> List['Convener']:
        """List all the conveners to run in this standard measurement set.

        Returns:
            List[Convener]: the list of conveners.

        """

        def _flatten(it):
            for x in it:
                if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
                    yield from _flatten(x)
                else:
                    yield x

        return list(_flatten(map(lambda x: x(**kwargs), self.get_measurements().values())))

    def _validate(self):
        d = self.get_measurements()
        not_documented = []
        for k, v in d.items():
            doc = v.__doc__
            if doc is None:
                not_documented.append(k)

        if len(not_documented) > 0:
            names = '\n  '.join(not_documented)
            raise ValueError(
                "There are measurements that are not documented with a docstring. "
                f"Please add one to the following:\n  {names}"
            )

    def teardown(self):
        pass

    def setup(self):
        pass
