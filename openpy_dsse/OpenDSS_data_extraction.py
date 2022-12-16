# -*- coding: utf-8 -*-
# @Time    : 03/03/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm
import logging

import py_dss_interface
import numpy as np
import pandas as pd
import scipy as sp
import math
from typing import Dict, Tuple, List
from .error_handling_logging import update_logg_file

log_py = logging.getLogger(__name__)
dss = py_dss_interface.DSSDLL()

class OpenDSS_data_collection:
    """
    Functions that allow bringing parameters and results from OpenDSS into DataFrame
    """

    def allbusnames_aux(self) -> pd.DataFrame:
        """
        Returns a dataframe with the nodes and an auxiliary number ['bus_name', 'bus_name_aux'].

        :return: DF_allbusnames_aux.
        """
        ynodeorder = dss.circuit_all_bus_names()
        name_nodes_list = list()
        a = 1
        for _ in range(len(ynodeorder)):
            name_nodes_list.append(a)
            a += 1

        name_nodes_list = list(zip(ynodeorder, name_nodes_list))
        DF_allbusnames_aux = pd.DataFrame(name_nodes_list, columns=['bus_name', 'bus_name_aux'])

        return DF_allbusnames_aux

    def Bus_name_nodes_conn_ph(self) -> pd.DataFrame:
        """
        Obtains from OpenDSS the voltages and angles per bus or node in a dataFrame with the following columns:
        ['bus_name', 'num_nodes', 'phase_1', 'phase_2', 'phase_3', 'voltage_bus1', 'angle_bus1', 'voltage_bus2',
        'angle_bus2', 'voltage_bus3', 'angle_bus3']

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :return: DF_voltage_angle_node
        """
        bus_names = dss.circuit_all_bus_names()

        bus_terminal1, bus_terminal2, bus_terminal3 = list(), list(), list()
        bus_name, num_nodes = list(), list()
        node_3, node_2, node_1 = 0, 0, 0

        for bus in bus_names:
            dss.circuit_set_active_bus(bus)
            if dss.bus_num_nodes() == 1:
                node_1 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                if dss.bus_nodes()[0] == 1:
                    bus_terminal1.append(1)
                    bus_terminal2.append(0)
                    bus_terminal3.append(0)

                elif dss.bus_nodes()[0] == 2:
                    bus_terminal1.append(0)
                    bus_terminal2.append(1)
                    bus_terminal3.append(0)

                elif dss.bus_nodes()[0] == 3:
                    bus_terminal1.append(0)
                    bus_terminal2.append(0)
                    bus_terminal3.append(1)

            elif dss.bus_num_nodes() == 2:
                node_2 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                if dss.bus_nodes()[0] == 1 and dss.bus_nodes()[1] == 2:
                    bus_terminal1.append(1)
                    bus_terminal2.append(1)
                    bus_terminal3.append(0)

                elif dss.bus_nodes()[0] == 1 and dss.bus_nodes()[1] == 3:
                    bus_terminal1.append(1)
                    bus_terminal2.append(0)
                    bus_terminal3.append(1)

                elif dss.bus_nodes()[0] == 2 and dss.bus_nodes()[1] == 3:
                    bus_terminal1.append(0)
                    bus_terminal2.append(1)
                    bus_terminal3.append(1)

            elif dss.bus_num_nodes() == 3:
                node_3 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                bus_terminal1.append(1)
                bus_terminal2.append(1)
                bus_terminal3.append(1)

            elif dss.bus_num_nodes() == 4:
                node_3 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                bus_terminal1.append(1)
                bus_terminal2.append(1)
                bus_terminal3.append(1)


        voltage_angle_list = list(
            zip(bus_name, num_nodes, bus_terminal1, bus_terminal2, bus_terminal3))

        DF_voltage_angle_node = pd.DataFrame(
            voltage_angle_list, columns=['bus_name', 'num_nodes', 'ph_1', 'ph_2', 'ph_3'])

        return DF_voltage_angle_node

    def Elem_name_ncond_conn_fb_tb_ph(self, element: List[str]) -> pd.DataFrame:
        """
        Obtains from OpenDSS the active and reactive powers according to list(element) in a dataFrame with the following
        columns: ['element_name', 'num_phases', 'num_cond', 'conn', 'from_bus', 'to_bus', 'bus1', 'bus2', 'phase_1',
        'phase_2', 'phase_3', 'P1(kW)', 'Q1(kvar)', 'P2(kW)', 'Q2(kvar)', 'P3(kW)', 'Q3(kvar)']

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :param element: list['vsources', 'transformers', 'lines', 'loads', 'capacitors']
        :return: DF_element_PQ
        """
        element_name_list = list()
        num_cond_list = list()
        num_phases_list = list()
        conn_list = list()
        from_bus_list = list()
        to_bus_list = list()
        element_bus1_list = list()
        element_bus2_list = list()
        element_terminal1_list = list()
        element_terminal2_list = list()
        element_terminal3_list = list()

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
                    if dss.loads_read_is_delta() == 1:
                        conn = 'delta'
                    else:
                        conn = 'wye'
                else:
                    bus2 = dss.cktelement_read_bus_names()[1]
                    conn = ''

                num_cond, node_order, bus1, bus2 = dss.cktelement_num_conductors(), dss.cktelement_node_order(), \
                                                   dss.cktelement_read_bus_names()[0], bus2
                from_bus, to_bus = from_to_bus(ii, num_cond, node_order, bus1, bus2)
                element_name_list.append(dss.cktelement_name())
                num_cond_list.append(num_cond)
                num_phases_list.append(dss.cktelement_num_phases())
                element_bus1_list.append(bus1)
                element_bus2_list.append(bus2)
                from_bus_list.append(from_bus)
                to_bus_list.append(to_bus)
                conn_list.append(conn)

                if ii == 'loads':
                    if conn == 'delta':
                        if len(dss.cktelement_node_order()) == 1:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)

                        elif len(dss.cktelement_node_order()) == 2:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)

                        elif len(dss.cktelement_node_order()) == 3:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)

                    elif conn == 'wye':

                        if len(dss.cktelement_node_order()) == 2:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)


                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)


                        elif len(dss.cktelement_node_order()) == 3:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)


                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)


                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)

                        elif len(dss.cktelement_node_order()) == 4:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)

                else:
                    if conn == '':
                        if dss.cktelement_num_phases() == 1:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)


                        elif dss.cktelement_num_phases() == 2:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)


                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)



                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)


                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)


                        elif dss.cktelement_num_phases() == 3:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)


                        elif dss.cktelement_num_phases() == 4:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)

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

        element_PQ_list = list(
            zip(element_name_list, num_phases_list, num_cond_list, conn_list, from_bus_list, to_bus_list,
                element_bus1_list, element_bus2_list, element_terminal1_list, element_terminal2_list,
                element_terminal3_list,))

        DF_element_PQ = pd.DataFrame(element_PQ_list,
                                     columns=['element_name', 'num_ph', 'num_cond', 'conn', 'from_bus', 'to_bus',
                                              'bus1', 'bus2', 'ph_1', 'ph_2', 'ph_3'])

        return DF_element_PQ

    def Volt_Ang_node_no_PU(self) -> pd.DataFrame:
        """
        Obtains from OpenDSS the voltages and angles per bus or node in a dataFrame with the following columns:
        ['bus_name', 'num_nodes', 'phase_1', 'phase_2', 'phase_3', 'voltage_bus1', 'angle_bus1', 'voltage_bus2',
        'angle_bus2', 'voltage_bus3', 'angle_bus3']

        :return: DF_voltage_angle_node
        """

        bus_names = dss.circuit_all_bus_names()
        Volt_1, Volt_2, Volt_3 = list(), list(), list()
        angle_bus1, angle_bus2, angle_bus3 = list(), list(), list()
        bus_terminal1, bus_terminal2, bus_terminal3 = list(), list(), list()
        bus_name, num_nodes = list(), list()
        node_3, node_2, node_1 = 0, 0, 0

        for bus in bus_names:
            dss.circuit_set_active_bus(bus)
            if dss.bus_num_nodes() == 1:
                node_1 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                if dss.bus_nodes()[0] == 1:
                    bus_terminal1.append(1)
                    bus_terminal2.append(0)
                    bus_terminal3.append(0)
                    Volt_1.append(dss.bus_vmag_angle()[0])
                    angle_bus1.append(dss.bus_vmag_angle()[1])
                    Volt_2.append(0)
                    angle_bus2.append(0)
                    Volt_3.append(0)
                    angle_bus3.append(0)
                elif dss.bus_nodes()[0] == 2:
                    bus_terminal1.append(0)
                    bus_terminal2.append(1)
                    bus_terminal3.append(0)
                    Volt_1.append(0)
                    angle_bus1.append(0)
                    Volt_2.append(dss.bus_vmag_angle()[0])
                    angle_bus2.append(dss.bus_vmag_angle()[1])
                    Volt_3.append(0)
                    angle_bus3.append(0)
                elif dss.bus_nodes()[0] == 3:
                    bus_terminal1.append(0)
                    bus_terminal2.append(0)
                    bus_terminal3.append(1)
                    Volt_1.append(0)
                    angle_bus1.append(0)
                    Volt_2.append(0)
                    angle_bus2.append(0)
                    Volt_3.append(dss.bus_vmag_angle()[0])
                    angle_bus3.append(dss.bus_vmag_angle()[1])

            elif dss.bus_num_nodes() == 2:
                node_2 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                if dss.bus_nodes()[0] == 1 and dss.bus_nodes()[1] == 2:
                    bus_terminal1.append(1)
                    bus_terminal2.append(1)
                    bus_terminal3.append(0)
                    Volt_1.append(dss.bus_vmag_angle()[0])
                    angle_bus1.append(dss.bus_vmag_angle()[1])
                    Volt_2.append(dss.bus_vmag_angle()[2])
                    angle_bus2.append(dss.bus_vmag_angle()[3])
                    Volt_3.append(0)
                    angle_bus3.append(0)

                elif dss.bus_nodes()[0] == 1 and dss.bus_nodes()[1] == 3:
                    bus_terminal1.append(1)
                    bus_terminal2.append(0)
                    bus_terminal3.append(1)
                    Volt_1.append(dss.bus_vmag_angle()[0])
                    angle_bus1.append(dss.bus_vmag_angle()[1])
                    Volt_2.append(0)
                    angle_bus2.append(0)
                    Volt_3.append(dss.bus_vmag_angle()[2])
                    angle_bus3.append(dss.bus_vmag_angle()[3])

                elif dss.bus_nodes()[0] == 2 and dss.bus_nodes()[1] == 3:
                    bus_terminal1.append(0)
                    bus_terminal2.append(1)
                    bus_terminal3.append(1)
                    Volt_1.append(0)
                    angle_bus1.append(0)
                    Volt_2.append(dss.bus_vmag_angle()[0])
                    angle_bus2.append(dss.bus_vmag_angle()[1])
                    Volt_3.append(dss.bus_vmag_angle()[2])
                    angle_bus3.append(dss.bus_vmag_angle()[3])

            elif dss.bus_num_nodes() == 3:
                node_3 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                bus_terminal1.append(1)
                bus_terminal2.append(1)
                bus_terminal3.append(1)
                Volt_1.append(dss.bus_vmag_angle()[0])
                angle_bus1.append(dss.bus_vmag_angle()[1])
                Volt_2.append(dss.bus_vmag_angle()[2])
                angle_bus2.append(dss.bus_vmag_angle()[3])
                Volt_3.append(dss.bus_vmag_angle()[4])
                angle_bus3.append(dss.bus_vmag_angle()[5])

            elif dss.bus_num_nodes() == 4:
                node_3 += 1
                num_nodes.append(dss.bus_num_nodes())
                bus_name.append(bus)
                bus_terminal1.append(1)
                bus_terminal2.append(1)
                bus_terminal3.append(1)
                Volt_1.append(dss.bus_vmag_angle()[0])
                angle_bus1.append(dss.bus_vmag_angle()[1])
                Volt_2.append(dss.bus_vmag_angle()[2])
                angle_bus2.append(dss.bus_vmag_angle()[3])
                Volt_3.append(dss.bus_vmag_angle()[4])
                angle_bus3.append(dss.bus_vmag_angle()[5])

        Volt_1 = [x / 1000 for x in Volt_1]
        Volt_2 = [x / 1000 for x in Volt_2]
        Volt_3 = [x / 1000 for x in Volt_3]

        voltage_angle_list = list(
            zip(bus_name, num_nodes, bus_terminal1, bus_terminal2, bus_terminal3, Volt_1, angle_bus1,
                Volt_2, angle_bus2, Volt_3, angle_bus3))

        DF_voltage_angle_node = pd.DataFrame(
            voltage_angle_list, columns=['bus_name', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
                                         'V1(kV)', 'Ang1(deg)', 'V2(kV)', 'Ang2(deg)', 'V3(kV)', 'Ang3(deg)'])

        return DF_voltage_angle_node

    def Volt_Ang_node_PU(self) -> pd.DataFrame:
        """
        Convert the result of function Volt_Ang_node_no_PU to value per unit

        :param dss: COM interface between OpenDSS and Python -> Electrical Network
        :param DF_Vmag_Ang_no_PU: Result of function Volt_Ang_node_no_PU(dss)
        :return:DF_Vmag_Ang_no_PU
        """

        DF_Vmag_Ang_PU = OpenDSS_data_collection.Volt_Ang_node_no_PU(dss)

        for n in range(len(DF_Vmag_Ang_PU)):
            dss.circuit_set_active_bus(DF_Vmag_Ang_PU['bus_name'][n])
            kVBas = dss.bus_kv_base()
            'Voltage'
            DF_Vmag_Ang_PU.at[n, 'V1(kV)'] = DF_Vmag_Ang_PU.at[n, 'V1(kV)'] / (kVBas)
            DF_Vmag_Ang_PU.at[n, 'V2(kV)'] = DF_Vmag_Ang_PU.at[n, 'V2(kV)'] / (kVBas)
            DF_Vmag_Ang_PU.at[n, 'V3(kV)'] = DF_Vmag_Ang_PU.at[n, 'V3(kV)'] / (kVBas)

        DF_Vmag_Ang_PU = DF_Vmag_Ang_PU.rename(
            columns={'V1(kV)': 'V1(pu)', 'V2(kV)': 'V2(pu)', 'V3(kV)': 'V3(pu)'})

        return DF_Vmag_Ang_PU

    def Volt_Ang_auxDSS_PU(self) -> pd.DataFrame:

        DF_Volt_Ang = OpenDSS_data_collection.Volt_Ang_node_PU(dss)
        DF_allbusnames_aux = OpenDSS_data_collection.allbusnames_aux(dss)

        'bus voltage measurements'
        DF_Volt_Ang = pd.merge(DF_Volt_Ang, DF_allbusnames_aux, how='inner', left_on='bus_name', right_on='bus_name')
        DF_Volt_Ang = DF_Volt_Ang[['bus_name', 'bus_name_aux', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
                                   'V1(pu)', 'V2(pu)', 'V3(pu)', 'Ang1(deg)', 'Ang2(deg)', 'Ang3(deg)']]
        DF_Volt_Ang = DF_Volt_Ang.rename(columns={'bus_name_aux': 'Bus Nro.'})
        DF_Volt_Ang = DF_Volt_Ang[['bus_name', 'Bus Nro.', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
                                   'V1(pu)', 'V2(pu)', 'V3(pu)', 'Ang1(deg)', 'Ang2(deg)', 'Ang3(deg)']]

        return DF_Volt_Ang

    def all_sequence_node_voltages(self) -> pd.DataFrame:
        """
        Get all the sequence node voltages in a dataframe with the following columns ['bus_name', 'num_nodes',
        'V1(kV)', 'V2(kV)', 'V0(kV)', '%V2/V1', '%V0/V1']

        :return: DF_sequence_node_voltages
        """

        bus_names = dss.circuit_all_bus_names()
        voltage_pos, voltage_neg, voltage_cero = list(), list(), list()
        bus_name, num_nodes = list(), list()
        for bus in bus_names:
            dss.circuit_set_active_bus(bus)
            num_nodes.append(dss.bus_num_nodes())
            bus_name.append(bus)
            voltage_pos.append(dss.bus_seq_voltages()[1] / 1000)
            voltage_neg.append(dss.bus_seq_voltages()[2] / 1000)
            voltage_cero.append(dss.bus_seq_voltages()[0] / 1000)

        voltage_sequence_list = list(zip(bus_name, num_nodes, voltage_pos, voltage_neg, voltage_cero))

        DF_sequence_node_voltages = pd.DataFrame(voltage_sequence_list,
                                                 columns=['bus_name', 'num_nodes', 'V1(kV)', 'V2(kV)', 'V0(kV)'])

        DF_sequence_node_voltages['%V2/V1'] = (DF_sequence_node_voltages['V2(kV)'] / DF_sequence_node_voltages[
            'V1(kV)']) * 100
        DF_sequence_node_voltages['%V0/V1'] = (DF_sequence_node_voltages['V0(kV)'] / DF_sequence_node_voltages[
            'V1(kV)']) * 100

        return DF_sequence_node_voltages

    def all_sequence_element_currents(self, element: List[str]) -> pd.DataFrame:
        """
        Get all the sequence node currents in a dataframe with the following columns ['element_name', 'num_nodes',
        'I1(kV)', 'I2(kV)', 'V0(kV)', '%I2/I1', '%V0/I1']

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :return: DF_sequence_node_currents
        """

        element_name_list = list()
        element_num_term_list = list()
        I1_list, I2_list, I0_list = list(), list(), list()

        for ii in element:
            if ii == 'transformers':
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
            elif ii == 'vsources':
                num_element = dss.vsources_count()
                dss.vsources_first()

            for num in range(num_element):
                name = dss.cktelement_name()
                if dss.cktelement_num_terminals() == 1:
                    element_name_list.append(dss.cktelement_name())
                    element_num_term_list.append(1)
                    I0_list.append(dss.cktelement_seq_currents()[0])
                    I1_list.append(dss.cktelement_seq_currents()[1])
                    I2_list.append(dss.cktelement_seq_currents()[2])
                elif dss.cktelement_num_terminals() == 2:
                    element_name_list.append(dss.cktelement_name())
                    element_num_term_list.append(1)
                    I0_list.append(dss.cktelement_seq_currents()[0])
                    I1_list.append(dss.cktelement_seq_currents()[1])
                    I2_list.append(dss.cktelement_seq_currents()[2])

                    element_name_list.append(dss.cktelement_name())
                    element_num_term_list.append(2)
                    I0_list.append(dss.cktelement_seq_currents()[3])
                    I1_list.append(dss.cktelement_seq_currents()[4])
                    I2_list.append(dss.cktelement_seq_currents()[5])

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

        current_sequence_list = list(zip(element_name_list, element_num_term_list, I0_list, I1_list, I2_list))

        DF_sequence_node_currents = pd.DataFrame(current_sequence_list,
                                                 columns=['element_name', ' Terminal', 'I0(A)', 'I1(A)', 'I2(A)'])

        DF_sequence_node_currents['%I2/I1'] = (DF_sequence_node_currents['I2(A)'] / DF_sequence_node_currents[
            'I1(A)']) * 100
        DF_sequence_node_currents['%I0/I1'] = (DF_sequence_node_currents['I0(A)'] / DF_sequence_node_currents[
            'I1(A)']) * 100

        return DF_sequence_node_currents

    def sequence_impedances(self) -> pd.DataFrame:
        """
        function to get the cmatrix of lines

        """

        line_name_list = list();
        num_phases = list()
        line_bus1 = list();
        line_bus2 = list()
        R1 = list()
        X1 = list()
        R0 = list()
        X0 = list()
        B1 = list()
        B0 = list()

        length, length_units = list(), list()
        linecode = list()
        length_units, linecode_units = list(), list()

        from_bus_list = list()
        to_bus_list = list()

        dss.lines_first()
        for lines in range(dss.lines_count()):
            length.append(dss.lines_read_length())
            length_units.append(dss.dssproperties_read_value('20'))
            linecode.append(dss.lines_read_linecode())
            line_name_list.append(dss.lines_read_name())
            line_bus1.append(dss.lines_read_bus1())
            line_bus2.append(dss.lines_read_bus2())
            num_phases.append(dss.lines_read_phases())

            from_bus_list.append(dss.lines_read_bus1()[:-6])
            to_bus_list.append(dss.lines_read_bus2()[:-6])

            R1.append(dss.lines_read_r1())
            X1.append(dss.lines_read_x1())
            R0.append(dss.lines_read_r0())
            X0.append(dss.lines_read_x0())
            B1.append(dss.dssproperties_read_value('26'))
            B0.append(dss.dssproperties_read_value('27'))

            dss.lines_next()

        lines_cdata_list = list(zip(line_name_list, num_phases, from_bus_list, to_bus_list,
                                    line_bus1, line_bus2, length, length_units, linecode,
                                    R1, X1, R0, X0, B1, B0))

        DF_sequence_impedances = pd.DataFrame(lines_cdata_list,
                                              columns=['line_name', 'num_phases', 'from_bus', 'to_bus',
                                                       'bus1', 'bus2', 'length', 'length_units', 'linecode',
                                                       'R1', 'X1', 'R0', 'X0', 'B1', 'B0'])

        return DF_sequence_impedances

    def lines_cdata(self) -> pd.DataFrame:
        """
        function to get the cmatrix of lines

        :return:

        """
        line_name_list = list();
        num_phases = list()
        lines_3ph_list = list();
        lines_2ph_list = list();
        lines_1ph_list = list()
        line_bus1 = list();
        line_bus2 = list()
        C11_mat = list()
        C22_mat = list()
        C33_mat = list()
        C12_mat = list()
        C23_mat = list()
        C13_mat = list()

        length, length_units = list(), list()
        linecode = list()
        length_units, linecode_units = list(), list()
        lines_3 = 0;
        lines_2 = 0;
        lines_1 = 0

        from_bus_list = list()
        to_bus_list = list()
        line_terminal1_list = list()
        line_terminal2_list = list()
        line_terminal3_list = list()

        dss.lines_first()
        for lines in range(dss.lines_count()):
            length.append(dss.lines_read_length())
            length_units.append(dss.dssproperties_read_value('20'))
            linecode.append(dss.lines_read_linecode())
            if dss.lines_read_phases() == 1:
                lines_1 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_1ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-2])
                to_bus_list.append(dss.lines_read_bus2()[:-2])
                if dss.cktelement_node_order()[0] == 1:
                    line_terminal1_list.append(1);
                    line_terminal2_list.append(0);
                    line_terminal3_list.append(0)
                    C11_mat.append(dss.lines_read_cmatrix()[0])
                    C22_mat.append(0)
                    C33_mat.append(0)
                    C12_mat.append(0)
                    C23_mat.append(0)
                    C13_mat.append(0)

                elif dss.cktelement_node_order()[0] == 2:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    C11_mat.append(0)
                    C22_mat.append(0)
                    C22_mat.append(dss.lines_read_cmatrix()[0])
                    C33_mat.append(0)
                    C12_mat.append(0)
                    C23_mat.append(0)
                    C13_mat.append(0)
                elif dss.cktelement_node_order()[0] == 3:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    C11_mat.append(0)
                    C22_mat.append(0)
                    C33_mat.append(dss.lines_read_cmatrix()[0])
                    C12_mat.append(0)
                    C23_mat.append(0)
                    C13_mat.append(0)

            elif dss.lines_read_phases() == 2:
                lines_2 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_2ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-4])
                to_bus_list.append(dss.lines_read_bus2()[:-4])
                if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    C11_mat.append(dss.lines_read_cmatrix()[0])
                    C22_mat.append(dss.lines_read_cmatrix()[3])
                    C33_mat.append(0)
                    C12_mat.append(dss.lines_read_cmatrix()[1])
                    C23_mat.append(0)
                    C13_mat.append(0)

                elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    C11_mat.append(dss.lines_read_cmatrix()[0])
                    C22_mat.append(0)
                    C33_mat.append(dss.lines_read_cmatrix()[3])
                    C12_mat.append(0)
                    C23_mat.append(0)
                    C13_mat.append(dss.lines_read_cmatrix()[1])

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    C11_mat.append(dss.lines_read_cmatrix()[0])
                    C22_mat.append(dss.lines_read_cmatrix()[3])
                    C33_mat.append(0)
                    C12_mat.append(dss.lines_read_cmatrix()[1])
                    C23_mat.append(0)
                    C13_mat.append(0)

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(1)
                    C11_mat.append(0)
                    C22_mat.append(dss.lines_read_cmatrix()[0])
                    C33_mat.append(dss.lines_read_cmatrix()[3])
                    C12_mat.append(0)
                    C23_mat.append(dss.lines_read_cmatrix()[1])
                    C13_mat.append(0)

                elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    C11_mat.append(dss.lines_read_cmatrix()[0])
                    C22_mat.append(0)
                    C33_mat.append(dss.lines_read_cmatrix()[3])
                    C12_mat.append(0)
                    C23_mat.append(0)
                    C13_mat.append(dss.lines_read_cmatrix()[1])

                elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(1)
                    C11_mat.append(0)
                    C22_mat.append(dss.lines_read_cmatrix()[0])
                    C33_mat.append(dss.lines_read_cmatrix()[3])
                    C12_mat.append(0)
                    C23_mat.append(dss.lines_read_cmatrix()[1])
                    C13_mat.append(0)

            elif dss.lines_read_phases() == 3:

                lines_3 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_3ph_list.append(dss.lines_read_name())

                from_bus_list.append(dss.lines_read_bus1()[:-6])
                to_bus_list.append(dss.lines_read_bus2()[:-6])
                line_terminal1_list.append(1)
                line_terminal2_list.append(1)
                line_terminal3_list.append(1)

                C11_mat.append(dss.lines_read_cmatrix()[0])
                C22_mat.append(dss.lines_read_cmatrix()[4])
                C33_mat.append(dss.lines_read_cmatrix()[8])
                C12_mat.append(dss.lines_read_cmatrix()[3])
                C23_mat.append(dss.lines_read_cmatrix()[7])
                C13_mat.append(dss.lines_read_cmatrix()[6])

            dss.lines_next()

        lines_cdata_list = list(zip(line_name_list, num_phases, from_bus_list, to_bus_list,
                                    line_bus1, line_bus2, line_terminal1_list, line_terminal2_list, line_terminal3_list,
                                    length, length_units, linecode,
                                    C11_mat, C22_mat, C33_mat, C12_mat, C23_mat, C13_mat))

        DF_lines_cdata = pd.DataFrame(lines_cdata_list,
                                      columns=['line_name', 'num_phases', 'from_bus', 'to_bus',
                                               'bus1', 'bus2', 'phase_1', 'phase_2', 'phase_3',
                                               'length', 'length_units', 'linecode',
                                               'C11_mat', 'C22_mat', 'C33_mat', 'C12_mat', 'C23_mat', 'C13_mat'])

        return DF_lines_cdata

    def lines_PQij(self) -> pd.DataFrame:
        line_name_list = list()
        lines_3ph_list = list()
        lines_2ph_list = list()
        lines_1ph_list = list()

        from_bus_list = list()
        to_bus_list = list()
        line_terminal1_list = list()
        line_terminal2_list = list()
        line_terminal3_list = list()

        num_phases = list()
        line_bus1 = list()
        line_bus2 = list()
        P1, P2, P3 = list(), list(), list()
        Q1, Q2, Q3 = list(), list(), list()
        lines_3 = 0;
        lines_2 = 0;
        lines_1 = 0
        dss.lines_first()
        for lines in range(dss.lines_count()):
            if dss.lines_read_phases() == 1:
                lines_1 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_1ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-2])
                to_bus_list.append(dss.lines_read_bus2()[:-2])
                if dss.cktelement_node_order()[0] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(0)
                    P1.append(dss.cktelement_powers()[0])
                    Q1.append(dss.cktelement_powers()[1])
                    P2.append(0);
                    Q2.append(0)
                    P3.append(0);
                    Q3.append(0)

                elif dss.cktelement_node_order()[0] == 2:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    P1.append(0);
                    Q1.append(0)
                    P2.append(dss.cktelement_powers()[0])
                    Q2.append(dss.cktelement_powers()[1])
                    P3.append(0);
                    Q3.append(0)

                elif dss.cktelement_node_order()[0] == 3:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    P1.append(0);
                    Q1.append(0)
                    P2.append(0);
                    Q2.append(0)
                    P3.append(dss.cktelement_powers()[0])
                    Q3.append(dss.cktelement_powers()[1])

            elif dss.lines_read_phases() == 2:
                lines_2 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_2ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-4])
                to_bus_list.append(dss.lines_read_bus2()[:-4])
                if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    P1.append(dss.cktelement_powers()[0])
                    Q1.append(dss.cktelement_powers()[1])
                    P2.append(dss.cktelement_powers()[2])
                    Q2.append(dss.cktelement_powers()[3])
                    P3.append(0);
                    Q3.append(0)

                elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    P1.append(dss.cktelement_powers()[0])
                    Q1.append(dss.cktelement_powers()[1])
                    P2.append(0);
                    Q2.append(0)
                    P3.append(dss.cktelement_powers()[2])
                    Q3.append(dss.cktelement_powers()[3])

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    P2.append(dss.cktelement_powers()[0])
                    Q2.append(dss.cktelement_powers()[1])
                    P1.append(dss.cktelement_powers()[2])
                    Q1.append(dss.cktelement_powers()[3])
                    P3.append(0);
                    Q3.append(0)

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(1)
                    P2.append(dss.cktelement_powers()[0])
                    Q2.append(dss.cktelement_powers()[1])
                    P3.append(dss.cktelement_powers()[2])
                    Q3.append(dss.cktelement_powers()[3])
                    P1.append(0);
                    Q1.append(0)

                elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    P3.append(dss.cktelement_powers()[0])
                    Q3.append(dss.cktelement_powers()[1])
                    P1.append(dss.cktelement_powers()[2])
                    Q1.append(dss.cktelement_powers()[3])
                    P2.append(0);
                    Q2.append(0)

                elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(1)
                    P3.append(dss.cktelement_powers()[0])
                    Q3.append(dss.cktelement_powers()[1])
                    P2.append(dss.cktelement_powers()[2])
                    Q2.append(dss.cktelement_powers()[3])
                    P1.append(0);
                    Q1.append(0)

            elif dss.lines_read_phases() == 3:

                lines_3 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_3ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-6])
                to_bus_list.append(dss.lines_read_bus2()[:-6])
                line_terminal1_list.append(1)
                line_terminal2_list.append(1)
                line_terminal3_list.append(1)
                P1.append(dss.cktelement_powers()[0])
                Q1.append(dss.cktelement_powers()[1])
                P2.append(dss.cktelement_powers()[2])
                Q2.append(dss.cktelement_powers()[3])
                P3.append(dss.cktelement_powers()[4])
                Q3.append(dss.cktelement_powers()[5])

            dss.lines_next()

        lines_PQij_list = list(zip(line_name_list, num_phases, from_bus_list, to_bus_list,
                                   line_bus1, line_bus2, line_terminal1_list, line_terminal2_list, line_terminal3_list,
                                   P1, Q1, P2, Q2, P3, Q3))

        DF_lines_PQij = pd.DataFrame(lines_PQij_list,
                                     columns=['line_name', 'num_phases', 'from_bus', 'to_bus',
                                              'bus1', 'bus2', 'phase_1', 'phase_2', 'phase_3',
                                              'P1(kW)', 'Q1(kvar)', 'P2(kW)', 'Q2(kvar)', 'P3(kW)', 'Q3(kvar)'])

        return DF_lines_PQij

    def lines_Iij(self) -> pd.DataFrame:
        line_name_list = list()
        lines_3ph_list = list()
        lines_2ph_list = list()
        lines_1ph_list = list()

        from_bus_list = list()
        to_bus_list = list()
        line_terminal1_list = list()
        line_terminal2_list = list()
        line_terminal3_list = list()

        num_phases = list()
        line_bus1 = list()
        line_bus2 = list()
        I1, I2, I3 = list(), list(), list()
        ang1, ang2, ang3 = list(), list(), list()
        lines_3 = 0;
        lines_2 = 0;
        lines_1 = 0
        dss.lines_first()
        for lines in range(dss.lines_count()):
            if dss.lines_read_phases() == 1:
                lines_1 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_1ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-2])
                to_bus_list.append(dss.lines_read_bus2()[:-2])
                if dss.cktelement_node_order()[0] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(0)
                    I1.append(dss.cktelement_currents_mag_ang()[0])
                    ang1.append(dss.cktelement_currents_mag_ang()[1])
                    I2.append(0);
                    ang2.append(0)
                    I3.append(0);
                    ang3.append(0)

                elif dss.cktelement_node_order()[0] == 2:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    I1.append(0);
                    ang1.append(0)
                    I2.append(dss.cktelement_currents_mag_ang()[0])
                    ang2.append(dss.cktelement_currents_mag_ang()[1])
                    I3.append(0);
                    ang3.append(0)

                elif dss.cktelement_node_order()[0] == 3:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    I1.append(0);
                    ang1.append(0)
                    I2.append(0);
                    ang2.append(0)
                    I3.append(dss.cktelement_currents_mag_ang()[0])
                    ang3.append(dss.cktelement_currents_mag_ang()[1])

            elif dss.lines_read_phases() == 2:
                lines_2 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_2ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-4])
                to_bus_list.append(dss.lines_read_bus2()[:-4])
                if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    I1.append(dss.cktelement_currents_mag_ang()[0])
                    ang1.append(dss.cktelement_currents_mag_ang()[1])
                    I2.append(dss.cktelement_currents_mag_ang()[2])
                    ang2.append(dss.cktelement_currents_mag_ang()[3])
                    I3.append(0);
                    ang3.append(0)

                elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    I1.append(dss.cktelement_currents_mag_ang()[0])
                    ang1.append(dss.cktelement_currents_mag_ang()[1])
                    I2.append(0);
                    ang2.append(0)
                    I3.append(dss.cktelement_currents_mag_ang()[2])
                    ang3.append(dss.cktelement_currents_mag_ang()[3])

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(0)
                    I2.append(dss.cktelement_currents_mag_ang()[0])
                    ang2.append(dss.cktelement_currents_mag_ang()[1])
                    I1.append(dss.cktelement_currents_mag_ang()[2])
                    ang1.append(dss.cktelement_currents_mag_ang()[3])
                    I3.append(0);
                    ang3.append(0)

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(1)
                    I2.append(dss.cktelement_currents_mag_ang()[0])
                    ang2.append(dss.cktelement_currents_mag_ang()[1])
                    I3.append(dss.cktelement_currents_mag_ang()[2])
                    ang3.append(dss.cktelement_currents_mag_ang()[3])
                    I1.append(0);
                    ang1.append(0)

                elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                    line_terminal1_list.append(1)
                    line_terminal2_list.append(0)
                    line_terminal3_list.append(1)
                    I3.append(dss.cktelement_currents_mag_ang()[0])
                    ang3.append(dss.cktelement_currents_mag_ang()[1])
                    I1.append(dss.cktelement_currents_mag_ang()[2])
                    ang1.append(dss.cktelement_currents_mag_ang()[3])
                    I2.append(0);
                    ang2.append(0)

                elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                    line_terminal1_list.append(0)
                    line_terminal2_list.append(1)
                    line_terminal3_list.append(1)
                    I3.append(dss.cktelement_currents_mag_ang()[0])
                    ang3.append(dss.cktelement_currents_mag_ang()[1])
                    I2.append(dss.cktelement_currents_mag_ang()[2])
                    ang2.append(dss.cktelement_currents_mag_ang()[3])
                    I1.append(0);
                    ang1.append(0)

            elif dss.lines_read_phases() == 3:

                lines_3 += 1
                line_name_list.append(dss.lines_read_name())
                line_bus1.append(dss.lines_read_bus1())
                line_bus2.append(dss.lines_read_bus2())
                num_phases.append(dss.lines_read_phases())
                lines_3ph_list.append(dss.lines_read_name())
                from_bus_list.append(dss.lines_read_bus1()[:-6])
                to_bus_list.append(dss.lines_read_bus2()[:-6])
                line_terminal1_list.append(1)
                line_terminal2_list.append(1)
                line_terminal3_list.append(1)
                I1.append(dss.cktelement_currents_mag_ang()[0])
                ang1.append(dss.cktelement_currents_mag_ang()[1])
                I2.append(dss.cktelement_currents_mag_ang()[2])
                ang2.append(dss.cktelement_currents_mag_ang()[3])
                I3.append(dss.cktelement_currents_mag_ang()[4])
                ang3.append(dss.cktelement_currents_mag_ang()[5])

            dss.lines_next()

        lines_Iij_list = list(zip(line_name_list, num_phases, from_bus_list, to_bus_list,
                                  line_bus1, line_bus2, line_terminal1_list, line_terminal2_list, line_terminal3_list,
                                  I1, ang1, I2, ang2, I3, ang3))

        DF_lines_Iij = pd.DataFrame(lines_Iij_list, columns=['line_name', 'num_phases', 'from_bus', 'to_bus',
                                                             'bus1', 'bus2', 'phase_1', 'phase_2', 'phase_3',
                                                             'I1(A)', 'ang1(deg)', 'I2(A)', 'ang2(deg)', 'I3(A)',
                                                             'ang3(deg)'])

        return DF_lines_Iij

    def loads_PQi(self) -> pd.DataFrame:
        loads_name_list = list()
        loads_3ph_list, loads_2ph_list, loads_1ph_list = list(), list(), list()
        loads_terminal1_list, loads_terminal2_list, loads_terminal3_list = list(), list(), list()
        from_bus_list = list()
        loads_model = list()
        num_phases = list()
        loads_bus = list()
        loads_conn = list()
        P1, P2, P3 = list(), list(), list()
        Q1, Q2, Q3 = list(), list(), list()
        loads_3, loads_2, loads_1 = 0, 0, 0
        loads_delta, loads_wye = 0, 0
        dss.loads_first()
        for _ in range(dss.loads_count()):
            dss.circuit_setactiveelement(f'load.{dss.loads_read_name()}')
            if dss.loads_read_is_delta() == 1:
                loads_delta += 1
                loads_conn.append('delta')
                if len(dss.cktelement_node_order()) == 1:
                    loads_1 += 1
                    loads_name_list.append(dss.loads_read_name())
                    num_phases.append(dss.cktelement_num_phases())
                    from_bus_list.append(dss.cktelement_read_bus_names()[0][:-2])
                    loads_model.append(dss.loads_read_model())
                    loads_bus.append(dss.cktelement_read_bus_names()[0])
                    loads_1ph_list.append(dss.lines_read_name())
                    if dss.cktelement_node_order()[0] == 1:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(0)
                        P1.append(dss.cktelement_powers()[0])
                        Q1.append(dss.cktelement_powers()[1])
                        P2.append(0)
                        Q2.append(0)
                        P3.append(0)
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 2:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(0)
                        P1.append(0);
                        Q1.append(0)
                        P2.append(dss.cktelement_powers()[0])
                        Q2.append(dss.cktelement_powers()[1])
                        P3.append(0);
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 3:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(1)
                        P1.append(0);
                        Q1.append(0)
                        P2.append(0);
                        Q2.append(0)
                        P3.append(dss.cktelement_powers()[0])
                        Q3.append(dss.cktelement_powers()[1])

                elif len(dss.cktelement_node_order()) == 2:
                    loads_2 += 1
                    loads_name_list.append(dss.loads_read_name())
                    num_phases.append(dss.cktelement_num_phases() + 1)
                    from_bus_list.append(dss.cktelement_read_bus_names()[0][:-4])
                    loads_model.append(dss.loads_read_model())
                    loads_bus.append(dss.cktelement_read_bus_names()[0])
                    loads_2ph_list.append(dss.lines_read_name())
                    if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(0)
                        P1.append(dss.cktelement_powers()[0])
                        Q1.append(dss.cktelement_powers()[1])
                        P2.append(dss.cktelement_powers()[2])
                        Q2.append(dss.cktelement_powers()[3])
                        P3.append(0);
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(1)
                        P1.append(dss.cktelement_powers()[0])
                        Q1.append(dss.cktelement_powers()[1])
                        P2.append(0);
                        Q2.append(0)
                        P3.append(dss.cktelement_powers()[2])
                        Q3.append(dss.cktelement_powers()[3])

                    elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(0)
                        P2.append(dss.cktelement_powers()[0])
                        Q2.append(dss.cktelement_powers()[1])
                        P1.append(dss.cktelement_powers()[2])
                        Q1.append(dss.cktelement_powers()[3])
                        P3.append(0);
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(1)
                        P2.append(dss.cktelement_powers()[0])
                        Q2.append(dss.cktelement_powers()[1])
                        P3.append(dss.cktelement_powers()[2])
                        Q3.append(dss.cktelement_powers()[3])
                        P1.append(0);
                        Q1.append(0)

                    elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(1)
                        P3.append(dss.cktelement_powers()[0])
                        Q3.append(dss.cktelement_powers()[1])
                        P1.append(dss.cktelement_powers()[2])
                        Q1.append(dss.cktelement_powers()[3])
                        P2.append(0);
                        Q2.append(0)

                    elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(1)
                        P3.append(dss.cktelement_powers()[0])
                        Q3.append(dss.cktelement_powers()[1])
                        P2.append(dss.cktelement_powers()[2])
                        Q2.append(dss.cktelement_powers()[3])
                        P1.append(0);
                        Q1.append(0)

                elif len(dss.cktelement_node_order()) == 3:
                    loads_3 += 1
                    loads_name_list.append(dss.loads_read_name())
                    num_phases.append(dss.cktelement_num_phases())
                    from_bus_list.append(dss.cktelement_read_bus_names()[0][:-6])
                    loads_model.append(dss.loads_read_model())
                    loads_bus.append(dss.cktelement_read_bus_names()[0])
                    loads_3ph_list.append(dss.lines_read_name())
                    loads_terminal1_list.append(1)
                    loads_terminal2_list.append(1)
                    loads_terminal3_list.append(1)
                    P1.append(dss.cktelement_powers()[0])
                    Q1.append(dss.cktelement_powers()[1])
                    P2.append(dss.cktelement_powers()[2])
                    Q2.append(dss.cktelement_powers()[3])
                    P3.append(dss.cktelement_powers()[4])
                    Q3.append(dss.cktelement_powers()[5])
            else:
                loads_wye += 1
                loads_conn.append('wye')
                if len(dss.cktelement_node_order()) == 2:
                    loads_1 += 1
                    loads_name_list.append(dss.loads_read_name())
                    num_phases.append(dss.cktelement_num_phases())
                    from_bus_list.append(dss.cktelement_read_bus_names()[0][:-2])
                    loads_model.append(dss.loads_read_model())
                    loads_bus.append(dss.cktelement_read_bus_names()[0])
                    loads_1ph_list.append(dss.lines_read_name())
                    if dss.cktelement_node_order()[0] == 1:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(0)
                        P1.append(dss.cktelement_powers()[0])
                        Q1.append(dss.cktelement_powers()[1])
                        P2.append(0)
                        Q2.append(0)
                        P3.append(0)
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 2:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(0)
                        P1.append(0);
                        Q1.append(0)
                        P2.append(dss.cktelement_powers()[0])
                        Q2.append(dss.cktelement_powers()[1])
                        P3.append(0);
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 3:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(1)
                        P1.append(0);
                        Q1.append(0)
                        P2.append(0);
                        Q2.append(0)
                        P3.append(dss.cktelement_powers()[0])
                        Q3.append(dss.cktelement_powers()[1])

                elif len(dss.cktelement_node_order()) == 3:
                    loads_2 += 1
                    loads_name_list.append(dss.loads_read_name())
                    num_phases.append(dss.cktelement_num_phases())
                    from_bus_list.append(dss.cktelement_read_bus_names()[0][:-4])
                    loads_model.append(dss.loads_read_model())
                    loads_bus.append(dss.cktelement_read_bus_names()[0])
                    loads_2ph_list.append(dss.lines_read_name())
                    if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(0)
                        P1.append(dss.cktelement_powers()[0])
                        Q1.append(dss.cktelement_powers()[1])
                        P2.append(dss.cktelement_powers()[2])
                        Q2.append(dss.cktelement_powers()[3])
                        P3.append(0);
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(1)
                        P1.append(dss.cktelement_powers()[0])
                        Q1.append(dss.cktelement_powers()[1])
                        P2.append(0);
                        Q2.append(0)
                        P3.append(dss.cktelement_powers()[2])
                        Q3.append(dss.cktelement_powers()[3])

                    elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(0)
                        P2.append(dss.cktelement_powers()[0])
                        Q2.append(dss.cktelement_powers()[1])
                        P1.append(dss.cktelement_powers()[2])
                        Q1.append(dss.cktelement_powers()[3])
                        P3.append(0);
                        Q3.append(0)

                    elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(1)
                        P2.append(dss.cktelement_powers()[0])
                        Q2.append(dss.cktelement_powers()[1])
                        P3.append(dss.cktelement_powers()[2])
                        Q3.append(dss.cktelement_powers()[3])
                        P1.append(0);
                        Q1.append(0)

                    elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                        loads_terminal1_list.append(1)
                        loads_terminal2_list.append(0)
                        loads_terminal3_list.append(1)
                        P3.append(dss.cktelement_powers()[0])
                        Q3.append(dss.cktelement_powers()[1])
                        P1.append(dss.cktelement_powers()[2])
                        Q1.append(dss.cktelement_powers()[3])
                        P2.append(0);
                        Q2.append(0)

                    elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                        loads_terminal1_list.append(0)
                        loads_terminal2_list.append(1)
                        loads_terminal3_list.append(1)
                        P3.append(dss.cktelement_powers()[0])
                        Q3.append(dss.cktelement_powers()[1])
                        P2.append(dss.cktelement_powers()[2])
                        Q2.append(dss.cktelement_powers()[3])
                        P1.append(0);
                        Q1.append(0)

                elif len(dss.cktelement_node_order()) == 4:
                    loads_3 += 1
                    loads_name_list.append(dss.loads_read_name())
                    num_phases.append(dss.cktelement_num_phases())
                    from_bus_list.append(dss.cktelement_read_bus_names()[0][:-6])
                    loads_model.append(dss.loads_read_model())
                    loads_bus.append(dss.cktelement_read_bus_names()[0])
                    loads_3ph_list.append(dss.lines_read_name())
                    loads_terminal1_list.append(1)
                    loads_terminal2_list.append(1)
                    loads_terminal3_list.append(1)
                    P1.append(dss.cktelement_powers()[0])
                    Q1.append(dss.cktelement_powers()[1])
                    P2.append(dss.cktelement_powers()[2])
                    Q2.append(dss.cktelement_powers()[3])
                    P3.append(dss.cktelement_powers()[4])
                    Q3.append(dss.cktelement_powers()[5])

            dss.loads_next()

        loads_PQi_list = list(zip(loads_name_list, loads_conn, loads_model, num_phases, from_bus_list, loads_bus,
                                  loads_terminal1_list, loads_terminal2_list, loads_terminal3_list,
                                  P1, Q1, P2, Q2, P3, Q3))

        DF_loads_PQi = pd.DataFrame(loads_PQi_list,
                                    columns=['loads_name', 'loads_conn', 'loads_model', 'num_phases', 'from_bus',
                                             'loads_bus', \
                                             'phase_1', 'phase_2', 'phase_3',
                                             'P1(kW)', 'Q1(kvar)', 'P2(kW)', 'Q2(kvar)', 'P3(kW)', 'Q3(kvar)'])

        return DF_loads_PQi

    def DataFrame_loads_kW_kVAr(self):
        num_loads = dss.loads_count()
        dss.loads_first()
        name_load, node_load, read_kw, read_kvar = list(), list(), list(), list()
        for ii in range(num_loads):
            name_load.append(dss.loads_read_name())
            node_load.append(dss.cktelement_read_bus_names()[0][:-2])
            read_kw.append(dss.loads_read_kw())
            read_kvar.append(dss.loads_read_kvar())
            dss.loads_next()

        load_list = list(zip(name_load, node_load, read_kw, read_kvar))
        DF_loads = pd.DataFrame(load_list, columns=['name', 'node', 'kW', 'kVAR'])

        return DF_loads

    def element_powers_PQij(self, element: List[str]) -> pd.DataFrame:
        """
        Obtains from OpenDSS the active and reactive powers according to list(element) in a dataFrame with the following
        columns: ['element_name', 'num_phases', 'num_cond', 'conn', 'from_bus', 'to_bus', 'bus1', 'bus2', 'phase_1',
        'phase_2', 'phase_3', 'P1(kW)', 'Q1(kvar)', 'P2(kW)', 'Q2(kvar)', 'P3(kW)', 'Q3(kvar)']

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :param element: list['vsources', 'transformers', 'lines', 'loads', 'capacitors']
        :return: DF_element_PQ
        """
        element_name_list = list()
        num_cond_list = list()
        num_phases_list = list()
        conn_list = list()
        from_bus_list = list()
        to_bus_list = list()
        element_bus1_list = list()
        element_bus2_list = list()
        element_terminal1_list = list()
        element_terminal2_list = list()
        element_terminal3_list = list()
        P1, P2, P3 = list(), list(), list()
        Q1, Q2, Q3 = list(), list(), list()

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
                    if dss.loads_read_is_delta() == 1:
                        conn = 'delta'
                    else:
                        conn = 'wye'
                else:
                    bus2 = dss.cktelement_read_bus_names()[1]
                    conn = ''

                num_cond, node_order, bus1, bus2 = dss.cktelement_num_conductors(), dss.cktelement_node_order(), \
                                                   dss.cktelement_read_bus_names()[0], bus2
                from_bus, to_bus = from_to_bus(ii, num_cond, node_order, bus1, bus2)
                element_name_list.append(dss.cktelement_name())
                num_cond_list.append(num_cond)
                num_phases_list.append(dss.cktelement_num_phases())
                element_bus1_list.append(bus1)
                element_bus2_list.append(bus2)
                from_bus_list.append(from_bus)
                to_bus_list.append(to_bus)
                conn_list.append(conn)

                if ii == 'loads':
                    if conn == 'delta':
                        if len(dss.cktelement_node_order()) == 1:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(0);
                                Q2.append(0)
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(0);
                                Q2.append(0)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])

                        elif len(dss.cktelement_node_order()) == 2:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(dss.cktelement_powers()[2]);
                                Q2.append(dss.cktelement_powers()[3])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(0);
                                Q2.append(0)
                                P3.append(dss.cktelement_powers()[2]);
                                Q3.append(dss.cktelement_powers()[3])

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[2]);
                                Q1.append(dss.cktelement_powers()[3])
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(dss.cktelement_powers()[2]);
                                Q3.append(dss.cktelement_powers()[3])


                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])
                                P1.append(dss.cktelement_powers()[2]);
                                Q1.append(dss.cktelement_powers()[3])
                                P2.append(0);
                                Q2.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])
                                P2.append(dss.cktelement_powers()[2]);
                                Q2.append(dss.cktelement_powers()[3])
                                P1.append(0);
                                Q1.append(0)

                        elif len(dss.cktelement_node_order()) == 3:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            P1.append(dss.cktelement_powers()[0])
                            Q1.append(dss.cktelement_powers()[1])
                            P2.append(dss.cktelement_powers()[2])
                            Q2.append(dss.cktelement_powers()[3])
                            P3.append(dss.cktelement_powers()[4])
                            Q3.append(dss.cktelement_powers()[5])

                    elif conn == 'wye':

                        if len(dss.cktelement_node_order()) == 2:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(0);
                                Q2.append(0)
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(0);
                                Q2.append(0)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])

                        elif len(dss.cktelement_node_order()) == 3:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(dss.cktelement_powers()[2]);
                                Q2.append(dss.cktelement_powers()[3])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(0);
                                Q2.append(0)
                                P3.append(dss.cktelement_powers()[2]);
                                Q3.append(dss.cktelement_powers()[3])

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P1.append(dss.cktelement_powers()[2]);
                                Q1.append(dss.cktelement_powers()[3])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(dss.cktelement_powers()[2]);
                                Q3.append(dss.cktelement_powers()[3])
                                P1.append(0);
                                Q1.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])
                                P1.append(dss.cktelement_powers()[2]);
                                Q1.append(dss.cktelement_powers()[3])
                                P2.append(0);
                                Q2.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])
                                P2.append(dss.cktelement_powers()[2]);
                                Q2.append(dss.cktelement_powers()[3])
                                P1.append(0);
                                Q1.append(0)

                        elif len(dss.cktelement_node_order()) == 4:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            P1.append(dss.cktelement_powers()[0]);
                            Q1.append(dss.cktelement_powers()[1])
                            P2.append(dss.cktelement_powers()[2]);
                            Q2.append(dss.cktelement_powers()[3])
                            P3.append(dss.cktelement_powers()[4]);
                            Q3.append(dss.cktelement_powers()[5])


                else:
                    if conn == '':
                        if dss.cktelement_num_phases() == 1:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(0);
                                Q2.append(0)
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(0);
                                Q2.append(0)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])

                        elif dss.cktelement_num_phases() == 2:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(dss.cktelement_powers()[2]);
                                Q2.append(dss.cktelement_powers()[3])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P1.append(dss.cktelement_powers()[0]);
                                Q1.append(dss.cktelement_powers()[1])
                                P2.append(0);
                                Q2.append(0)
                                P3.append(dss.cktelement_powers()[2]);
                                Q3.append(dss.cktelement_powers()[3])

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                P1.append(dss.cktelement_powers()[2]);
                                Q1.append(dss.cktelement_powers()[3])
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(0);
                                Q3.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                P1.append(0);
                                Q1.append(0)
                                P2.append(dss.cktelement_powers()[0]);
                                Q2.append(dss.cktelement_powers()[1])
                                P3.append(dss.cktelement_powers()[2]);
                                Q3.append(dss.cktelement_powers()[3])


                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])
                                P1.append(dss.cktelement_powers()[2]);
                                Q1.append(dss.cktelement_powers()[3])
                                P2.append(0);
                                Q2.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                P3.append(dss.cktelement_powers()[0]);
                                Q3.append(dss.cktelement_powers()[1])
                                P2.append(dss.cktelement_powers()[2]);
                                Q2.append(dss.cktelement_powers()[3])
                                P1.append(0);
                                Q1.append(0)

                        elif dss.cktelement_num_phases() == 3:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            P1.append(dss.cktelement_powers()[0])
                            Q1.append(dss.cktelement_powers()[1])
                            P2.append(dss.cktelement_powers()[2])
                            Q2.append(dss.cktelement_powers()[3])
                            P3.append(dss.cktelement_powers()[4])
                            Q3.append(dss.cktelement_powers()[5])

                        elif dss.cktelement_num_phases() == 4:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            P1.append(dss.cktelement_powers()[0])
                            Q1.append(dss.cktelement_powers()[1])
                            P2.append(dss.cktelement_powers()[2])
                            Q2.append(dss.cktelement_powers()[3])
                            P3.append(dss.cktelement_powers()[4])
                            Q3.append(dss.cktelement_powers()[5])

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

        element_PQ_list = list(
            zip(element_name_list, num_phases_list, num_cond_list, conn_list, from_bus_list, to_bus_list,
                element_bus1_list, element_bus2_list, element_terminal1_list, element_terminal2_list,
                element_terminal3_list,
                P1, Q1, P2, Q2, P3, Q3))

        DF_element_PQ = pd.DataFrame(element_PQ_list,
                                     columns=['element_name', 'num_ph', 'num_cond', 'conn', 'from_bus', 'to_bus',
                                              'bus1', 'bus2', 'ph_1', 'ph_2', 'ph_3',
                                              'P1(kW)', 'Q1(kvar)', 'P2(kW)', 'Q2(kvar)', 'P3(kW)', 'Q3(kvar)'])

        return DF_element_PQ

    def element_currents_Iij_Ang(self, element: List[str]) -> pd.DataFrame:
        """
        Gets from OpenDSS the | I | and angle according to list(element) in a dataFrame with the following columns:
        'element_name', 'num_phases', 'num_cond', 'conn', 'from_bus', 'to_bus', 'bus1', 'bus2', 'phase_1', 'phase_2',
        'phase_3', 'I1(A)', 'ang1(deg)', 'I2(A)', 'ang2(deg)', 'I3(A)', 'ang3(deg)'

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :param element: list['vsources', 'transformers', 'lines', 'loads', 'capacitors']
        :return: DF_element_I_ang
        """
        element_name_list = list()
        num_cond_list = list()
        num_phases_list = list()
        conn_list = list()
        from_bus_list = list()
        to_bus_list = list()
        element_bus1_list = list()
        element_bus2_list = list()
        element_terminal1_list = list()
        element_terminal2_list = list()
        element_terminal3_list = list()
        I_1, I_2, I_3 = list(), list(), list()
        ang1, ang2, ang3 = list(), list(), list()

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
                    if dss.loads_read_is_delta() == 1:
                        conn = 'delta'
                    else:
                        conn = 'wye'
                else:
                    bus2 = dss.cktelement_read_bus_names()[1]
                    conn = ''

                num_cond, node_order, bus1, bus2 = dss.cktelement_num_conductors(), dss.cktelement_node_order(), \
                                                   dss.cktelement_read_bus_names()[0], bus2
                from_bus, to_bus = from_to_bus(ii, num_cond, node_order, bus1, bus2)
                element_name_list.append(dss.cktelement_name())
                num_cond_list.append(num_cond)
                num_phases_list.append(dss.cktelement_num_phases())
                element_bus1_list.append(bus1)
                element_bus2_list.append(bus2)
                from_bus_list.append(from_bus)
                to_bus_list.append(to_bus)
                conn_list.append(conn)

                if ii == 'loads':
                    if conn == 'delta':
                        if len(dss.cktelement_node_order()) == 1:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])

                        elif len(dss.cktelement_node_order()) == 2:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(dss.cktelement_currents_mag_ang()[2]);
                                ang2.append(dss.cktelement_currents_mag_ang()[3])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(dss.cktelement_currents_mag_ang()[2]);
                                ang3.append(dss.cktelement_currents_mag_ang()[3])

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[2]);
                                ang1.append(dss.cktelement_currents_mag_ang()[3])
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(dss.cktelement_currents_mag_ang()[2]);
                                ang3.append(dss.cktelement_currents_mag_ang()[3])


                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])
                                I_1.append(dss.cktelement_currents_mag_ang()[2]);
                                ang1.append(dss.cktelement_currents_mag_ang()[3])
                                I_2.append(0);
                                ang2.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(dss.cktelement_currents_mag_ang()[2]);
                                ang2.append(dss.cktelement_currents_mag_ang()[3])
                                I_1.append(0);
                                ang1.append(0)

                        elif len(dss.cktelement_node_order()) == 3:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            I_1.append(dss.cktelement_currents_mag_ang()[0])
                            ang1.append(dss.cktelement_currents_mag_ang()[1])
                            I_2.append(dss.cktelement_currents_mag_ang()[2])
                            ang2.append(dss.cktelement_currents_mag_ang()[3])
                            I_3.append(dss.cktelement_currents_mag_ang()[4])
                            ang3.append(dss.cktelement_currents_mag_ang()[5])

                    elif conn == 'wye':

                        if len(dss.cktelement_node_order()) == 2:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])

                        elif len(dss.cktelement_node_order()) == 3:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(dss.cktelement_currents_mag_ang()[2]);
                                ang2.append(dss.cktelement_currents_mag_ang()[3])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(dss.cktelement_currents_mag_ang()[2]);
                                ang3.append(dss.cktelement_currents_mag_ang()[3])

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_1.append(dss.cktelement_currents_mag_ang()[2]);
                                ang1.append(dss.cktelement_currents_mag_ang()[3])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(dss.cktelement_currents_mag_ang()[2]);
                                ang3.append(dss.cktelement_currents_mag_ang()[3])
                                I_1.append(0);
                                ang1.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])
                                I_1.append(dss.cktelement_currents_mag_ang()[2]);
                                ang1.append(dss.cktelement_currents_mag_ang()[3])
                                I_2.append(0);
                                ang2.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(dss.cktelement_currents_mag_ang()[2]);
                                ang2.append(dss.cktelement_currents_mag_ang()[3])
                                I_1.append(0);
                                ang1.append(0)

                        elif len(dss.cktelement_node_order()) == 4:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            I_1.append(dss.cktelement_currents_mag_ang()[0]);
                            ang1.append(dss.cktelement_currents_mag_ang()[1])
                            I_2.append(dss.cktelement_currents_mag_ang()[2]);
                            ang2.append(dss.cktelement_currents_mag_ang()[3])
                            I_3.append(dss.cktelement_currents_mag_ang()[4]);
                            ang3.append(dss.cktelement_currents_mag_ang()[5])

                else:
                    if conn == '':
                        if dss.cktelement_num_phases() == 1:
                            if dss.cktelement_node_order()[0] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])

                        elif dss.cktelement_num_phases() == 2:
                            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(dss.cktelement_currents_mag_ang()[2]);
                                ang2.append(dss.cktelement_currents_mag_ang()[3])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_1.append(dss.cktelement_currents_mag_ang()[0]);
                                ang1.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(0);
                                ang2.append(0)
                                I_3.append(dss.cktelement_currents_mag_ang()[2]);
                                ang3.append(dss.cktelement_currents_mag_ang()[3])

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(0)
                                I_1.append(dss.cktelement_currents_mag_ang()[2]);
                                ang1.append(dss.cktelement_currents_mag_ang()[3])
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(0);
                                ang3.append(0)

                            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                I_1.append(0);
                                ang1.append(0)
                                I_2.append(dss.cktelement_currents_mag_ang()[0]);
                                ang2.append(dss.cktelement_currents_mag_ang()[1])
                                I_3.append(dss.cktelement_currents_mag_ang()[2]);
                                ang3.append(dss.cktelement_currents_mag_ang()[3])


                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                                element_terminal1_list.append(1)
                                element_terminal2_list.append(0)
                                element_terminal3_list.append(1)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])
                                I_1.append(dss.cktelement_currents_mag_ang()[2]);
                                ang1.append(dss.cktelement_currents_mag_ang()[3])
                                I_2.append(0);
                                ang2.append(0)

                            elif dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                                element_terminal1_list.append(0)
                                element_terminal2_list.append(1)
                                element_terminal3_list.append(1)
                                I_3.append(dss.cktelement_currents_mag_ang()[0]);
                                ang3.append(dss.cktelement_currents_mag_ang()[1])
                                I_2.append(dss.cktelement_currents_mag_ang()[2]);
                                ang2.append(dss.cktelement_currents_mag_ang()[3])
                                I_1.append(0);
                                ang1.append(0)

                        elif dss.cktelement_num_phases() == 3:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            I_1.append(dss.cktelement_currents_mag_ang()[0])
                            ang1.append(dss.cktelement_currents_mag_ang()[1])
                            I_2.append(dss.cktelement_currents_mag_ang()[2])
                            ang2.append(dss.cktelement_currents_mag_ang()[3])
                            I_3.append(dss.cktelement_currents_mag_ang()[4])
                            ang3.append(dss.cktelement_currents_mag_ang()[5])

                        elif dss.cktelement_num_phases() == 4:
                            element_terminal1_list.append(1)
                            element_terminal2_list.append(1)
                            element_terminal3_list.append(1)
                            I_1.append(dss.cktelement_currents_mag_ang()[0])
                            ang1.append(dss.cktelement_currents_mag_ang()[1])
                            I_2.append(dss.cktelement_currents_mag_ang()[2])
                            ang2.append(dss.cktelement_currents_mag_ang()[3])
                            I_3.append(dss.cktelement_currents_mag_ang()[4])
                            ang3.append(dss.cktelement_currents_mag_ang()[5])

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

        element_I_ang_list = list(
            zip(element_name_list, num_phases_list, num_cond_list, conn_list, from_bus_list, to_bus_list,
                element_bus1_list, element_bus2_list, element_terminal1_list, element_terminal2_list,
                element_terminal3_list,
                I_1, ang1, I_2, ang2, I_3, ang3))

        DF_element_I_ang = pd.DataFrame(element_I_ang_list,
                                        columns=['element_name', 'num_ph', 'num_cond', 'conn', 'from_bus', 'to_bus',
                                                 'bus1', 'bus2', 'ph_1', 'ph_2', 'ph_3',
                                                 'I1(A)', 'ang1(deg)', 'I2(A)', 'ang2(deg)', 'I3(A)', 'ang3(deg)'])

        return DF_element_I_ang

    def initial_voltage_angle_option(self, option: str, file_path: str = None, sheet_name: str = None) -> pd.DataFrame:
        """
        Function to select between flat values or those obtained by OpenDSS

        :param option: Value in PU (flat, dss, file)
        :param file_path:
        :param sheet_name:
        :return: df_initial_values
        """

        dss.vsources_first()
        Vol_ref = float(dss.dssproperties_read_value('3'))
        Ang_ref = float(dss.dssproperties_read_value('4'))

        if option == 'flat':
            DF_allbusnames_aux = OpenDSS_data_collection.allbusnames_aux(dss)
            df_initial_values = OpenDSS_data_collection.Volt_Ang_node_no_PU(dss)

            for k in range(len(df_initial_values)):
                if df_initial_values['num_nodes'][k] == 1:
                    if df_initial_values['ph_1'][k] == 1 and df_initial_values['ph_2'][k] == 0 and \
                            df_initial_values['ph_3'][k] == 0:
                        df_initial_values.at[k, 'V1(kV)'] = Vol_ref
                        df_initial_values.at[k, 'V2(kV)'] = 0
                        df_initial_values.at[k, 'V3(kV)'] = 0
                        df_initial_values.at[k, 'Ang1(deg)'] = math.radians(Ang_ref)
                        df_initial_values.at[k, 'Ang2(deg)'] = math.radians(0)
                        df_initial_values.at[k, 'Ang3(deg)'] = math.radians(0)
                    elif df_initial_values['ph_1'][k] == 0 and df_initial_values['ph_2'][k] == 1 and \
                            df_initial_values['ph_3'][k] == 0:
                        df_initial_values.at[k, 'V1(kV)'] = 0
                        df_initial_values.at[k, 'V2(kV)'] = Vol_ref
                        df_initial_values.at[k, 'V3(kV)'] = 0
                        df_initial_values.at[k, 'Ang1(deg)'] = math.radians(0)
                        df_initial_values.at[k, 'Ang2(deg)'] = math.radians(Ang_ref - 120)
                        df_initial_values.at[k, 'Ang3(deg)'] = math.radians(0)
                    elif df_initial_values['ph_1'][k] == 0 and df_initial_values['ph_2'][k] == 0 and \
                            df_initial_values['ph_3'][k] == 1:
                        df_initial_values.at[k, 'V1(kV)'] = 0
                        df_initial_values.at[k, 'V2(kV)'] = 0
                        df_initial_values.at[k, 'V3(kV)'] = Vol_ref
                        df_initial_values.at[k, 'Ang1(deg)'] = math.radians(0)
                        df_initial_values.at[k, 'Ang2(deg)'] = math.radians(0)
                        df_initial_values.at[k, 'Ang3(deg)'] = math.radians(Ang_ref + 120)

                elif df_initial_values['num_nodes'][k] == 2:
                    if df_initial_values['ph_1'][k] == 1 and df_initial_values['ph_2'][k] == 1 and \
                            df_initial_values['ph_3'][k] == 0:
                        df_initial_values.at[k, 'V1(kV)'] = Vol_ref
                        df_initial_values.at[k, 'V2(kV)'] = Vol_ref
                        df_initial_values.at[k, 'V3(kV)'] = 0
                        df_initial_values.at[k, 'Ang1(deg)'] = math.radians(Ang_ref)
                        df_initial_values.at[k, 'Ang2(deg)'] = math.radians(Ang_ref - 120)
                        df_initial_values.at[k, 'Ang3(deg)'] = math.radians(0)
                    elif df_initial_values['ph_1'][k] == 1 and df_initial_values['ph_2'][k] == 0 and \
                            df_initial_values['ph_3'][k] == 1:
                        df_initial_values.at[k, 'V1(kV)'] = Vol_ref
                        df_initial_values.at[k, 'V2(kV)'] = 0
                        df_initial_values.at[k, 'V3(kV)'] = Vol_ref
                        df_initial_values.at[k, 'Ang1(deg)'] = math.radians(Ang_ref)
                        df_initial_values.at[k, 'Ang2(deg)'] = math.radians(0)
                        df_initial_values.at[k, 'Ang3(deg)'] = math.radians(Ang_ref + 120)
                    elif df_initial_values['ph_1'][k] == 0 and df_initial_values['ph_2'][k] == 1 and \
                            df_initial_values['ph_3'][k] == 1:
                        df_initial_values.at[k, 'V1(kV)'] = 0
                        df_initial_values.at[k, 'V2(kV)'] = Vol_ref
                        df_initial_values.at[k, 'V3(kV)'] = Vol_ref
                        df_initial_values.at[k, 'Ang1(deg)'] = math.radians(0)
                        df_initial_values.at[k, 'Ang2(deg)'] = math.radians(Ang_ref - 120)
                        df_initial_values.at[k, 'Ang3(deg)'] = math.radians(Ang_ref + 120)

                elif df_initial_values['num_nodes'][k] == 3:
                    df_initial_values.at[k, 'V1(kV)'] = Vol_ref
                    df_initial_values.at[k, 'V2(kV)'] = Vol_ref
                    df_initial_values.at[k, 'V3(kV)'] = Vol_ref
                    df_initial_values.at[k, 'Ang1(deg)'] = math.radians(Ang_ref)
                    df_initial_values.at[k, 'Ang2(deg)'] = math.radians(Ang_ref - 120)
                    df_initial_values.at[k, 'Ang3(deg)'] = math.radians(Ang_ref + 120)

            df_initial_values = pd.merge(
                df_initial_values, DF_allbusnames_aux, how='inner', left_on='bus_name', right_on='bus_name')

            df_initial_values = df_initial_values[
                ['bus_name', 'bus_name_aux', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
                 'V1(kV)', 'V2(kV)', 'V3(kV)', 'Ang1(deg)', 'Ang2(deg)', 'Ang3(deg)']]

            df_initial_values = df_initial_values.rename(
                columns={'bus_name_aux': 'Bus Nro.', 'V1(kV)': 'V1(pu)', 'V2(kV)': 'V2(pu)', 'V3(kV)': 'V3(pu)',
                         'Ang1(deg)': 'Ang1(rad)', 'Ang2(deg)': 'Ang2(rad)', 'Ang3(deg)': 'Ang3(rad)'})

            df_initial_values = df_initial_values[
                ['bus_name', 'Bus Nro.', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
                 'V1(pu)', 'V2(pu)', 'V3(pu)', 'Ang1(rad)', 'Ang2(rad)', 'Ang3(rad)']]

        elif option == 'dss':
            df_initial_values = OpenDSS_data_collection.Volt_Ang_auxDSS_PU(dss)
            for k in range(len(df_initial_values)):
                df_initial_values.at[k, 'Ang1(deg)'] = math.radians(df_initial_values.at[k, 'Ang1(deg)'])
                df_initial_values.at[k, 'Ang2(deg)'] = math.radians(df_initial_values.at[k, 'Ang2(deg)'])
                df_initial_values.at[k, 'Ang3(deg)'] = math.radians(df_initial_values.at[k, 'Ang3(deg)'])

            df_initial_values = df_initial_values.rename(
                columns={'Ang1(deg)': 'Ang1(rad)', 'Ang2(deg)': 'Ang2(rad)', 'Ang3(deg)': 'Ang3(rad)'})

        elif option == 'file':
            'Para prueba usaremos los valores obtenidos de openDSS'
            df_initial_values = pd.read_excel(io=file_path, sheet_name=sheet_name)
            for k in range(len(df_initial_values)):
                df_initial_values.at[k, 'Ang1(deg)'] = math.radians(df_initial_values.at[k, 'Ang1(deg)'])
                df_initial_values.at[k, 'Ang2(deg)'] = math.radians(df_initial_values.at[k, 'Ang2(deg)'])
                df_initial_values.at[k, 'Ang3(deg)'] = math.radians(df_initial_values.at[k, 'Ang3(deg)'])

            df_initial_values = df_initial_values.rename(
                columns={'Ang1(deg)': 'Ang1(rad)', 'Ang2(deg)': 'Ang2(rad)', 'Ang3(deg)': 'Ang3(rad)'})

        else:
            update_logg_file("Incorrect parameter entered\nSelect between 'flat' or 'dss'.", 4, log_py)
            exit()

        return df_initial_values

    def element_yprimitive(self, element: List[str]) -> pd.DataFrame:
        """
        Returns a Yprimitive dataFrame containing: ['Name', 'from_bus', 'to_bus', 'bus1', 'bus2', 'num_conductors',
        'num_phases', 'node_order', 'ph1', 'ph2', 'ph3', 'G11', 'B11', 'G22', 'B22', 'G33', 'B33', 'G12', 'B12', 'G23',
        'B23', 'G13', 'B13']

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :param element: list['vsources', 'transformers', 'lines', 'loads', 'capacitors']
        :return: DF_yprimitive
        """

        element_1, element_2, element_3, element_4 = 0, 0, 0, 0
        element_name_list = list()
        element_num_phases_list = list()
        element_num_conductors_list = list()
        element_node_order_list = list()
        element_bus1_list = list()
        element_bus2_list = list()
        from_bus_list = list()
        to_bus_list = list()

        from_bus1_list = list()
        to_bus1_list = list()

        element_ph1_list, element_ph2_list, element_ph3_list = list(), list(), list()
        G11_list, B11_list, G22_list, B22_list, G33_list, B33_list = list(), list(), list(), list(), list(), list()
        G12_list, B12_list, G23_list, B23_list, G13_list, B13_list = list(), list(), list(), list(), list(), list()

        for ii in element:
            if ii == 'transformers':
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
            elif ii == 'vsources':
                num_element = dss.vsources_count()
                dss.vsources_first()

            for num in range(num_element):

                element_ph1, element_ph2, element_ph3 = 0, 0, 0
                G11, B11, G22, B22, G33, B33 = 0, 0, 0, 0, 0, 0
                G12, B12, G23, B23, G13, B13 = 0, 0, 0, 0, 0, 0

                element_name_list.append(dss.cktelement_name())
                element_num_phases_list.append(dss.cktelement_num_phases())

                element_num_conductors_list.append(dss.cktelement_num_conductors())
                element_node_order_list.append(dss.cktelement_node_order())
                element_bus1_list.append(dss.cktelement_read_bus_names()[0])

                if ii == 'loads':
                    element_bus2_list.append('')
                    bus2 = ''
                else:
                    bus2 = dss.cktelement_read_bus_names()[1]
                    element_bus2_list.append(dss.cktelement_read_bus_names()[1])

                num_cond, node_order, bus1, bus2 = dss.cktelement_num_conductors(), dss.cktelement_node_order(), \
                                                   dss.cktelement_read_bus_names()[0], bus2
                from_bus, to_bus = from_to_bus(ii, num_cond, node_order, bus1, bus2)

                from_bus_list.append(from_bus)
                to_bus_list.append(to_bus)

                if dss.cktelement_num_phases() == 1:
                    element_1 += 1

                    n_Gii, n_Bii = 0, 1
                    if dss.cktelement_node_order()[0] == 1:
                        element_ph1, element_ph2, element_ph3 = 1, 0, 0
                        G11, B11, G22, B22, G33, B33 = dss.cktelement_y_prim()[n_Gii], dss.cktelement_y_prim()[
                            n_Bii], 0, 0, 0, 0
                        G12, B12, G23, B23, G13, B13 = 0, 0, 0, 0, 0, 0

                    elif dss.cktelement_node_order()[0] == 2:
                        element_ph1, element_ph2, element_ph3 = 0, 1, 0
                        G11, B11, G22, B22, G33, B33 = 0, 0, dss.cktelement_y_prim()[n_Gii], dss.cktelement_y_prim()[
                            n_Bii], 0, 0
                        G12, B12, G23, B23, G13, B13 = 0, 0, 0, 0, 0, 0

                    elif dss.cktelement_node_order()[0] == 3:
                        element_ph1, element_ph2, element_ph3 = 0, 0, 1
                        G11, B11, G22, B22, G33, B33 = 0, 0, 0, 0, dss.cktelement_y_prim()[n_Gii], dss.cktelement_y_prim()[
                            n_Bii]
                        G12, B12, G23, B23, G13, B13 = 0, 0, 0, 0, 0, 0

                elif dss.cktelement_num_phases() == 2:
                    element_2 += 1

                    n_Gii, n_Bii = 0, 1
                    n_Gjj, n_Bjj = 10, 11
                    n_Gij, n_Bij = 2, 3

                    if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2 or \
                            dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                        element_ph1, element_ph2, element_ph3 = 1, 1, 0
                        G11, B11, G22, B22, G33, B33 = dss.cktelement_y_prim()[n_Gii], dss.cktelement_y_prim()[n_Bii], \
                                                       dss.cktelement_y_prim()[n_Gjj], dss.cktelement_y_prim()[n_Bjj], 0, 0
                        G12, B12, G23, B23, G13, B13 = dss.cktelement_y_prim()[n_Gij], dss.cktelement_y_prim()[
                            n_Bij], 0, 0, 0, 0

                    elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3 or \
                            dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                        element_ph1, element_ph2, element_ph3 = 1, 0, 1
                        G11, B11, G22, B22, G33, B33 = dss.cktelement_y_prim()[n_Gii], dss.cktelement_y_prim()[n_Bii], 0, 0, \
                                                       dss.cktelement_y_prim()[n_Gjj], dss.cktelement_y_prim()[n_Bjj]
                        G12, B12, G23, B23, G13, B13 = 0, 0, 0, 0, dss.cktelement_y_prim()[n_Gij], dss.cktelement_y_prim()[
                            n_Bij]

                    elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3 or \
                            dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                        element_ph1, element_ph2, element_ph3 = 0, 1, 1
                        G11, B11, G22, B22, G33, B33 = 0, 0, dss.cktelement_y_prim()[n_Gii], dss.cktelement_y_prim()[n_Bii], \
                                                       dss.cktelement_y_prim()[n_Gjj], dss.cktelement_y_prim()[n_Bjj]
                        G12, B12, G23, B23, G13, B13 = 0, 0, dss.cktelement_y_prim()[n_Gij], dss.cktelement_y_prim()[
                            n_Bij], 0, 0

                elif dss.cktelement_num_phases() == 3:

                    if len(dss.cktelement_y_prim()) == 18:
                        # loads
                        nG11, nB11, nG22, nB22, nG33, nB33 = 0, 1, 8, 9, 16, 17
                        nG12, nB12, nG13, nB13, nG23, nB23 = 2, 3, 4, 5, 10, 11

                    elif len(dss.cktelement_y_prim()) == 72:
                        # line
                        nG11, nB11, nG22, nB22, nG33, nB33 = 0, 1, 14, 15, 28, 29
                        nG12, nB12, nG13, nB13, nG23, nB23 = 2, 3, 4, 5, 16, 17
                    else:
                        # element with neutral
                        nG11, nB11, nG22, nB22, nG33, nB33 = 0, 1, 18, 19, 36, 37
                        nG12, nB12, nG13, nB13, nG23, nB23 = 2, 3, 4, 5, 20, 21

                    element_3 += 1
                    element_ph1, element_ph2, element_ph3 = 1, 1, 1
                    G11, B11, G22, B22, G33, B33 = dss.cktelement_y_prim()[nG11], dss.cktelement_y_prim()[nB11], \
                                                   dss.cktelement_y_prim()[nG22], dss.cktelement_y_prim()[nB22], \
                                                   dss.cktelement_y_prim()[nG33], dss.cktelement_y_prim()[nB33]
                    G12, B12, G23, B23, G13, B13 = dss.cktelement_y_prim()[nG12], dss.cktelement_y_prim()[nB12], \
                                                   dss.cktelement_y_prim()[nG23], dss.cktelement_y_prim()[nB23], \
                                                   dss.cktelement_y_prim()[nG13], dss.cktelement_y_prim()[nB13]

                element_ph1_list.append(element_ph1);
                element_ph2_list.append(element_ph2);
                element_ph3_list.append(element_ph3)
                G11_list.append(G11);
                B11_list.append(B11);
                G22_list.append(G22);
                B22_list.append(B22);
                G33_list.append(G33);
                B33_list.append(B33)
                G12_list.append(G12);
                B12_list.append(B12);
                G23_list.append(G23);
                B23_list.append(B23);
                G13_list.append(G13);
                B13_list.append(B13)

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

        yprimitive_list = list(zip(element_name_list, from_bus_list, to_bus_list, element_bus1_list, element_bus2_list,
                                   element_num_conductors_list, element_num_phases_list,
                                   element_node_order_list, element_ph1_list, element_ph2_list, element_ph3_list,
                                   G11_list, B11_list, G22_list, B22_list, G33_list, B33_list,
                                   G12_list, B12_list, G23_list, B23_list, G13_list, B13_list))

        DF_yprimitive = pd.DataFrame(yprimitive_list,
                                     columns=['Name', 'from_bus', 'to_bus', 'bus1', 'bus2', 'num_conductors', 'num_phases',
                                              'node_order', 'ph1', 'ph2', 'ph3', 'G11', 'B11', 'G22', 'B22', 'G33', 'B33',
                                              'G12', 'B12', 'G23', 'B23', 'G13', 'B13'])

        return DF_yprimitive

