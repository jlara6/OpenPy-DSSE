# -*- coding: utf-8 -*-
# @Time    : 18/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import numpy as np
#from .Algorithm_classification import *
#from .OpenDSS_data_extraction import OpenDSS_data_collection
from .error_handling_logging import update_logg_file

# Options or combinations currently available
# op = [Typ_cir: str, ALG: str, coord: str, method: str]
alg_mapping = {
    'op1': ['1ph', 'NV', 'polar', 'nonlinear'],
    'op2': ['1ph', 'NV', 'polar', 'linear_PMU'],
    'op3': ['1ph', 'NV', 'polar', 'nonlinear_PMU'],
    'op4': ['Pos', 'NV', 'polar', 'nonlinear'],
    'op5': ['Pos', 'NV', 'polar', 'nonlinear_PMU']
}

class File_options:

    def __init__(self, DSS_path: str, MEAS_path: str, path_save: str, MEAS_Pos: bool, name_project: str):

        self.DSS_path = DSS_path
        self.MEAS_path = MEAS_path
        self.path_save = path_save
        self.MEAS_Pos = MEAS_Pos
        self.name_project = name_project

class Algorithm_options:

    def __init__(self, Typ_cir: str, ALG: str, coord: str, method: str):
        self.Typ_cir = Typ_cir
        self.ALG = ALG
        self.coord = coord
        self.method = method

class BaseAlgorithm:

    def __init__(self, Sbas3ph_MVA: float, tolerance: float, max_iter: int, init_values: str):

        self.Sbas3ph_MVA = Sbas3ph_MVA
        self.tolerance = tolerance
        self.max_iter = max_iter
        self.init_values = init_values
        self.successful = False

class functions_DSSE:
    def check_observability(self, num_state_var, num_measurements, log_py):
        if num_measurements < (2 * num_state_var) - 1:
            update_logg_file("System is not observable (cancelling)", 4, log_py)
            update_logg_file(f'Measurements available: {num_measurements}. '
                             f'Measurements required: {(2 * num_state_var) - 1}', 3, log_py)
            exit()

            raise UserWarning("Measurements available: %d. Measurements required: %d" %
                              (num_measurements, (2 * num_state_var) - 1))

            exit()
        else:
            pass

    def check_num_max_iter(self, max_iter, n_Iter, tol, log_py):
        if max_iter <= n_Iter:
            if max_iter > 1:
                update_logg_file(f"The state estimation algorithm does not converge", 4, log_py)
                update_logg_file(f"Number of iterrations:{max_iter}, Tolerance: {format(tol, '.2E')}", 4, log_py)
                update_logg_file("Suggestion, change the location and type of measurements", 3, log_py)
                exit()

    def calculate_Ginv(self, Gm: np.array, log_py):
        try:
            G_inv = np.linalg.inv(Gm)
        except:
            update_logg_file('Cannot calculate inverse matrix of G, change type and location of measurements', 4, log_py)
            exit()
        return G_inv

class Estimating_other_parameters:
    def __init__(self, I_Ang_EST: bool = False, PQi_EST: bool = False, PQf_EST: bool = False):
        self.I_Ang_EST = I_Ang_EST
        self.PQi_EST = PQi_EST
        self.PQf_EST = PQf_EST

class Plot_DSSE_results:
    def __init__(self, Plot_results: bool = False, no_PU: bool = False, MAPE: bool = False, MAE: bool = False, RMSE: bool = False):

        self.Plot_results = Plot_results
        self.no_PU = no_PU
        self.MAPE = MAPE
        self.MAE = MAE
        self.RMSE = RMSE

class Bad_data_detection(BaseAlgorithm):

    def __init__(self, Sbas3ph_MVA, tolerance, max_iter, init_values):
        super(Bad_data_detection, self).__init__(Sbas3ph_MVA, tolerance, max_iter, init_values)

        # Parameters for Bad data detection
        self.R_inv = None
        self.Gm = None
        self.r = None
        self.H = None
        self.hx = None

