from typing import Union

import numpy as np
import spotpy
from spotpy.objectivefunctions import rmse
from spotpy.parameter import Uniform, ParameterSet

from hydromodel.models.gr4j import gr4j
from hydromodel.models.hymod import hymod
from hydromodel.models.xaj import xaj


class SpotSetup(object):
    def __init__(self, p_and_e, qobs, warmup_length=30, model="xaj", obj_func=None):
        """
        Set up for Spotpy

        Parameters
        ----------
        p_and_e
            inputs of model
        qobs
            observation data
        warmup_length
            GR4J model need warmup period
        model
            we support "gr4j", "hymod", and "xaj"
        obj_func
            objective function, typically RMSE
        """
        if model == "xaj":
            self.parameter_names = [
                # Allen, R.G., L. Pereira, D. Raes, and M. Smith, 1998.
                # Crop Evapotranspiration, Food and Agriculture Organization of the United Nations,
                # Rome, Italy. FAO publication 56. ISBN 92-5-104219-5. 290p.
                "K",  # ratio of potential evapotranspiration to reference crop evaporation generally from Allen, 1998
                "B",  # The exponent of the tension water capacity curve
                "IM",  # The ratio of the impervious to the total area of the basin
                "UM",  # Tension water capacity in the upper layer
                "LM",  # Tension water capacity in the lower layer
                "DM",  # Tension water capacity in the deepest layer
                "C",  # The coefficient of deep evapotranspiration
                "SM",  # The areal mean of the free water capacity of surface soil layer
                "EX",  # The exponent of the free water capacity curve
                "KI",  # Outflow coefficients of interflow
                "KG",  # Outflow coefficients of groundwater
                "CS",  # The recession constant of channel system
                "L",  # Lag time
                "CI",  # The recession constant of the lower interflow
                "CG",  # The recession constant of groundwater storage
            ]
        elif model == "xaj_mz":
            # use mizuRoute for xaj's surface routing module
            self.parameter_names = [
                # Allen, R.G., L. Pereira, D. Raes, and M. Smith, 1998.
                # Crop Evapotranspiration, Food and Agriculture Organization of the United Nations,
                # Rome, Italy. FAO publication 56. ISBN 92-5-104219-5. 290p.
                "K",  # ratio of potential evapotranspiration to reference crop evaporation generally from Allen, 1998
                "B",  # The exponent of the tension water capacity curve
                "IM",  # The ratio of the impervious to the total area of the basin
                "UM",  # Tension water capacity in the upper layer
                "LM",  # Tension water capacity in the lower layer
                "DM",  # Tension water capacity in the deepest layer
                "C",  # The coefficient of deep evapotranspiration
                "SM",  # The areal mean of the free water capacity of surface soil layer
                "EX",  # The exponent of the free water capacity curve
                "KI",  # Outflow coefficients of interflow
                "KG",  # Outflow coefficients of groundwater
                "A",  # parameter of mizuRoute
                "THETA",  # parameter of mizuRoute
                "CI",  # The recession constant of the lower interflow
                "CG",  # The recession constant of groundwater storage
            ]
        elif model == "gr4j":
            self.parameter_names = ["x1", "x2", "x3", "x4"]
        elif model == "hymod":
            self.parameter_names = ["cmax", "bexp", "alpha", "ks", "kq"]
        else:
            raise NotImplementedError("We don't provide this model now")
        self.model = model
        self.params = []
        for par_name in self.parameter_names:
            # All parameters' range are [0,1], we will transform them to normal range in the model
            self.params.append(Uniform(par_name, low=0.0, high=1.0))
        # Just a way to keep this example flexible and applicable to various examples
        self.obj_func = obj_func
        # Load Observation data from file
        self.p_and_e = p_and_e
        # chose observation data after warmup period
        self.true_obs = qobs[warmup_length:, :, :]
        self.warmup_length = warmup_length

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self, x: ParameterSet) -> Union[list, np.array]:
        """
        run xaj model

        Parameters
        ----------
        x
            the parameters of xaj. This function only has this one parameter.

        Returns
        -------
        Union[list, np.array]
            simulated result from xaj
        """
        # Here the model is started with one parameter combination
        # TODO: Now ParameterSet only support one list, and we only support one basin's calibration now
        # parameter, 2-dim variable: [basin=1, parameter]
        params = np.array(x).reshape(1, -1)
        if self.model == "xaj":
            sim = xaj(self.p_and_e, params, warmup_length=self.warmup_length)
        elif self.model == "xaj_mz":
            sim = xaj(
                self.p_and_e,
                params,
                warmup_length=self.warmup_length,
                route_method="MZ",
            )
        elif self.model == "gr4j":
            sim = gr4j(self.p_and_e, params, warmup_length=self.warmup_length)
        elif self.model == "hymod":
            sim = hymod(self.p_and_e, params, warmup_length=self.warmup_length)
        else:
            raise NotImplementedError("We don't provide this model now")
        return sim[:, 0, 0]

    def evaluation(self) -> Union[list, np.array]:
        """
        read observation values

        Returns
        -------
        Union[list, np.array]
            observation
        """
        # TODO: we only support one basin's calibration now
        return self.true_obs[:, 0, 0]

    def objectivefunction(
        self,
        simulation: Union[list, np.array],
        evaluation: Union[list, np.array],
        params=None,
    ) -> float:
        """
        A user defined objective function to calculate fitness.

        Parameters
        ----------
        simulation:
            simulation results
        evaluation:
            evaluation results
        params:
            parameters leading to the simulation

        Returns
        -------
        float
            likelihood
        """
        # SPOTPY expects to get one or multiple values back,
        # that define the performance of the model run
        if not self.obj_func:
            # This is used if not overwritten by user
            like = rmse(evaluation, simulation)
        else:
            # Way to ensure flexible spot setup class
            like = self.obj_func(evaluation, simulation)
        return like


def calibrate_by_sceua(p_and_e, qobs, warmup_length=30, model="xaj", **sce_ua_param):
    """
    Function for calibrating hymod

    Parameters
    ----------
    p_and_e
        inputs of model
    qobs
        observation data
    warmup_length
        the length of warmup period
    model
        we support "gr4j", "hymod", and "xaj"
    sce_ua_param
        parameters for sce_ua: random seed=2000, rep=5000, ngs=7, kstop=3, peps=0.1, pcento=0.1 (default values)

    Returns
    -------
    None
    """
    random_seed = sce_ua_param["random_seed"]
    rep = sce_ua_param["rep"]
    ngs = sce_ua_param["ngs"]
    kstop = sce_ua_param["kstop"]
    peps = sce_ua_param["peps"]
    pcento = sce_ua_param["pcento"]
    np.random.seed(random_seed)  # Makes the results reproduceable

    # Initialize the xaj example
    # In this case, we tell the setup which algorithm we want to use, so
    # we can use this exmaple for different algorithms
    spot_setup = SpotSetup(
        p_and_e,
        qobs,
        warmup_length=warmup_length,
        model=model,
        obj_func=spotpy.objectivefunctions.rmse,
    )
    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.sceua(
        spot_setup, dbname="SCEUA_" + model, dbformat="csv", random_state=random_seed
    )
    # Start the sampler, one can specify ngs, kstop, peps and pcento id desired
    sampler.sample(rep, ngs=ngs, kstop=kstop, peps=peps, pcento=pcento)
    print("Calibrate Finished!")
