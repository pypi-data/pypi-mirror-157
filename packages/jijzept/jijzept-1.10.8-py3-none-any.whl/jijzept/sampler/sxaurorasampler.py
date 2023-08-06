from numbers import Number
from typing import Dict, List, Optional, Tuple, Union

import cimod
import numpy as np
import openjij as oj

from jijmodeling.expression.expression import Expression

from jijzept.client import JijZeptClient
from jijzept.entity.schema import SolverType
from jijzept.post_api import post_instance_and_query
from jijzept.response import DimodResponse
from jijzept.sampler.jijmodel_post import JijModelingInterface


class JijSXAuroraSampler(JijModelingInterface):
    jijmodeling_solver_type = SolverType(queue_name="sxaurorasolver", solver="SAParaSearch")

    def __init__(
        self,
        token: str = None,
        url: Union[str, Dict] = None,
        proxy=None,
        config=None,
        config_env="default",
    ):
        """Sets token and url.

        Args:
            token (str, optional): Token string. Defaults to None.
            url (Union[str, Dict], optional): API URL. Defaults to None.
            proxy (str, optional) Proxy URL. Defaults to None.
            config (str, optional): Config file path. Defaults to None.

        Raises:
            :obj:`TypeError`: `token`, `url`, or `config` is not str.
        """
        self.client = JijZeptClient(url, token, proxy, config, config_env)

    def sample_model(
        self,
        model: Expression,
        feed_dict: Dict[str, Union[Number, list, np.ndarray]],
        multipliers: Dict[str, Number] = {},
        fixed_variables: Dict[str, Dict[Tuple[int, ...], Union[int, float]]] = {},
        search: bool = False,
        num_search: int = 15,
        algorithm: Optional[str] = None,
        num_sweeps: Optional[int] = None,
        beta_min: Optional[float] = None,
        beta_max: Optional[float] = None,
        num_reads: Optional[int] = None,
        tsallis_q: Optional[float] = None,
        timeout: Optional[int] = None,
        sync: bool = True,
        queue_name: Optional[str] = None,
    ) -> DimodResponse:
        """Sample using JijModeling by means of Microsoft QIO Simulated Annealing solver.

        Args:
            model (Expression): Mathematical expression of JijModeling.
            feed_dict (Dict[str, Union[Number, list, np.ndarray]]): The actual values to be assigned to the placeholders.
            multipliers (Dict[str, Number], optional): The actual multipliers for penalty terms, derived from constraint conditions.
            fixed_variables (Dict[str, Dict[Tuple[int, ...], Union[int, float]]]): dictionary of variables to fix.
            search (bool, optional): If `True`, the parameter search will be carried out, which tries to find better values of multipliers for penalty terms.
            num_search (int, optional): The number of parameter search iteration. Defaults to set 15. This option works if `search` is `True`.
            algorithm (Optional[str]): Algorithm for parameter search. Defaults to None.
            num_sweeps (Optional[int], optional): The number of Monte-Carlo steps. If `None`, this will be set automatically.
            beta_min (Optional[float], optional): Minimum (initial) inverse temperature. If `None`, this will be set automatically.
            beta_max (Optional[float], optional): Maximum (final) inverse temperature. If `None`, this will be set automatically.
            num_reads (Optional[int], optional): The number of samples. If `None`, this will be set automatically.
            tsallis_q (Optional[float], optional): q value of tsallis statistics. If `None`, this will be set automatically.
            timeout (Optional[int], optional): The number of timeout [sec] for post request. If `None`, 3600 (one hour) will be set.
            sync (bool, optional): Synchronous mode.

        Returns:
            dimod.SampleSet: Stores minimum energy samples and other information.

        Examples:

        ```python
        import jijzept as jz
        import jijmodeling as jm
        n = jm.Placeholder('n')
        x = jm.Binary('x', shape=n)
        d = jm.Placeholder('d', shape=n)
        i = jm.Element("i", n)
        problem = jm.Problem('problem')
        problem += jm.Sum({i: n}, d[i] * x[i])
        sampler = jz.JijSXAuroraSampler(config='config.toml')
        response = sampler.sample_model(problem, feed_dict={'n': 5, 'd': [1,2,3,4,5]})
        ```
        """

        return super().sample_model(
            model,
            feed_dict=feed_dict,
            multipliers=multipliers,
            fixed_variables=fixed_variables,
            search=search,
            num_search=num_search,
            algorithm=algorithm,
            num_sweeps=num_sweeps,
            beta_min=beta_min,
            beta_max=beta_max,
            num_reads=num_reads,
            tsallis_q=tsallis_q,
            timeout=timeout,
            sync=sync,
            queue_name=queue_name,
        )