class Values_per_unit:

    def __init__(self, SbasMVA_3ph: float):
        self.SbasMVA_3ph = SbasMVA_3ph

    def element_PQij_PU(self, df_element_power: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the output of the function element_powers_PQij to values per unit.

        :param SbasMVA_3ph: Circuit Base Power
        :param df_element_power: It comes from the function: element_powers_PQij
        :return: df_element_power
        """

        Sbas_1ph = (self.SbasMVA_3ph / 3)

        for k in range(len(df_element_power)):
            if df_element_power.at[k, 'from_bus'] != '' and df_element_power.at[k, 'to_bus'] == '':
                df_element_power.at[k, 'P1(kW)'] = ((df_element_power.at[k, 'P1(kW)']) * -1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'P2(kW)'] = ((df_element_power.at[k, 'P2(kW)']) * -1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'P3(kW)'] = ((df_element_power.at[k, 'P3(kW)']) * -1) / (Sbas_1ph * 1000)

                df_element_power.at[k, 'Q1(kvar)'] = ((df_element_power.at[k, 'Q1(kvar)']) * -1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'Q2(kvar)'] = ((df_element_power.at[k, 'Q2(kvar)']) * -1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'Q3(kvar)'] = ((df_element_power.at[k, 'Q3(kvar)']) * -1) / (Sbas_1ph * 1000)

            elif df_element_power.at[k, 'from_bus'] != '' and df_element_power.at[k, 'to_bus'] != '':
                df_element_power.at[k, 'P1(kW)'] = ((df_element_power.at[k, 'P1(kW)']) * 1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'P2(kW)'] = ((df_element_power.at[k, 'P2(kW)']) * 1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'P3(kW)'] = ((df_element_power.at[k, 'P3(kW)']) * 1) / (Sbas_1ph * 1000)

                df_element_power.at[k, 'Q1(kvar)'] = ((df_element_power.at[k, 'Q1(kvar)']) * 1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'Q2(kvar)'] = ((df_element_power.at[k, 'Q2(kvar)']) * 1) / (Sbas_1ph * 1000)
                df_element_power.at[k, 'Q3(kvar)'] = ((df_element_power.at[k, 'Q3(kvar)']) * 1) / (Sbas_1ph * 1000)

        df_element_power = df_element_power.rename(
            columns={'P1(kW)': 'P1(pu)', 'P2(kW)': 'P2(pu)', 'P3(kW)': 'P3(pu)',
                     'Q1(kvar)': 'Q1(pu)', 'Q2(kvar)': 'Q2(pu)', 'Q3(kvar)': 'Q3(pu)'})

        return df_element_power

    def element_Sij_PU(self, DF_element_PQij_PU: pd.DataFrame):

        DF_Aux = DF_element_PQij_PU[
            ['element_name', 'num_phases', 'num_cond', 'conn',
             'from_bus', 'to_bus',  'bus1', 'bus2',
             'phase_1', 'phase_2', 'phase_3']]

        DF_element_Sij_pu = pd.DataFrame()
        DF_element_Sij_pu['S1(pu)'] = ((DF_element_PQij_PU['P1(pu)'] ** 2) + (DF_element_PQij_PU['Q1(pu)'] ** 2)) ** 0.5
        DF_element_Sij_pu['S2(pu)'] = ((DF_element_PQij_PU['P2(pu)'] ** 2) + (DF_element_PQij_PU['Q2(pu)'] ** 2)) ** 0.5
        DF_element_Sij_pu['S3(pu)'] = ((DF_element_PQij_PU['P3(pu)'] ** 2) + (DF_element_PQij_PU['Q3(pu)'] ** 2)) ** 0.5

        DF_element_Sij_pu = pd.concat([DF_Aux, DF_element_Sij_pu], axis=1)

        return DF_element_Sij_pu

    def element_Iij_PU(self, df_element_currents: pd.DataFrame) -> pd.DataFrame:
        """
        Convert the output of the function element_currents_Iij_Ang to values per unit.

        :param dss: COM interface between OpenDSS and Python: Electrical Network
        :param SbasMVA_3ph: Circuit Base Power
        :param df_element_currents: It comes from the function: element_currents_Iij_Ang
        :return: df_element_currents
        """
        for k in range(len(df_element_currents)):
            dss.circuit_set_active_bus(df_element_currents['from_bus'][k])
            kVbase = dss.bus_kv_base()
            Ibas = ((self.SbasMVA_3ph / 3) * 1000) / kVbase

            if df_element_currents.at[k, 'from_bus'] != '' and df_element_currents.at[k, 'to_bus'] == '':
                df_element_currents.at[k, 'I1(A)'] = ((df_element_currents.at[k, 'I1(A)']) * -1) / (Ibas)
                df_element_currents.at[k, 'I2(A)'] = ((df_element_currents.at[k, 'I2(A)']) * -1) / (Ibas)
                df_element_currents.at[k, 'I3(A)'] = ((df_element_currents.at[k, 'I3(A)']) * -1) / (Ibas)

            elif df_element_currents.at[k, 'from_bus'] != '' and df_element_currents.at[k, 'to_bus'] != '':
                df_element_currents.at[k, 'I1(A)'] = ((df_element_currents.at[k, 'I1(A)']) * 1) / (Ibas)
                df_element_currents.at[k, 'I2(A)'] = ((df_element_currents.at[k, 'I2(A)']) * 1) / (Ibas)
                df_element_currents.at[k, 'I3(A)'] = ((df_element_currents.at[k, 'I3(A)']) * 1) / (Ibas)

        df_element_currents = df_element_currents.rename(
            columns={'I1(A)': 'I1(pu)', 'I2(A)': 'I2(pu)', 'I3(A)': 'I3(pu)'})

        return df_element_currents

    def DataFrame_normalization(self, df_allbusnames_aux: pd.DataFrame, df_voltage_angle: pd.DataFrame,
                                df_element_power: pd.DataFrame, df_element_currents: pd.DataFrame) -> pd.DataFrame:
        """
        With the DataFrame df_allbusnames_help combine with the rest of the DataFrame, so that they all handle the same notation

        :param df_allbusnames_aux: From -> allbusnames_aux(dss)
        :param df_voltage_angle: From -> Volt_Ang_node_PU(dss, Volt_Ang_node_no_PU(dss))
        :param df_element_power: From -> element_PQij_PU(SbasMVA_3ph, element_powers_PQij(dss, elements_openDSS))
        :param df_element_currents: From -> element_Iij_PU(dss, SbasMVA_3ph, element_currents_Iij_Ang(dss, elements_openDSS))
        :return: df_voltage_angle, df_element_PQij_PQi, df_element_Iij_Ii
        """

        dict_DF_normalization = dict()

        'bus voltage measurements'
        df_voltage_angle = pd.merge(df_voltage_angle, df_allbusnames_aux, how='inner', left_on='bus_name',
                                    right_on='bus_name')
        df_voltage_angle = df_voltage_angle[
            ['bus_name', 'bus_name_aux', 'num_nodes', 'phase_1', 'phase_2', 'phase_3', 'V1', 'V2',
             'V3', 'angle_bus1', 'angle_bus2', 'angle_bus3']]

        dict_DF_normalization['voltage_angle_pu'] = df_voltage_angle

        'Active and reactive power of OpenDSS elements'
        df_element_PQij = df_element_power
        df_element_PQij = pd.merge(df_element_PQij, df_allbusnames_aux, how='inner', left_on='from_bus',
                                   right_on='bus_name', suffixes=('_i', ''))
        df_element_PQij = pd.merge(df_element_PQij, df_allbusnames_aux, how='inner', left_on='to_bus',
                                   right_on='bus_name',
                                   suffixes=('_j', ''))
        df_element_PQij = df_element_PQij[['element_name', 'from_bus', 'to_bus', 'bus_name_aux_j', 'bus_name_aux',
                                           'num_phases', 'phase_1', 'phase_2', 'phase_3',
                                           'P1(pu)', 'Q1(pu)', 'P2(pu)', 'Q2(pu)', 'P3(pu)', 'Q3(pu)']]
        df_element_PQij = df_element_PQij.rename(
            columns={'bus_name_aux_j': 'from_bus_aux', 'bus_name_aux': 'to_bus_aux'})

        df_element_PQi = df_element_power
        df_mask = df_element_PQi['to_bus'] == ''
        filtered_df = df_element_PQi[df_mask]
        df_element_PQi = pd.merge(filtered_df, df_allbusnames_aux, how='inner', left_on='from_bus', right_on='bus_name')
        df_element_PQi = df_element_PQi.assign(bus_name_aux_j='')
        df_element_PQi = df_element_PQi[['element_name', 'from_bus', 'to_bus', 'bus_name_aux', 'bus_name_aux_j',
                                         'num_phases', 'phase_1', 'phase_2', 'phase_3',
                                         'P1(pu)', 'Q1(pu)', 'P2(pu)', 'Q2(pu)', 'P3(pu)', 'Q3(pu)']]
        df_element_PQi = df_element_PQi.rename(columns={'bus_name_aux': 'from_bus_aux', 'bus_name_aux_j': 'to_bus_aux'})
        df_element_PQij_PQi = pd.concat([df_element_PQij, df_element_PQi])

        dict_DF_normalization['element_power_pu'] = df_element_PQij_PQi

        'Iij-Ii'
        'OpenDSS line current and element injection'
        df_element_Iij = df_element_currents

        df_element_Iij = pd.merge(df_element_Iij, df_allbusnames_aux, how='inner', left_on='from_bus',
                                  right_on='bus_name',
                                  suffixes=('_i', ''))
        df_element_Iij = pd.merge(df_element_Iij, df_allbusnames_aux, how='inner', left_on='to_bus',
                                  right_on='bus_name',
                                  suffixes=('_j', ''))
        df_element_Iij = df_element_Iij[['element_name', 'from_bus', 'to_bus', 'bus_name_aux_j', 'bus_name_aux',
                                         'num_phases', 'phase_1', 'phase_2', 'phase_3',
                                         'I1(pu)', 'ang1(deg)', 'I2(pu)', 'ang2(deg)', 'I3(pu)', 'ang3(deg)']]
        df_element_Iij = df_element_Iij.rename(columns={'bus_name_aux_j': 'from_bus_aux', 'bus_name_aux': 'to_bus_aux'})

        df_element_Ii = df_element_currents
        df_mask = df_element_Ii['to_bus'] == ''
        filtered_df = df_element_Ii[df_mask]
        df_element_Ii = pd.merge(filtered_df, df_allbusnames_aux, how='inner', left_on='from_bus', right_on='bus_name')
        df_element_Ii = df_element_Ii.assign(bus_name_aux_j='')
        df_element_Ii = df_element_Ii[['element_name', 'from_bus', 'to_bus', 'bus_name_aux', 'bus_name_aux_j',
                                       'num_phases', 'phase_1', 'phase_2', 'phase_3',
                                       'I1(pu)', 'ang1(deg)', 'I2(pu)', 'ang2(deg)', 'I3(pu)', 'ang3(deg)']]
        df_element_Ii = df_element_Ii.rename(columns={'bus_name_aux': 'from_bus_aux', 'bus_name_aux_j': 'to_bus_aux'})
        df_element_Iij_Ii = pd.concat([df_element_Iij, df_element_Ii])

        dict_DF_normalization['element_current_pu'] = df_element_Iij_Ii

        return dict_DF_normalization

    def element_Yprimitive_pu(self, df_element_YPrim: pd.DataFrame) -> pd.DataFrame:

        SbasMVA_1ph = self.SbasMVA_3ph / 3
        DF_aux = df_element_YPrim.copy()
        for index, row in df_element_YPrim.iterrows():
            dss.circuit_set_active_bus(df_element_YPrim['from_bus'][index])
            kVbase = dss.bus_kv_base()
            Zbas = pow(kVbase, 2) / SbasMVA_1ph
            Ybas = 1 / Zbas
            list_G_B = ['G11', 'B11', 'G22', 'B22', 'G33', 'B33', 'G12', 'B12', 'G23', 'B23', 'G13', 'B13']
            for n in list_G_B:
                DF_aux[n][index] = df_element_YPrim[list_G_B][n][index] / Ybas

        return DF_aux

def all_sequence_element_powers(dss: str, element: List) -> pd.DataFrame:
    """
    Get all the sequence node currents in a dataframe with the following columns ['bus_name', 'num_nodes', 'I1(kV)', 'I2(kV)', 'V0(kV)', '%I2/I1', '%V0/I1']

    :param dss: COM interface between OpenDSS and Python: Electrical Network
    :return: DF_sequence_node_currents
    """

    element_name_list = list()
    element_num_term_list = list()
    P0_list, P1_list, P2_list = list(), list(), list()
    Q0_list, Q1_list, Q2_list = list(), list(), list()

    for ii in element:
        if ii == 'transformers':
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
        elif ii == 'vsources':
            num_element = dss.vsources_count()
            dss.vsources_first()

        for num in range(num_element):
            name = dss.cktelement_name()
            if dss.cktelement_num_terminals() == 1:
                element_name_list.append(dss.cktelement_name())
                element_num_term_list.append(1)
                P0_list.append(dss.cktelement_seq_powers()[0])
                Q0_list.append(dss.cktelement_seq_powers()[1])
                P1_list.append(dss.cktelement_seq_powers()[2])
                Q1_list.append(dss.cktelement_seq_powers()[3])
                P2_list.append(dss.cktelement_seq_powers()[4])
                Q2_list.append(dss.cktelement_seq_powers()[5])

            elif dss.cktelement_num_terminals() == 2:
                element_name_list.append(dss.cktelement_name())
                element_num_term_list.append(1)
                P0_list.append(dss.cktelement_seq_powers()[0])
                Q0_list.append(dss.cktelement_seq_powers()[1])
                P1_list.append(dss.cktelement_seq_powers()[2])
                Q1_list.append(dss.cktelement_seq_powers()[3])
                P2_list.append(dss.cktelement_seq_powers()[4])
                Q2_list.append(dss.cktelement_seq_powers()[5])

                element_name_list.append(dss.cktelement_name())
                element_num_term_list.append(2)
                P0_list.append(dss.cktelement_seq_powers()[7])
                Q0_list.append(dss.cktelement_seq_powers()[7])
                P1_list.append(dss.cktelement_seq_powers()[8])
                Q1_list.append(dss.cktelement_seq_powers()[9])
                P2_list.append(dss.cktelement_seq_powers()[10])
                Q2_list.append(dss.cktelement_seq_powers()[11])

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

    powers_seq_list = list(zip(element_name_list, element_num_term_list, P0_list, Q0_list, P1_list, Q1_list, P2_list, Q2_list))

    DF_sequence_elem_powers = pd.DataFrame(
        powers_seq_list, columns=['bus_name', ' Terminal', 'P0(kW)', 'P1(kW)', 'P2(kW)', 'Q0(kvar)', 'Q1(kvar)',  'Q2(kvar)'])

    #DF_sequence_elem_powers['S0(kVA)'] = ((DF_sequence_elem_powers['P0(kW)'] ** 2) + (DF_sequence_elem_powers['Q0(kvar)'] ** 2)) ** 0.5
    #DF_sequence_elem_powers['S1(kVA)'] = ((DF_sequence_elem_powers['P1(kW)'] ** 2) + (DF_sequence_elem_powers['Q1(kvar)'] ** 2)) ** 0.5
    #DF_sequence_elem_powers['S2(kVA)'] = ((DF_sequence_elem_powers['P2(kW)'] ** 2) + (DF_sequence_elem_powers['Q2(kvar)'] ** 2)) ** 0.5

    #DF_sequence_elem_powers['%S2/S1'] = (DF_sequence_elem_powers['S2(kVA)'] / DF_sequence_elem_powers['S1(kVA)']) * 100
    #DF_sequence_elem_powers['%S0/S1'] = (DF_sequence_elem_powers['S0(kVA)'] / DF_sequence_elem_powers['S1(kVA)']) * 100


    return DF_sequence_elem_powers

def element_sequence_impedance(dss: str, element: List) -> pd.DataFrame:
    """
    Returns a Yprimitive dataFrame containing: ['Name', 'from_bus', 'to_bus', 'bus1', 'bus2', 'num_conductors',
    'num_phases', 'node_order', 'ph1', 'ph2', 'ph3', 'G11', 'B11', 'G22', 'B22', 'G33', 'B33', 'G12', 'B12', 'G23',
    'B23', 'G13', 'B13']

    :param dss: COM interface between OpenDSS and Python: Electrical Network
    :param element: list['vsources', 'transformers', 'lines', 'loads', 'capacitors']
    :return: DF_yprimitive
    """

    element_1, element_2, element_3, element_4 = 0, 0, 0, 0
    element_name_list = list()
    element_num_phases_list = list()
    element_num_conductors_list = list()
    element_node_order_list = list()
    element_bus1_list = list()
    element_bus2_list = list()
    from_bus_list = list()
    to_bus_list = list()
    element_ph1_list, element_ph2_list, element_ph3_list = list(), list(), list()

    R1_list = list()
    X1_list = list()
    R0_list = list()
    X0_list = list()
    B1_list = list()
    B0_list = list()

    for ii in element:
        if ii == 'transformers':
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
        elif ii == 'vsources':
            num_element = dss.vsources_count()
            dss.vsources_first()

        for num in range(num_element):

            element_ph1, element_ph2, element_ph3 = 0, 0, 0
            R1, X1, R0, X0, B1, B0 = 0, 0, 0, 0, 0, 0

            element_name_list.append(dss.cktelement_name())
            element_num_phases_list.append(dss.cktelement_num_phases())

            element_num_conductors_list.append(dss.cktelement_num_conductors())
            element_node_order_list.append(dss.cktelement_node_order())
            element_bus1_list.append(dss.cktelement_read_bus_names()[0])

            if ii == 'loads':
                element_bus2_list.append('')
                bus2 = ''
            else:
                bus2 = dss.cktelement_read_bus_names()[1]
                element_bus2_list.append(dss.cktelement_read_bus_names()[1])

            num_cond, node_order, bus1, bus2 = dss.cktelement_num_conductors(), dss.cktelement_node_order(), \
                                               dss.cktelement_read_bus_names()[0], bus2
            from_bus, to_bus = from_to_bus(ii, num_cond, node_order, bus1, bus2)

            from_bus_list.append(from_bus)
            to_bus_list.append(to_bus)

            if ii == 'lines':
                R1 = dss.lines_read_r1()
                X1 = dss.lines_read_x1()
                R0 = dss.lines_read_r0()
                X0 = dss.lines_read_x0()
                B1 = dss.dssproperties_read_value('26')
                B0 = dss.dssproperties_read_value('27')

            if dss.cktelement_num_phases() == 1:
                element_1 += 1

                if dss.cktelement_node_order()[0] == 1:
                    element_ph1, element_ph2, element_ph3 = 1, 0, 0

                elif dss.cktelement_node_order()[0] == 2:
                    element_ph1, element_ph2, element_ph3 = 0, 1, 0


                elif dss.cktelement_node_order()[0] == 3:
                    element_ph1, element_ph2, element_ph3 = 0, 0, 1


            elif dss.cktelement_num_phases() == 2:
                element_2 += 1


                if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2 or \
                        dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                    element_ph1, element_ph2, element_ph3 = 1, 1, 0

                elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3 or \
                        dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                    element_ph1, element_ph2, element_ph3 = 1, 0, 1

                elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3 or \
                        dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                    element_ph1, element_ph2, element_ph3 = 0, 1, 1

            elif dss.cktelement_num_phases() == 3:
                element_3 += 1
                element_ph1, element_ph2, element_ph3 = 1, 1, 1


            element_ph1_list.append(element_ph1);
            element_ph2_list.append(element_ph2);
            element_ph3_list.append(element_ph3)
            R1_list.append(R1);
            X1_list.append(X1);
            R0_list.append(R0);
            X0_list.append(X0);
            B1_list.append(B1)
            B0_list.append(B0)

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

    z_sequence_list = list(zip(element_name_list, from_bus_list, to_bus_list, element_bus1_list, element_bus2_list,
                               element_num_conductors_list, element_num_phases_list,
                               element_node_order_list, element_ph1_list, element_ph2_list, element_ph3_list,
                               R1_list, X1_list, R0_list, X0_list, B1_list, B0_list))

    DF_z_sequence = pd.DataFrame(z_sequence_list,
                                 columns=['Name', 'from_bus', 'to_bus', 'bus1', 'bus2', 'num_conductors', 'num_phases',
                                          'node_order', 'ph1', 'ph2', 'ph3', 'R1', 'X1', 'R0', 'X0', 'B1', 'B0'])

    return DF_z_sequence

def voltage_angle_DSS(DF_allbusnames_aux: pd.DataFrame, DF_voltage_angle: pd.DataFrame) -> pd.DataFrame:

    #bus voltage measurements
    DF_voltage_angle = pd.merge(DF_voltage_angle, DF_allbusnames_aux, how='inner', left_on='bus_name',
                                right_on='bus_name')
    DF_voltage_angle = DF_voltage_angle[['bus_name', 'bus_name_aux', 'num_nodes', 'phase_1', 'phase_2', 'phase_3',
                                         'voltage_bus1', 'voltage_bus2', 'voltage_bus3',
                                         'angle_bus1', 'angle_bus2', 'angle_bus3']]

    DF_voltage_angle = DF_voltage_angle.rename(
        columns={'bus_name_aux': 'Bus Nro.', 'voltage_bus1': 'V_1', 'voltage_bus2': 'V_2', 'voltage_bus3': 'V_3',
                 'angle_bus1': 'Ang_1', 'angle_bus2': 'Ang_2', 'angle_bus3': 'Ang_3'})

    DF_voltage_angle = DF_voltage_angle[['bus_name', 'Bus Nro.', 'num_nodes', 'phase_1', 'phase_2', 'phase_3',
                                         'V_1', 'V_2', 'V_3', 'Ang_1', 'Ang_2', 'Ang_3']]

    return DF_voltage_angle

def lines_yprimite(dss: str) -> pd.DataFrame:
    line_name_list = list();
    num_phases = list()
    lines_3ph_list = list();
    lines_2ph_list = list();
    lines_1ph_list = list()
    line_bus1 = list();
    line_bus2 = list()
    G11, B11 = list(), list()
    G22, B22 = list(), list()
    G33, B33 = list(), list()
    G12, B12 = list(), list()
    G23, B23 = list(), list()
    G13, B13 = list(), list()
    lines_3 = 0;
    lines_2 = 0;
    lines_1 = 0

    from_bus_list = list()
    to_bus_list = list()
    line_terminal1_list = list()
    line_terminal2_list = list()
    line_terminal3_list = list()

    dss.lines_first()
    for lines in range(dss.lines_count()):
        if dss.lines_read_phases() == 1:
            lines_1 += 1
            line_name_list.append(dss.lines_read_name())
            line_bus1.append(dss.lines_read_bus1())
            line_bus2.append(dss.lines_read_bus2())
            num_phases.append(dss.lines_read_phases())
            lines_1ph_list.append(dss.lines_read_name())
            from_bus_list.append(dss.lines_read_bus1()[:-2])
            to_bus_list.append(dss.lines_read_bus2()[:-2])
            if dss.cktelement_node_order()[0] == 1:
                line_terminal1_list.append(1);
                line_terminal2_list.append(0);
                line_terminal3_list.append(0)
                G11.append(dss.lines_read_yprim()[0]);
                B11.append(dss.lines_read_yprim()[1])
                G22.append(0);
                B22.append(0)
                G33.append(0);
                B33.append(0)
                G12.append(0);
                B12.append(0)
                G23.append(0);
                B23.append(0)
                G13.append(0);
                B13.append(0)

            elif dss.cktelement_node_order()[0] == 2:
                line_terminal1_list.append(0)
                line_terminal2_list.append(1)
                line_terminal3_list.append(0)
                G11.append(0);
                B11.append(0)
                G22.append(dss.lines_read_yprim()[0]);
                B22.append(dss.lines_read_yprim()[1])
                G33.append(0);
                B33.append(0)
                G12.append(0);
                B12.append(0)
                G23.append(0);
                B23.append(0)
                G13.append(0);
                B13.append(0)
            elif dss.cktelement_node_order()[0] == 3:
                line_terminal1_list.append(0)
                line_terminal2_list.append(0)
                line_terminal3_list.append(1)
                G11.append(0);
                B11.append(0)
                G22.append(0);
                B22.append(0)
                G33.append(dss.lines_read_yprim()[0]);
                B33.append(dss.lines_read_yprim()[1])
                G12.append(0);
                B12.append(0)
                G23.append(0);
                B23.append(0)
                G13.append(0);
                B13.append(0)

        elif dss.lines_read_phases() == 2:
            lines_2 += 1
            line_name_list.append(dss.lines_read_name())
            line_bus1.append(dss.lines_read_bus1())
            line_bus2.append(dss.lines_read_bus2())
            num_phases.append(dss.lines_read_phases())
            lines_2ph_list.append(dss.lines_read_name())
            from_bus_list.append(dss.lines_read_bus1()[:-4])
            to_bus_list.append(dss.lines_read_bus2()[:-4])
            if dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 2 \
                    or dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 1:
                line_terminal1_list.append(1)
                line_terminal2_list.append(1)
                line_terminal3_list.append(0)
                G11.append(dss.lines_read_yprim()[0]);
                B11.append(dss.lines_read_yprim()[1])
                G22.append(dss.lines_read_yprim()[10]);
                B22.append(dss.lines_read_yprim()[11])
                G33.append(0);
                B33.append(0)
                G12.append(dss.lines_read_yprim()[2]);
                B12.append(dss.lines_read_yprim()[3])
                G23.append(0);
                B23.append(0)
                G13.append(0);
                B13.append(0)

            elif dss.cktelement_node_order()[0] == 1 and dss.cktelement_node_order()[1] == 3 or \
                    dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 1:
                line_terminal1_list.append(1)
                line_terminal2_list.append(0)
                line_terminal3_list.append(1)
                G11.append(dss.lines_read_yprim()[0]);
                B11.append(dss.lines_read_yprim()[1])
                G22.append(0);
                B22.append(0)
                G33.append(dss.lines_read_yprim()[10]);
                B33.append(dss.lines_read_yprim()[11])
                G12.append(0);
                B12.append(0)
                G23.append(0);
                B23.append(0)
                G13.append(dss.lines_read_yprim()[2]);
                B13.append(dss.lines_read_yprim()[3])

            elif dss.cktelement_node_order()[0] == 2 and dss.cktelement_node_order()[1] == 3 or \
                    dss.cktelement_node_order()[0] == 3 and dss.cktelement_node_order()[1] == 2:
                line_terminal1_list.append(0)
                line_terminal2_list.append(1)
                line_terminal3_list.append(1)
                G11.append(0);
                B11.append(0)
                G22.append(dss.lines_read_yprim()[0]);
                B22.append(dss.lines_read_yprim()[1])
                G33.append(dss.lines_read_yprim()[10]);
                B33.append(dss.lines_read_yprim()[11])
                G12.append(0);
                B12.append(0)
                G23.append(dss.lines_read_yprim()[2]);
                B23.append(dss.lines_read_yprim()[3])
                G13.append(0);
                B13.append(0)

        elif dss.lines_read_phases() == 3:

            lines_3 += 1
            line_name_list.append(dss.lines_read_name())
            line_bus1.append(dss.lines_read_bus1())
            line_bus2.append(dss.lines_read_bus2())
            num_phases.append(dss.lines_read_phases())
            lines_3ph_list.append(dss.lines_read_name())

            from_bus_list.append(dss.lines_read_bus1()[:-6])
            to_bus_list.append(dss.lines_read_bus2()[:-6])
            line_terminal1_list.append(1)
            line_terminal2_list.append(1)
            line_terminal3_list.append(1)

            G11.append(dss.lines_read_yprim()[0]);
            B11.append(dss.lines_read_yprim()[1])
            G22.append(dss.lines_read_yprim()[14]);
            B22.append(dss.lines_read_yprim()[15])
            G33.append(dss.lines_read_yprim()[28]);
            B33.append(dss.lines_read_yprim()[29])
            G12.append(dss.lines_read_yprim()[2]);
            B12.append(dss.lines_read_yprim()[3])
            G23.append(dss.lines_read_yprim()[16]);
            B23.append(dss.lines_read_yprim()[17])
            G13.append(dss.lines_read_yprim()[4]);
            B13.append(dss.lines_read_yprim()[5])

        dss.lines_next()

    lines_yprimite_list = list(zip(line_name_list, num_phases, from_bus_list, to_bus_list,
                                   line_bus1, line_bus2, line_terminal1_list, line_terminal2_list, line_terminal3_list,
                                   G11, B11, G22, B22, G33, B33,
                                   G12, B12, G23, B23, G13, B13))

    DF_lines_yprimite = pd.DataFrame(lines_yprimite_list,
                                     columns=['line_name', 'num_phases', 'from_bus', 'to_bus',
                                              'bus1', 'bus2', 'phase_1', 'phase_2', 'phase_3',
                                              'G11', 'B11', 'G22', 'B22', 'G33', 'B33',
                                              'G12', 'B12', 'G23', 'B23', 'G13', 'B13'])

    return DF_lines_yprimite

def from_to_bus(type_element, num_cond, node_order, bus1, bus2):
    if type_element == 'loads':
        if num_cond == 1:
            aux1 = bus1.find('.' + str(node_order[0]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]
            to_bus = ''
        elif num_cond == 2:
            aux1 = bus1.find('.' + str(node_order[0]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]
            to_bus = ''
        elif num_cond == 3:
            aux1 = bus1.find('.' + str(node_order[0]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]
            to_bus = ''
        elif num_cond == 4:
            aux1 = bus1.find('.' + str(node_order[0]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]
            to_bus = ''

    else:
        if num_cond == 1:
            aux1 = bus1.find('.' + str(node_order[0]))
            aux2 = bus2.find('.' + str(node_order[1]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]

            if aux2 == -1:
                to_bus = bus2
            else:
                to_bus = bus2[:aux2]
        elif num_cond == 2:
            aux1 = bus1.find('.' + str(node_order[0]))
            aux2 = bus2.find('.' + str(node_order[2]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]

            if aux2 == -1:
                to_bus = bus2
            else:
                to_bus = bus2[:aux2]

        elif num_cond == 3:
            aux1 = bus1.find('.' + str(node_order[0]))
            aux2 = bus2.find('.' + str(node_order[3]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]

            if aux2 == -1:
                to_bus = bus2
            else:
                to_bus = bus2[:aux2]
        elif num_cond == 4:
            aux1 = bus1.find('.' + str(node_order[0]))
            aux2 = bus2.find('.' + str(node_order[4]))
            if aux1 == -1:
                from_bus = bus1
            else:
                from_bus = bus1[:aux1]
            if aux2 == -1:
                to_bus = bus2
            else:
                to_bus = bus2[:aux2]

    return from_bus, to_bus


