from dataclasses import dataclass, asdict
from numbers import Number
from typing import Dict, Optional, Tuple, Union
import logging

import numpy as np

from jijmodeling.problem import Problem

from jijzept.response import DimodResponse
from jijzept.client import JijZeptClient
from jijzept.entity.schema import SolverType
from jijzept.sampler.jijmodel_post import JijModelingInterface


@dataclass
class JijLeapHybridCQMParameters:
    """Manage Parameters for using Leap Hybrid CQM Sampler
    Attributes:
        time_limit (Optional[Union[int, float]]): the maximum run time, in seconds, the solver is allowed to work on the given problem. Must be at least the minimum required for the problem, which is calculated and set by default. It is deprecated to set this up due to high credit consumption.
        label (str): The problem label given to the dimod.SampelSet instance returned by the JijLeapHybridCQMSampler.
        Defaults to None.
    """

    time_limit: Optional[Union[int, float]] = None
    label: Optional[str] = None


class JijLeapHybridCQMSampler(JijModelingInterface):
    jijmodeling_solver_type = SolverType(
        queue_name="thirdpartysolver", solver="DwaveLeap"
    )

    def __init__(
        self,
        token: Optional[str] = None,
        url: Optional[Union[str, dict]] = None,
        proxy: Optional[str] = None,
        config: Optional[str] = None,
        config_env: str = "default",
        token_leap: Optional[str] = None,
        url_leap: Optional[str] = None,
    ) -> None:
        """Sets token and url.

        Args:
            token (str): Token string for JijZept.
            url (Union[str, dict]): API URL for JijZept.
            config (str): Config file path for JijZept.
            token_leap (str): Token string for Dwave Leap.
            url_leap (str): API URL for Dwave Leap.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)
        self.token_leap = token_leap
        self.url_leap = url_leap

    def sample_model(
        self,
        model: Problem,
        feed_dict: Dict[str, Union[Number, list, np.ndarray]],
        fixed_variables: Dict[str, Dict[Tuple[int, ...], Union[int, float]]] = {},
        parameters: Optional[JijLeapHybridCQMParameters] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
        **kwargs,
    ) -> DimodResponse:
        """Converts the given problem to dimod.ConstrainedQuadraticModel and runs Dwave's LeapHybridCQMSampler.
        Note here that the supported type of decision variables is only Binary when using LeapHybridCQMSolver from Jijzept.

        Args:
            problem (Problem): Optimization problem of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): variables to fix.
            parameters (JijLeapHybridCQMParameters): Parameters used in Dwave Leap Hybrid CQMSampler. If `None`, the default value of the JijDA3SolverParameters will be set.
            timeout (int): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool): Synchronous mode.
            queue_name (str): Queue name.
            kwargs: Dwave Leap parameters using **kwags. If both `**kwargs` and `parameters` are exist, the value of `**kwargs` takes precedence.

        Returns:
            dimod.Sampleset: Stores samples and other information.

        Examples:

        ```python
        import jijmodeling as jm
        from jijzept import JijLeapHybridCQMSampler, JijLeapHybridCQMParameters

        w = jm.Placeholder("w", dim=1)
        num_items = jm.Placeholder("num_items")
        c = jm.Placeholder("c")
        y = jm.Binary("y", shape=(num_items,))
        x = jm.Binary("x", shape=(num_items, num_items))
        i = jm.Element("i", num_items)
        j = jm.Element("j", num_items)
        problem = jm.Problem("bin_packing")
        problem += y[:]
        problem += jm.Constraint("onehot_constraint", jm.Sum(j, x[i, j]) - 1 == 0, forall=i)
        problem += jm.Constraint("knapsack_constraint", jm.Sum(i, w[i] * x[i, j]) - y[j] * c <= 0, forall=j)
        feed_dict = {"num_items": 2, "w": [9, 1], "c": 10}

        sampler = JijLeapHybridCQMSampler(config="XX", token_leap="XX")
        parameters = JijLeapHybridCQMParameters(label="bin_packing")
        sampleset = sampler.sample_model(
            problem, feed_dict, parameters=parameters
        )
        ```

        """

        if parameters is None:
            parameters = JijLeapHybridCQMParameters()

        parameters = asdict(parameters)
        if kwargs:
            logging.warning("Setting Parameters using **kwargs is not recommended.")
            parameters.update(**kwargs)

        return super().sample_model(
            token=self.token_leap,
            url=self.url_leap,
            model=model,
            feed_dict=feed_dict,
            multipliers={},
            fixed_variables=fixed_variables,
            parameters=parameters,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )
