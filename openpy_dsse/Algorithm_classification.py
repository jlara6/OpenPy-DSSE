# -*- coding: utf-8 -*-
# @Time    : 18/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import logging
import os
import cmath

import pathlib
import matplotlib.pyplot as plt
import seaborn as sns
from timeit import default_timer
from functools import reduce

from .base_DSSE import *
from .MEAS_from_OpenDSS import Normalization_MEAS
from .YBus_Matrix_Pos_Seq import *
from .DSSE_algorithms.WLS_alg_1ph import WLS_1ph_state_estimator
from .DSSE_algorithms.WLS_alg_Pos_Seq import WLS_Pos_state_estimator
from .error_handling_logging import update_logg_file, to_Excel_MEAS, elem_YBus, orient, indent

pd.options.mode.chained_assignment = None

#dss = py_dss_interface.DSSDLL()
data_DSS = OpenDSS_data_collection()
log_py = logging.getLogger(__name__)

def DSS_EST_save_view(
        results_DSSE: dict, MEAS_dict: dict(),
        path_save: str, name_project: str,
        DSS_coll: bool, View_res: bool, summary: bool):

    if View_res:
        print('-' * 64)
        print(f'{name_project}\nState estimation was successful\nResults obtained:')

    if DSS_coll:
        df_DSS_EST = pd.merge(results_DSSE['df_DSS'], results_DSSE['df_EST'], on=('bus_name', 'Bus Nro.'))
    else:
        df_DSS_EST = results_DSSE['df_EST']

    if path_save is not None:
        df_DSS_EST.to_excel(f'{path_save}\Results_DSSE_{name_project}.xlsx', index=False)

        df_DSS_EST_json = df_DSS_EST.to_json(orient=orient, indent=indent)
        with open(f"{path_save}\Results_DSSE_{name_project}.json", "w") as outfile:
            outfile.write(df_DSS_EST_json)

    if View_res and summary:
        print(f"Number of iterations: {results_DSSE['n_Iter']}")
        tol = format(results_DSSE['tol'], '.2E')
        print(f"Tolerance obtained :{tol}")
        print(f"Simulation time: {format(results_DSSE['time'], '.2E')} seg")
        list_aux = list()
        for x, y in results_DSSE['num_MEAS'].items():
            list_aux.append(f"|| {x}: {y}")
        print("Type and number of measurements:")
        print(*list_aux)

    if View_res == True:
        print(df_DSS_EST)

    if to_Excel_MEAS == True:
        df_MEAS_SCADA = MEAS_dict['SCADA']
        df_MEAS_PMU = MEAS_dict['PMU']
        if path_save != '':
            df_MEAS_SCADA.to_excel(f'{path_save}\MEAS_SCADA_{name_project}.xlsx', index=False)

        if (path_save != '') and (df_MEAS_PMU.empty == False):
            df_MEAS_PMU.to_excel(f'{path_save}\MEAS_PMU_{name_project}.xlsx', index=False)

def DSS_V_Ang_opt(option: list):
    df_V_Ang_dss = data_DSS.Volt_Ang_auxDSS_PU()
    df_V_Ang_dss = df_V_Ang_dss.drop(['num_nodes', 'ph_1', 'ph_2', 'ph_3'], axis=1)

    if option == alg_mapping['op1'] or \
            option == alg_mapping['op2'] or \
            option == alg_mapping['op3'] or \
            option == alg_mapping['op4'] or \
            option == alg_mapping['op5']:
        df_V_Ang_dss = df_V_Ang_dss.drop(['V2(pu)', 'V3(pu)', 'Ang2(deg)', 'Ang3(deg)'], axis=1)
        df_V_Ang_dss = df_V_Ang_dss.rename(columns={'V1(pu)': 'V1(pu)_DSS', 'Ang1(deg)': 'Ang1(deg)_DSS'})
    return df_V_Ang_dss

def EST_add_name_DSS(df_V_ang: pd.DataFrame):
    data_aux = data_DSS.allbusnames_aux().rename(columns={'bus_name_aux': 'Bus Nro.'})
    df_V_ang = data_aux.merge(df_V_ang, left_on='Bus Nro.', right_on='Bus Nro.')
    return df_V_ang

