# GridCal
# Copyright (C) 2022 Santiago Peñate Vera
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import numpy as np
from GridCal.Engine.basic_structures import Logger
from GridCal.Engine.Simulations.PowerFlow.power_flow_options import PowerFlowOptions
from GridCal.Engine.Simulations.PowerFlow.power_flow_worker import multi_island_pf
from GridCal.Engine.Simulations.PowerFlow.power_flow_results import PowerFlowResults
# from GridCal.Engine.Simulations.OPF.opf_results import OptimalPowerFlowResults
from GridCal.Engine.Core.multi_circuit import MultiCircuit
from GridCal.Engine.Simulations.driver_types import SimulationTypes
from GridCal.Engine.Simulations.driver_template import DriverTemplate
from GridCal.Engine.Core.Compilers.circuit_to_newton import NEWTON_AVAILBALE, to_newton_native, newton_power_flow
from GridCal.Engine.Core.Compilers.circuit_to_bentayga import BENTAYGA_AVAILABLE, bentayga_pf
import GridCal.Engine.basic_structures as bs


class PowerFlowDriver(DriverTemplate):
    name = 'Power Flow'
    tpe = SimulationTypes.PowerFlow_run

    """
    Power flow wrapper to use with Qt
    """
    def __init__(self, grid: MultiCircuit, options: PowerFlowOptions, opf_results: "OptimalPowerFlowResults" = None,
                 engine: bs.EngineType = bs.EngineType.GridCal):
        """
        PowerFlowDriver class constructor
        :param grid: MultiCircuit instance
        :param options: PowerFlowOptions instance
        :param opf_results: OptimalPowerFlowResults instance
        """

        DriverTemplate.__init__(self, grid=grid, engine=engine)

        # Options to use
        self.options = options

        self.opf_results = opf_results

        self.results = PowerFlowResults(n=0, m=0, n_tr=0, n_hvdc=0,
                                        bus_names=(), branch_names=(), transformer_names=(),
                                        hvdc_names=(), bus_types=())

        self.logger = Logger()

        self.convergence_reports = list()

        self.__cancel__ = False

    def get_steps(self):
        """

        :return:
        """
        return list()

    def run(self):
        """
        Pack run_pf for the QThread
        :return:
        """

        if self.engine == bs.EngineType.Newton and not NEWTON_AVAILBALE:
            self.engine = bs.EngineType.GridCal
            self.logger.add_warning('Failed back to GridCal')

        if self.engine == bs.EngineType.Bentayga and not BENTAYGA_AVAILABLE:
            self.engine = bs.EngineType.GridCal
            self.logger.add_warning('Failed back to GridCal')

        if self.engine == bs.EngineType.GridCal:
            self.results = multi_island_pf(multi_circuit=self.grid,
                                           options=self.options,
                                           opf_results=self.opf_results,
                                           logger=self.logger)
            self.convergence_reports = self.results.convergence_reports

        elif self.engine == bs.EngineType.Newton:

            nc = to_newton_native(self.grid)
            res = newton_power_flow(nc, self.options)

            self.results = PowerFlowResults(n=nc.bus_data.active.shape[0],
                                            m=nc.branch_data.active.shape[0],
                                            n_tr=nc.transformer_data.active.shape[0],
                                            n_hvdc=nc.transformer_data.active.shape[0],
                                            bus_names=nc.bus_data.names,
                                            branch_names=nc.branch_data.names,
                                            transformer_names=nc.transformer_data.names,
                                            hvdc_names=nc.hvdc_data.names,
                                            bus_types=nc.bus_data.types)

            self.results.voltage = res.voltage
            self.results.Sbus = res.Sbus
            self.results.Sf = res.Sf
            self.results.St = res.St
            self.results.loading = res.Loading
            self.results.losses = res.Losses
            self.results.Vbranch = res.VBranch
            self.results.F = (nc.Cf * np.arange(nc.Cf.shape[1])).astype(int)
            self.results.T = (nc.Ct * np.arange(nc.Ct.shape[1])).astype(int)
            self.results.hvdc_F = (nc.hvdc_data.Cf * np.arange(nc.hvdc_data.Cf.shape[1])).astype(int)
            self.results.hvdc_T = (nc.hvdc_data.Ct * np.arange(nc.hvdc_data.Ct.shape[1])).astype(int)
            self.results.bus_area_indices = self.grid.get_bus_area_indices()
            self.results.area_names = [a.name for a in self.grid.areas]
            print('newton error:', res.error)

        elif self.engine == bs.EngineType.Bentayga:

            res = bentayga_pf(self.grid, self.options, time_series=False)

            self.results = PowerFlowResults(n=self.grid.get_bus_number(),
                                            m=self.grid.get_branch_number_wo_hvdc(),
                                            n_tr=self.grid.get_transformers2w_number(),
                                            n_hvdc=self.grid.get_hvdc_number(),
                                            bus_names=res.bus_names,
                                            branch_names=res.branch_names,
                                            transformer_names=[],
                                            hvdc_names=res.hvdc_names,
                                            bus_types=res.bus_types)

            self.results.voltage = res.V[0, :]
            self.results.Sbus = res.S[0, :]
            self.results.Sf = res.Sf[0, :]
            self.results.St = res.St[0, :]
            self.results.loading = res.loading[0, :]
            self.results.losses = res.losses[0, :]
            self.results.Vbranch = res.Vbranch[0, :]
            self.results.If = res.If[0, :]
            self.results.It = res.It[0, :]
            self.results.Beq = res.Beq[0, :]
            self.results.m = res.tap_modules[0, :]
            self.results.theta = res.tap_angles[0, :]
            self.results.F = res.F
            self.results.T = res.T
            self.results.hvdc_F = res.F_hvdc
            self.results.hvdc_T = res.T_hvdc
            self.results.hvdc_Pf = res.hvdc_Pf[0, :]
            self.results.hvdc_Pt = res.hvdc_Pt[0, :]
            self.results.hvdc_loading = res.hvdc_loading[0, :]
            self.results.hvdc_losses = res.hvdc_losses[0, :]
            self.results.bus_area_indices = self.grid.get_bus_area_indices()
            self.results.area_names = [a.name for a in self.grid.areas]
            print('Bentayga error:', res.stats)

        else:
            raise Exception('Engine ' + self.engine.value + ' not implemented for ' + self.name)
