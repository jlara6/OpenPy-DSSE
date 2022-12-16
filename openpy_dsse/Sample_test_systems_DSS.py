# -*- coding: utf-8 -*-
# @Time    : 18/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import os
import pathlib
import logging
from .base_DSSE import update_logg_file

log_py = logging.getLogger(__name__)

class Sample_tests:

    def examples(
            self,
            Typ_cir: str,
            case: int, sub_case: int = None
    ):
        script_path = os.path.dirname(os.path.abspath(__file__))
        circuit = dict()

        if Typ_cir == '1ph':
            if case == 1:
                circuit['DSS_file'] = pathlib.Path(script_path).joinpath(
                    "./examples", "4Node", "OpenDSS files", "Master_4node.dss")
                circuit['MEAS_path'] = pathlib.Path(script_path).joinpath("./examples", "4Node", "MEAS_files")
                circuit['save_path'] = pathlib.Path(script_path).joinpath("./examples", "4Node", "Results")
                circuit['name_project'] = '4Node'

            if case == 2:
                circuit['DSS_file'] = pathlib.Path(script_path).joinpath(
                    "./examples", "15NodeIEEE", "OpenDSS files", "Master_15node.dss")
                circuit['MEAS_path'] = pathlib.Path(script_path).joinpath("./examples", "15NodeIEEE", "MEAS_files")
                circuit['save_path'] = pathlib.Path(script_path).joinpath("./examples", "15NodeIEEE", "Results")
                circuit['name_project'] = '15NodeIEEE'
            circuit['Typ_cir'] = Typ_cir

        if Typ_cir == 'Pos':
            if case == 1:
                circuit['DSS_file'] = pathlib.Path(script_path).joinpath(
                    "./examples", "13NodeIEEE", "OpenDSS files", "Master13NodeIEEE.DSS")
                circuit['MEAS_path'] = pathlib.Path(script_path).joinpath("./examples", "13NodeIEEE", "MEAS_files")
                circuit['save_path'] = pathlib.Path(script_path).joinpath("./examples", "13NodeIEEE", "Results")
                circuit['name_project'] = '13NodeIEEE'
            if case == 2:
                circuit['DSS_file'] = pathlib.Path(script_path).joinpath(
                    "./examples", "37NodeIEEE", "OpenDSS files", "Master_ieee37.DSS")
                circuit['MEAS_path'] = pathlib.Path(script_path).joinpath("./examples", "37NodeIEEE", "MEAS_files")
                circuit['save_path'] = pathlib.Path(script_path).joinpath("./examples", "37NodeIEEE", "Results")
                circuit['name_project'] = '37nodeIEEE'
            circuit['Typ_cir'] = Typ_cir

        res = not circuit

        if res == True:
            update_logg_file('Select an available test case (1ph or Pos), see documentation.', 4, log_py)
            exit()

        return circuit
