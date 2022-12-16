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

from .OpenDSS_data_extraction import OpenDSS_data_collection, dss

data_DSS = OpenDSS_data_collection()

class estimated_electrical_variables:

    def __init__(self, I_Ang_EST: bool = False, PQi_EST: bool = False, PQf_EST: bool = False):
        self.I_Ang_EST = I_Ang_EST
        self.PQi_EST = PQi_EST
        self.PQf_EST = PQf_EST

    def Imang_Angle_EST_1ph(self, I_elem_pu_DSS: pd.DataFrame, df_Results_DSSE: pd.DataFrame, YBusMatrix_PU: np.array):

        #Current
        I_elem_pu_DSS = I_elem_pu_DSS[['element_name', 'from_bus', 'to_bus', 'I1(pu)', 'ang1(deg)']]
        DF_Iij_aux_DSS = pd.merge(I_elem_pu_DSS, data_DSS.allbusnames_aux(),
                                  how='inner', left_on='from_bus', right_on='bus_name', suffixes=('_i', ''))

        DF_Iij_aux_DSS = pd.merge(DF_Iij_aux_DSS, data_DSS.allbusnames_aux(), how='inner', left_on='to_bus',
                                  right_on='bus_name',
                                  suffixes=('_j', ''))

        DF_Iij_aux_DSS = DF_Iij_aux_DSS.rename(
            columns={'bus_name_aux_j': 'from_bus_aux', 'bus_name_aux': 'to_bus_aux'})

        DF_I_Ang_estimate = pd.DataFrame(
            columns=['element_name', 'from_bus', 'to_bus', 'I1(pu)', 'ang1(deg)'])

        DF_results_WLS = df_Results_DSSE.copy()
        for k in range(len(DF_results_WLS)):
            'angle'
            DF_results_WLS.at[k, 'Ang1(deg)'] = math.radians(DF_results_WLS.at[k, 'Ang1(deg)'])

        Matrix_WLS_results = np.array(DF_results_WLS)
        V_1 = np.array([Matrix_WLS_results[:, 1]]).T
        Vang_1 = np.array([Matrix_WLS_results[:, 2]]).T

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

        return DF_I_Ang_estimate

