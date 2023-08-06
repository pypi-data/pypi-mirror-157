from __future__ import annotations
from dataclasses import dataclass, asdict
from numbers import Number
from typing import Optional, Union
import logging

import numpy as np

from jijzept.response import DimodResponse
from jijmodeling import Problem
from jijzept.client import JijZeptClient
from jijzept.entity.schema import SolverType
from jijzept.sampler.jijmodel_post import JijModelingInterface


@dataclass
class JijFixstarsAmplifyParameters:
    """Manage Parameters for using Fixstars Amplify
    Attributes:
        amplify_timeout (int): Set the timeout in milliseconds. Defaults to 1000.
        num_unit_steps (int): The number of the unit steps for annealing. Defaults to 10.
        num_outputs (int): The number of outputs for spin arrays and energy values. Assumed 1 if no value is set. If set to 0, all spin arrays and energy values are output. Defaults to 1.
        filter_solution (bool): Boolean value that specifies whether the solutions are filtered based on given constraints. Default to `False`.
        penalty_calibration (bool): Boolean value that determines whether to automatically adjust the coefficients of the penalty functions of constraint objects. Defaults to `False`.
    """

    amplify_timeout: int = 1000
    num_unit_steps: int = 10
    num_outputs: int = 1
    filter_solution: bool = False
    penalty_calibration: bool = False


class JijFixstarsAmplifySampler(JijModelingInterface):
    jijmodeling_solver_type: SolverType = SolverType(
        queue_name="thirdpartysolver", solver="FixstarsAmplify"
    )

    def __init__(
        self,
        token: Optional[str] = None,
        url: Union[str, dict] = None,
        proxy: Optional[str] = None,
        config: Optional[str] = None,
        config_env: str = "default",
        fixstars_token: str = "",
        fixstars_url: str = "",
    ) -> None:
        """Sets Jijzept token and url and fixstars amplify token and url.

        Args:
            token (Optional[str]): Token string.
            url (Union[str, dict]): API URL.
            proxy (Optional[str]) Proxy URL.
            config (Optional[str]): Config file path for JijZept.
            config_env (str): config env.
            fixstars_token (str): Token string for Fixstars Amplify.
            fixstars_url (str): Url string for Fixstars Ampplify.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)
        self.fixstars_token = fixstars_token
        self.fixstars_url = fixstars_url

    def sample_model(
        self,
        model: Problem,
        feed_dict: dict[str, Union[Number, list, np.ndarray]],
        multipliers: dict[str, Number] = {},
        fixed_variables: dict[str, dict[tuple[int, ...], Number]] = {},
        parameters: Optional[JijFixstarsAmplifyParameters] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
        **kwargs,
    ) -> DimodResponse:
        """Converts the given problem to amplify.BinaryQuadraticModel and run Fixstars Amplify Solver.
        Note here that the supported type of decision variables is only Binary when using Fixstars Ampplify Solver from Jijzept.

        Args:
            model (Problem): Mathematical expression of JijModeling.
            feed_dict (dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (dict[str, Number]): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (dict[str, dict[tuple[int, ...], Number]]): Dictionary of variables to fix.
            parameters (Optional[JijFixstarsAmplifyParameters]): Parameters used in Fixstars Amplify. If `None`, the default value of the JijFixstarsAmplifyParameters will be set.
            timeout (Optional[int]): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool): Synchronous mode.
            queue_name (Optional[str]): Queue name.

        Returns:
            dimod.Sampleset: Stores samples and other information.

        Examples:

        ```python
        import jijmodeling as jm
        from jijzept import JijFixstarsAmplifySampler, JijFixstarsAmplifyParameters


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
        multipliers = {"onehot_constraint": 11, "knapsack_constraint": 22}

        sampler = JijFixstarsAmplifySampler(config="xx", fixstars_token="oo")
        parameters = JijFixstarsAmplifyParameters(amplify_timeout=1000, num_unit_steps=10, num_outputs=1, filter_solution=False, penalty_calibration=False)
        sampleset = sampler.sample_model(
            problem, feed_dict, multipliers, parameters=parameters
        )
        ```
        """
        if parameters is None:
            parameters = JijFixstarsAmplifyParameters()

        parameters = asdict(parameters)
        if kwargs:
            logging.warning("Setting Parameters using **kwargs is not recommended.")
            parameters.update(**kwargs)

        parameters["timeout"] = parameters.pop("amplify_timeout")
        return super().sample_model(
            model=model,
            feed_dict=feed_dict,
            multipliers=multipliers,
            fixed_variables=fixed_variables,
            search=False,
            num_search=15,
            algorithm=None,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
            token=self.fixstars_token,
            url=self.fixstars_url,
            parameters=parameters,
        )
