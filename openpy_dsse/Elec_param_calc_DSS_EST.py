# -*- coding: utf-8 -*-
# @Time    : 18/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
import numpy as np
import math
import cmath

from openpy_dsse import YBus_Matrix_Pos_Seq

from .OpenDSS_data_extraction import OpenDSS_data_collection, Values_per_unit, dss
from openpy_dsse.DSSE_algorithms.Symb_Eqn.sym_func_1ph import sym_func_Iij_rec
from .YBus_Matrix_Pos_Seq import get_G_B_Pos_seq, YBus_Matrix_SeqPos_OpenDSS
from .error_handling_logging import elem_YBus, orient, indent

data_DSS = OpenDSS_data_collection()

class estimated_electrical_variables:
    def __init__(self, I_Ang_EST: bool = False, PQi_EST: bool = False, PQf_EST: bool = False):
        self.I_Ang_EST = I_Ang_EST
        self.PQi_EST = PQi_EST
        self.PQf_EST = PQf_EST
    def Imang_Angle_EST_1ph(
            self,
            df_Results_DSSE: pd.DataFrame,
            SbasMVA_3ph: float,
            path_save: str,
            View_res: bool,
            DSS_col: bool,
            name_project: str
    ):
        I_Ang_EST_DSS = dict()
        YBus_1ph = YBus_Matrix_SeqPos_OpenDSS(data_DSS.allbusnames_aux())
        YBusMatrix_PU = YBus_1ph.YBus_Matrix_pu(
            SbasMVA_3ph=SbasMVA_3ph,
            YBus_Matrix=YBus_1ph.build_YBus_Matrix_Pos_Seq(
                element=elem_YBus
            )
        )
        Per_PU = Values_per_unit(SbasMVA_3ph=SbasMVA_3ph)
        I_elem_pu_DSS = Per_PU.element_Iij_PU(
            df_element_currents=data_DSS.element_currents_Iij_Ang(
                element=['lines'])
        )
        #Current
        I_elem_pu_DSS = I_elem_pu_DSS[['element_name', 'from_bus', 'to_bus', 'I1(pu)', 'ang1(deg)']]
        DF_Iij_aux_DSS = pd.merge(
            I_elem_pu_DSS, data_DSS.allbusnames_aux(),
            how='inner', left_on='from_bus', right_on='bus_name', suffixes=('_i', '')
        )
        DF_Iij_aux_DSS = pd.merge(
            DF_Iij_aux_DSS, data_DSS.allbusnames_aux(),
            how='inner', left_on='to_bus', right_on='bus_name', suffixes=('_j', '')
        )
        DF_Iij_aux_DSS = DF_Iij_aux_DSS.rename(
            columns={'bus_name_aux_j': 'from_bus_aux', 'bus_name_aux': 'to_bus_aux'}
        )
        DF_I_Ang_estimate = pd.DataFrame(
            columns=['element_name', 'from_bus', 'to_bus', 'I1(pu)', 'ang1(deg)'])
        DF_results_WLS = df_Results_DSSE.copy()
        for k in range(len(DF_results_WLS)):
            'angle'
            DF_results_WLS.at[k, 'Ang1(deg)_EST'] = math.radians(DF_results_WLS.at[k, 'Ang1(deg)_EST'])
        Matrix_WLS_results = np.array(DF_results_WLS)
        V_1 = np.array([Matrix_WLS_results[:, 2]]).T
        Vang_1 = np.array([Matrix_WLS_results[:, 3]]).T

        f29 = sym_func_Iij_rec()
        for index, row in DF_Iij_aux_DSS.iterrows():
            id_name = DF_Iij_aux_DSS['element_name'][index]
            m = DF_Iij_aux_DSS['from_bus_aux'][index] - 1
            n = DF_Iij_aux_DSS['to_bus_aux'][index] - 1

            G1, B1 = get_G_B_Pos_seq(m, n, YBusMatrix_PU)
            I_ij = f29(G1, B1, V_1[m][0], Vang_1[m][0], V_1[n][0], Vang_1[n][0])
            I1, ang1 = cmath.polar(I_ij)
            DF_I_Ang_estimate = DF_I_Ang_estimate.append({
                'element_name': id_name,
                'from_bus': DF_Iij_aux_DSS['from_bus'][index],
                'to_bus': DF_Iij_aux_DSS['to_bus'][index],
                'I1(pu)': I1, 'ang1(deg)': math.degrees(ang1) - 180}, ignore_index=True)

        I_Ang_EST_DSS['df_EST'] = DF_I_Ang_estimate.rename(columns={'I1(pu)': 'I1(pu)_EST', 'ang1(deg)': 'Ang1(deg)_EST'})
        I_Ang_EST_DSS['df_DSS'] = I_elem_pu_DSS.rename(columns={'I1(pu)': 'I1(pu)_DSS', 'ang1(deg)': 'Ang1(deg)_DSS'})
        if DSS_col:
            df_DSS_EST = pd.merge(I_Ang_EST_DSS['df_DSS'], I_Ang_EST_DSS['df_EST'], on=('element_name', 'from_bus', 'to_bus'))
        else:
            df_DSS_EST = I_Ang_EST_DSS['df_EST']
        if View_res:
            print(df_DSS_EST)
        if path_save is not None:
            df_DSS_EST.to_excel(f'{path_save}\Results_I_Ang_from_DSSE_{name_project}.xlsx', index=False)

            df_DSS_EST_json = df_DSS_EST.to_json(orient=orient, indent=indent)
            with open(f"{path_save}\Results_I_Ang_from_DSSE_{name_project}.json", "w") as outfile:
                outfile.write(df_DSS_EST_json)
        return I_Ang_EST_DSS

