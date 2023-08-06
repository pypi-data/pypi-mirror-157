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
from jijzept.response.jmresponse import JijModelingResponse
from jijzept.sampler.jijmodel_post import JijModelingInterface


@dataclass
class JijDA3SolverParameters:
    """Manage Parameters for using Digital Annealer v3

    Parameters:
        time_limit_sec (int): Set the timeout in seconds in the range 1 ~ 1800.
        target_energy (Optional[float]): Set the target energy value. The calculation is terminated when the minimum energy savings reaches the target energy.
        num_run (int): Set the number of parallel trial iterations in the range 1 ~ 16.
        num_group (int): Set the number of groups of parallel trials in the range 1 ~ 16.
        num_output_solution (int): Set the number of output solutions for each parallel trial group in the range 1 ~ 1024.
        gs_level (int): Set the level of global search. The higher this value, the longer the constraint utilization search will search in the range 0 ~ 100.
        If set the 1way 1hot or 2way 1hot, it is recommended that 0 be set for gs_level.
        gs_cutoff (int): Set the convergence decision level in the constraint utilization search of the solver in the range 0 ~ 1000000. If `0`, convergence judgement is off.
        penalty_auto_mode (int): Set the coefficient adjustment mode for the constaint term.
        If `0`, fixed to the value setin `penlaty_coef`. If `1`, the value set in `penalty_coef` is used as the initial value and adjusted automatically.
        penalty_coef (int): Set the coefficients of the constraint term.
        penalty_inc_rate (int): Set parameters for automatic adjustment of constriant term.
        max_penalty_coef (int): Set the maximum value of the constraint term coefficient in the global search. If no maximum value is specified, set to 0.
        penalty_strength (float): Set the coefficient when the constraint that appears when converting HUBO to QUBO is treated as a penalty term.
    """

    time_limit_sec: int = 10
    target_energy: Optional[float] = None
    num_run: int = 16
    num_group: int = 1
    num_output_solution: int = 5
    gs_level: int = 5
    gs_cutoff: int = 8000
    penalty_auto_mode: int = 1
    penalty_coef: int = 1
    penalty_inc_rate: int = 150
    max_penalty_coef: int = 0
    penalty_strength: float = 5.0


# TODO: add integration test
class JijDA3Sampler(JijModelingInterface):
    jijmodeling_solver_type: SolverType = SolverType(
        # queue_name="testsolver",
        queue_name="thirdpartysolver",
        solver="DigitalAnnealer",
    )

    def __init__(
        self,
        token: Optional[str] = None,
        url: Union[str, dict] = None,
        proxy: Optional[str] = None,
        config: Optional[str] = None,
        config_env: str = "default",
        da3_token: str = "",
        # da3_url: str = "",
        da3_url: str = "https://api.aispf.global.fujitsu.com/da",
        # da3_url: Optional[str] = None,
    ) -> None:
        """Sets Jijzept token and url and Digital Annealer v3 token and url.

        Args:
            token (Optional[str]): Token string.
            url (Optional[Union[str, dict]]): API URL.
            proxy (Optional[str]): Proxy URL.
            config (Optional[str]): Config file path for JijZept.
            config_env (str): config env.
            da3_token (str): Token string for Degital Annealer 3.
            da3_url (Optional[str]): API Url string for Degital Annealer 3.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)
        self.da3_token = da3_token
        self.da3_url = da3_url

    def sample_model(
        self,
        model: Problem,
        feed_dict: dict[str, Union[Number, list, np.ndarray]],
        multipliers: dict[str, Number] = {},
        fixed_variables: dict[str, dict[tuple[int, ...], Number]] = {},
        parameters: Optional[JijDA3SolverParameters] = None,
        search: bool = False,
        num_search: int = 15,
        algorithm: Optional[str] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
        jm_sampleset: bool = False,
        **kwargs,
    ) -> Union[DimodResponse, JijModelingResponse]:
        """Sample using JijModeling by means of Digital Annealer v3.

        Args:
            model (Problem): Mathematical expression of JijModeling.
            feed_dict (dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (dict[str, Number]): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (dict[str, dict[tuple[int, ...], Number]]): Dictionary of variables to fix.
            parameters (Optional[JijDA3SolverParameters]): Parameters used in Ditital Annealer3. If `None`, the default value of the JijDA3SolverParameters will be set.
            search (bool): If `True` parameter search is enabled.
            num_search (int): The number of parameter search iteration. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search.
            timeout (Optional[int]): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool): Synchronous mode.
            queue_name (Optional[str]): Queue name.
            jm_sampleset (Optional[bool]): Option to use jijmodeling.SampleSet.
            kwargs: Digital Annealer 3 parameters using **kwags. If both `**kwargs` and `parameters` are exist, the value of `**kwargs` takes precedence.

        Returns:
            DimodResponse: Stores minimum energy samples and other information.

        Examples:

            ```python
            import jijmodeling as jm
            from jijzept import JijDA3Sampler, JijDA3SolverParameters

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
            problem += jm.Constraint(
                "knapsack_constraint", jm.Sum(i, w[i] * x[i, j]) - y[j] * c <= 0, forall=j
            )

            feed_dict = {"num_items": 2, "w": [9, 1], "c": 10}
            multipliers = {"onehot_constraint": 11, "knapsack_constraint": 22}

            sampler = JijDA3Sampler(config="xx", da3_token="oo")
            parameters = JijDA3SolverParameters()

            sampleset = sampler.sample_model(
                problem, feed_dict, multipliers=multipliers, parameters=parameters
            )
            ```
        """

        if parameters is None:
            parameters = JijDA3SolverParameters()

        parameters = asdict(parameters)
        if kwargs:
            logging.warn(
                "Setting Parameters using **kwargs is not recommended. Use JijDA3SolverParameters class"
            )
            parameters.update(**kwargs)

        return super().sample_model(
            model=model,
            feed_dict=feed_dict,
            multipliers=multipliers,
            fixed_variables=fixed_variables,
            search=search,
            num_search=num_search,
            algorithm=algorithm,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
            parameters=parameters,
            token=self.da3_token,
            url=self.da3_url,
            jm_sampleset=jm_sampleset,
        )