class DSSE_algorithms(BaseAlgorithm, File_options, Algorithm_options):
    """
    Class that selects the type of the state estimation algorithm
    """
    def __init__(
            self,
            Sbas3ph_MVA: float, tolerance: float, max_iter: int, init_values: str,
            DSS_path: str, MEAS_path: str, path_save: str, Typ_cir: str, ALG: str, coord: str, method: str,
            name_project: str, MEAS_Pos: str, DSS_coll: bool, View_res: bool, summary: bool
    ) -> None:
        """
        DSSE_algorithms class constructor
        """
        BaseAlgorithm.__init__(self, Sbas3ph_MVA, tolerance, max_iter, init_values)
        File_options.__init__(self, DSS_path, MEAS_path, path_save, MEAS_Pos, name_project)
        Algorithm_options.__init__(self, Typ_cir, ALG, coord, method)
        self.DSS_coll = DSS_coll
        self.View_res = View_res
        self.summary = summary

    def addresses_algorithm(self):
        option = [self.Typ_cir, self.ALG, self.coord, self.method]
        Alg_Typ = diff_algorithms(
            self.Sbas3ph_MVA,
            self.tolerance,
            self.max_iter,
            self.init_values,
            self.DSS_path,
            self.MEAS_path,
            self.path_save,
            self.MEAS_Pos,
            self.name_project,
            alg_opt=option
        )
        if option == alg_mapping['op1'] or option == alg_mapping['op2'] or option == alg_mapping['op3']:
            state_estimation, MEAS_study = Alg_Typ.WLS_1ph_NV_Polar_linear_nonlinear_PMU(self.View_res)
        elif option == alg_mapping['op4'] or option == alg_mapping['op5']:
            state_estimation, MEAS_study = Alg_Typ.WLS_Pos_NV_Polar_nonlinear_PMU(self.View_res)
        else:
            update_logg_file('Select the configuration: Typ_circ, Alg, coord and method available. See documentation', 4, log_py)
            exit()

        DSS_EST_save_view(
            state_estimation, MEAS_study,
            self.path_save, self.name_project, self.DSS_coll, self.View_res, self.summary)
        return state_estimation

