# -*- coding: utf-8 -*-
# @Time    : 03/03/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import py_dss_interface
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from .OpenDSS_data_extraction import *


#dss = py_dss_interface.DSSDLL()

class YBus_Matrix_SeqPos_OpenDSS:

    def __init__(self, DF_allbusnames_aux: pd.DataFrame):
        self.DF_allbusnames_aux = DF_allbusnames_aux

    def build_YBus_Matrix_Pos_Seq(self, element: List[str]) -> np.array:

        nbus = dss.circuit_num_buses()
        Y_Bus = np.zeros((nbus, nbus), dtype=complex)
        DF = self.DF_allbusnames_aux

        for ii in element:
            if ii == 'vsources':
                num_element = dss.vsources_count()
                dss.vsources_first()
            elif ii == 'transformers':
                num_element = dss.transformers_count()
                dss.transformers_first()
            elif ii == 'lines':
                num_element = dss.lines_count()
                dss.lines_first()
            elif ii == 'loads':
                num_element = dss.loads_count()
                dss.loads_first()
            elif ii == 'capacitors':
                num_element = dss.capacitors_count()
                dss.capacitors_first()

            for num in range(num_element):
                if ii == 'loads':
                    bus2 = ''
                else:
                    bus2 = dss.cktelement_read_bus_names()[1]
                num_cond, node_order, bus1, bus2 = dss.cktelement_num_conductors(), dss.cktelement_node_order(), \
                                                   dss.cktelement_read_bus_names()[0], bus2
                from_bus, to_bus = from_to_bus(ii, num_cond, node_order, bus1, bus2)

                if ii == 'loads':
                    if dss.cktelement_num_phases() == 1:
                        n_Gii, n_Bii = 0, 1
                        n_Gij, n_Bij = 2, 3
                        n_Gji, n_Bji = 4, 5
                        n_Gjj, n_Bjj = 6, 7
                        Yii = np.array([[complex(dss.cktelement_y_prim()[n_Gii], (dss.cktelement_y_prim()[n_Bii]))]])
                        Yij = np.array([[complex(dss.cktelement_y_prim()[n_Gij], (dss.cktelement_y_prim()[n_Bij]))]])
                        Yji = np.array([[complex(dss.cktelement_y_prim()[n_Gji], (dss.cktelement_y_prim()[n_Bji]))]])
                        Yjj = np.array([[complex(dss.cktelement_y_prim()[n_Gjj], (dss.cktelement_y_prim()[n_Bjj]))]])
                else:
                    if dss.cktelement_num_phases() == 1:
                        n_Gii, n_Bii = 0, 1
                        n_Gij, n_Bij = 2, 3
                        n_Gji, n_Bji = 4, 5
                        n_Gjj, n_Bjj = 6, 7
                        Yii = np.array([[complex(dss.cktelement_y_prim()[n_Gii], (dss.cktelement_y_prim()[n_Bii]))]])
                        Yij = np.array([[complex(dss.cktelement_y_prim()[n_Gij], (dss.cktelement_y_prim()[n_Bij]))]])
                        Yji = np.array([[complex(dss.cktelement_y_prim()[n_Gji], (dss.cktelement_y_prim()[n_Bji]))]])
                        Yjj = np.array([[complex(dss.cktelement_y_prim()[n_Gjj], (dss.cktelement_y_prim()[n_Bjj]))]])

                if from_bus != '' and to_bus != '':
                    aux_i = (int(DF[DF['bus_name'] == from_bus]['bus_name_aux']) - 1)
                    aux_j = (int(DF[DF['bus_name'] == to_bus]['bus_name_aux']) - 1)
                elif from_bus != '' and to_bus == '':
                    aux_i = (int(DF[DF['bus_name'] == from_bus]['bus_name_aux']) - 1)
                    aux_j = ''

                if aux_i == aux_j or aux_j == '':
                    # Yii
                    Y_Bus[aux_i, aux_i] = Y_Bus[aux_i, aux_i] + Yii
                else:
                    # Yii
                    # Yii
                    Y_Bus[aux_i, aux_i] = Y_Bus[aux_i, aux_i] + Yii
                    # Yij
                    Y_Bus[aux_i, aux_j] = Y_Bus[aux_i, aux_j] + Yij
                    # Yji
                    Y_Bus[aux_j, aux_i] = Y_Bus[aux_j, aux_i] + Yji
                    # Yjj
                    Y_Bus[aux_j, aux_j] = Y_Bus[aux_j, aux_j] + Yjj

                if ii == 'transformers':
                    dss.transformers_next()
                elif ii == 'lines':
                    dss.lines_next()
                elif ii == 'loads':
                    dss.loads_next()
                elif ii == 'capacitors':
                    dss.capacitors_next()
                elif ii == 'vsources':
                    dss.vsources_next()

        return Y_Bus

    def YBus_Matrix_pu(self, SbasMVA_3ph: float, YBus_Matrix: np.array) -> np.array:
        """
        Transform YBus_Matrix into values per unit

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :param SbasMVA_3ph: Circuit Base Power
        :param YBus_Matrix: Return the function -> build_YBus_Matrix
        :param DF_allbusnames_aux: Return the function: allbusnames_aux
        :return: YBus_Matrix
        """

        SbasMVA_1ph = SbasMVA_3ph / 3
        DF = self.DF_allbusnames_aux

        for n in range(len(DF)):
            # bus_name = DF['bus_name'][n]
            dss.circuit_set_active_bus(DF['bus_name'][n])
            kVbase = dss.bus_kv_base()
            Zbas = pow(kVbase, 2) / SbasMVA_1ph
            Ybas = 1 / Zbas
            bus = (DF['bus_name_aux'][n] - 1)
            YBus_Matrix[bus, :] = YBus_Matrix[bus, :] / Ybas

        return YBus_Matrix


def get_G_B_Pos_seq(m: int, k: int, YBus_Matrix:np.array):
    """
    Function to search with coordinates m, k in YBus Matrix

    :param m: position "m" in the matrix
    :param k: position "k" in the matrix
    :param YBus_Matrix: Return of the function -> build_YBus_Matrix
    :return: G, B, G_matrix, B_matrix
    """
    Y_Matrix = YBus_Matrix[m, k]

    G = Y_Matrix.real
    B = Y_Matrix.imag

    return G, B

def Get_YMatrix_Pos_seq(DF_sequence: pd.DataFrame, DF_allbusnames_aux: pd.DataFrame):

    DF_aux = DF_allbusnames_aux
    DF_sequence.loc[:, 'from_bus_aux'] = ''
    DF_sequence.loc[:, 'to_bus_aux'] = ''
    DF_sequence.loc[:, 'B/2'] = DF_sequence['B1']
    DF_sequence['B/2'] = pd.to_numeric(DF_sequence['B/2'], errors='coerce')
    DF_sequence['B/2'] = DF_sequence['B/2'] / 2
    DF_sequence.loc[:, 'TAP'] = 1

    for index, row in DF_sequence.iterrows():
        DF_sequence.at[index, 'from_bus_aux'] = int(DF_aux[DF_aux['bus_name'] == DF_sequence['from_bus'][index]]['bus_name_aux'])
        DF_sequence.at[index, 'to_bus_aux'] = int(DF_aux[DF_aux['bus_name'] == DF_sequence['to_bus'][index]]['bus_name_aux'])

    line_data = np.array(DF_sequence)
    fb = line_data[:, 17]  # From bus number...
    tb = line_data[:, 18]  # To bus number...
    R1 = line_data[:, 11]  # Resistance, R1...
    X1 = line_data[:, 12]  # Reactance, X1...
    B1 = np.array([line_data[:, 19]]).T  # Ground Admittance, B/2...
    A1 = np.array([line_data[:, 20]]).T  # Tap setting value..
    Z1 = np.array(R1 + 1j * X1)  # Z matrix...
    Y1 = np.array([1 / Z1]).T  # To get inverse of each element...
    B1 = 1j * B1

    nbus = max(max(np.array(line_data[:, 17], dtype=int)), max(np.array(line_data[:, 18], dtype=int)))
    nbranch = len(fb)
    Ysec_bus = np.zeros((nbus, nbus), dtype=complex)

    # Formation of the Off Diagonal Elements...
    for k in range(nbranch):
        Ysec_bus[int(fb[k] - 1), int(tb[k] - 1)] = Ysec_bus[int(fb[k] - 1), int(tb[k] - 1)] - Y1[k] / A1[k]
        Ysec_bus[int(tb[k] - 1), int(fb[k] - 1)] = Ysec_bus[int(fb[k] - 1), int(tb[k] - 1)]

    # Formation of Diagonal Elements....
    for m in range(nbus):
        for n in range(nbranch):
            if fb[n] - 1 == m:
                Ysec_bus[m, m] = Ysec_bus[m, m] + (Y1[n] / A1[n] ** 2) + B1[n]

            elif tb[n] - 1 == m:
                Ysec_bus[m, m] = Ysec_bus[m, m] + Y1[n] + B1[n]

    return Ysec_bus