class diff_algorithms(BaseAlgorithm, File_options):

    def __init__(
            self,
            Sbas3ph_MVA,
            tolerance,
            max_iter,
            init_values,
            DSS_path,
            MEAS_path,
            path_save,
            MEAS_Pos,
            name_project,
            alg_opt: list
    ) -> None:
        """
        diff_algorithms class constructor
        """
        BaseAlgorithm.__init__(self, Sbas3ph_MVA, tolerance, max_iter, init_values)
        File_options.__init__(self, DSS_path, MEAS_path, path_save, MEAS_Pos, name_project)
        self.alg_opt = alg_opt

    def WLS_1ph_NV_Polar_linear_nonlinear_PMU(self, View_res: bool):
        # Empty objects
        Results_DSSE = dict()
        MEAS_DSSE = dict()
        'Connecting to OpenDSS'
        dss.text(f'compile [{self.DSS_path}]')
        dss.solution_solve()

        if View_res:
            update_logg_file('State estimation of a single-phase distribution network ', 1, log_py)

        'Obtain initial values of voltage and angle'
        df_Volt_Ang_init = data_DSS.initial_voltage_angle_option(option=self.init_values)
        df_Volt_Ang_init = df_Volt_Ang_init.drop(
            ['num_nodes', 'ph_2', 'ph_3', 'V2(pu)', 'V3(pu)', 'Ang2(rad)', 'Ang3(rad)'], axis=1)

        'Get circuit YBus from OpenDSS'
        #initialize class
        YBus_1ph = YBus_Matrix_SeqPos_OpenDSS(data_DSS.allbusnames_aux())
        Ybus_PU = YBus_1ph.YBus_Matrix_pu(
            SbasMVA_3ph=self.Sbas3ph_MVA,
            YBus_Matrix=YBus_1ph.build_YBus_Matrix_Pos_Seq(
                element=elem_YBus
            )
        )
        'Get circuit YBus from OpenDSS'

        'Obtain measurements according to type and configuration'
        #initialize class
        get_MEAS = Normalization_MEAS(
            MEAS_path=self.MEAS_path,
            MEAS_Pos=self.MEAS_Pos,
            Sbas3ph_MVA=self.Sbas3ph_MVA,
            path_save=self.path_save,
            alg_opt=self.alg_opt
        )
        df_MEAS_SCADA = get_MEAS.SCADA_MEAS()
        df_MEAS_PMU = get_MEAS.PMU_MEAS()

        if self.alg_opt == alg_mapping['op1']:
            df_MEAS_PMU = pd.DataFrame(columns=df_MEAS_PMU.columns)

        # initialize class
        Alg_1ph = WLS_1ph_state_estimator(
            tolerance=self.tolerance,
            num_iter_max=self.max_iter,
            DF_MEAS_SCADA=df_MEAS_SCADA,
            DF_MEAS_PMU=df_MEAS_PMU,
            DF_Volt_Ang_initial=df_Volt_Ang_init,
            YBus_Matrix=Ybus_PU
        )
        if self.alg_opt == alg_mapping['op1'] or self.alg_opt == alg_mapping['op2']:
            started = default_timer()
            df_V_ang, n_Iter, tol, num_MEAS = Alg_1ph.WLS_nonlinear_linear_PMU()
            finished = default_timer()
            time = finished - started

        if self.alg_opt == alg_mapping['op3']:
            started = default_timer()
            arr_V_ang, df_V_ang, n_Iter, tol, num_MEAS = Alg_1ph.WLS_nonlinear_PMU()
            finished = default_timer()
            time = finished - started

        Results_DSSE['df_EST'] = EST_add_name_DSS(df_V_ang)
        Results_DSSE['df_DSS'] = DSS_V_Ang_opt(self.alg_opt)
        Results_DSSE['n_Iter'] = n_Iter
        Results_DSSE['tol'] = tol
        Results_DSSE['time'] = time
        Results_DSSE['num_MEAS'] = num_MEAS
        MEAS_DSSE['SCADA'] = df_MEAS_SCADA
        MEAS_DSSE['PMU'] = df_MEAS_PMU

        return Results_DSSE, MEAS_DSSE

    def WLS_Pos_NV_Polar_nonlinear_PMU(self, View_res: bool):
        # Empty objects
        Results_DSSE = dict()
        MEAS_DSSE = dict()
        'Connecting to OpenDSS'
        dss.text(f'compile [{self.DSS_path}]')
        'creation of the positive sequence circuit'
        dss.text('MakePosSeq')
        dss.text(f'Save Circuit Dir=({os.path.abspath(os.getcwd())}\PosSeq circuit)')
        SeqPos_address = f'{os.path.abspath(os.getcwd())}\PosSeq circuit\Master.DSS'
        dss.text(f'compile [{SeqPos_address}]')
        dss.solution_solve()
        '**************************************************************************************************************'
        '_______________________________________________START -> STATE ESTIMATOR_______________________________________'
        if View_res:
            update_logg_file('State estimation through the positive sequence equivalent circuit', 2, log_py)

        'Obtain initial values of voltage and angle'
        df_Volt_Ang_init = data_DSS.initial_voltage_angle_option(option=self.init_values)
        df_Volt_Ang_init = df_Volt_Ang_init.drop(
            ['num_nodes', 'ph_2', 'ph_3', 'V2(pu)', 'V3(pu)', 'Ang2(rad)', 'Ang3(rad)'], axis=1)
        'Get circuit YBus from OpenDSS'
        YBus_SeqPos = YBus_Matrix_SeqPos_OpenDSS(data_DSS.allbusnames_aux())  # start the class
        Ybus_PU = YBus_SeqPos.YBus_Matrix_pu(
            SbasMVA_3ph=self.Sbas3ph_MVA,
            YBus_Matrix=YBus_SeqPos.build_YBus_Matrix_Pos_Seq(element=elem_YBus))

        'Obtain measurements according to type and configuration as per study_case_DSSE.py'
        get_MEAS = Normalization_MEAS(
            MEAS_path=self.MEAS_path,
            MEAS_Pos=self.MEAS_Pos,
            Sbas3ph_MVA=self.Sbas3ph_MVA,
            path_save=self.path_save,
            alg_opt=self.alg_opt
        )
        df_MEAS_SCADA, df_MEAS_PMU = get_MEAS.SCADA_PMU_MEAS_Pos()
        if self.alg_opt == ['Pos', 'NV', 'polar', 'nonlinear']:
            df_MEAS_PMU = pd.DataFrame(
                columns=df_MEAS_PMU.columns
            )
        Alg_Pos = WLS_Pos_state_estimator(
            tolerance=self.tolerance,
            num_iter_max=self.max_iter,
            DF_MEAS_SCADA=df_MEAS_SCADA,
            DF_MEAS_PMU=df_MEAS_PMU,
            DF_Volt_Ang_initial=df_Volt_Ang_init,
            YBus_Matrix=Ybus_PU
        )
        if self.alg_opt == alg_mapping['op4']:
            started = default_timer()
            df_V_ang, n_Iter, tol, num_MEAS = Alg_Pos.WLS_linear_nonlinear_PMU()
            finished = default_timer()
            time = finished - started
        elif self.alg_opt == alg_mapping['op5']:
            started = default_timer()
            df_V_ang, n_Iter, tol, num_MEAS = Alg_Pos.WLS_nonlinear_PMU()
            finished = default_timer()
            time = finished - started
        Results_DSSE['df_EST'] = EST_add_name_DSS(df_V_ang)
        Results_DSSE['df_DSS'] = DSS_V_Ang_opt(self.alg_opt)
        Results_DSSE['n_Iter'] = n_Iter
        Results_DSSE['tol'] = tol
        Results_DSSE['time'] = time
        Results_DSSE['num_MEAS'] = num_MEAS

        MEAS_DSSE['SCADA'] = df_MEAS_SCADA
        MEAS_DSSE['PMU'] = df_MEAS_PMU

        return Results_DSSE, MEAS_DSSE





