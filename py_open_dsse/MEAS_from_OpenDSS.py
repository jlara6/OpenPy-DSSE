# -*- coding: utf-8 -*-
# @Time    : 28/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import numbers
import json
import numpy as np
import pandas as pd
from functools import reduce
from .OpenDSS_data_extraction import OpenDSS_data_collection, Values_per_unit, dss
from .error_handling_logging import update_logg_file, _excel_json, to_Excel_MEAS
from .base_DSSE import alg_mapping

# from Normalization_measurements import *
# dss = py_dss_interface.DSSDLL()
pd.options.mode.chained_assignment = None

data_DSS = OpenDSS_data_collection()

import logging

log_py = logging.getLogger(__name__)
orient, indent = "index", 1


class MEAS_files:
    """
    Class to generate files, which serve to model measurements of a distribution system.
    """

    def __init__(self, Sbas3ph_MVA):
        self.Sbas3ph_MVA = Sbas3ph_MVA

    def aux_generate_init_MEAS_files(self, DSS_file_address, MEAS_path):
        """
        Generate an initial file of measurements, place the names of nodes and elements that can be measured in an .xlsx file.

        :return: MEAS_file_format.xlsx
        """
        dss.text("ClearAll")
        dss.text(f"compile [{DSS_file_address}]")
        dss.solution_solve()

        df_Bus_i = data_DSS.Bus_name_nodes_conn_ph()
        df_Elem_ft = data_DSS.Elem_name_ncond_conn_fb_tb_ph(element=['lines', 'transformers'])

        df_Bus_i[['DS_Vm', 'STS_Vm', 'DS_PQd', 'STS_PQd(SM)', 'STS_PQd(0)', 'STS_PQd(Psd)']] = 0
        df_Elem_ft[['DS_PQft', 'STS_PQft', 'DS_Ift', 'STS_Ift']] = 0

        df_Bus_i_PMU = data_DSS.Bus_name_nodes_conn_ph()
        df_Elem_ft_PMU = data_DSS.Elem_name_ncond_conn_fb_tb_ph(element=['lines', 'transformers'])

        df_Bus_i_PMU[['DS_Vm', 'STS_Vm']] = 0
        df_Elem_ft_PMU[['DS_Ift', 'STS_Ift']] = 0

        'Create and export files with extension .JSON'

        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)

        if to_Excel_MEAS == True:
            dict_aux = dict()
            dict_aux['Bus_i'] = df_Bus_i
            dict_aux['Elem_ft'] = df_Elem_ft
            dict_aux['Bus_i_PMU'] = df_Bus_i_PMU
            dict_aux['Elem_ft_PMU'] = df_Elem_ft_PMU
            elem_name = ['Bus_i', 'Elem_ft', 'Bus_i_PMU', 'Elem_ft_PMU']

            try:
                writer = pd.ExcelWriter(f'{MEAS_path}\MEAS_file_format.xlsx')
                for name in elem_name:
                    dict_aux[name].to_excel(writer, sheet_name=name, index=False)
                writer.save()
                writer.close()
                update_logg_file(
                    f'The empty file with the possible measurements was created and saved in: \n{MEAS_path}\MEAS_file_format.xlsx',
                    1, log_py)
            except PermissionError:
                update_logg_file("Attention !! \nYou must close the MEAS_file_format.xlsx file and repeat the process.",
                                 4, log_py)
                exit()

    def aux_add_errors_MEAS_accord_PF_DSS(self, DSS_file_address: str, MEAS_path: str, seed_DS: int, nDP: int = 5):

        # _excel_json('MEAS_file_format', MEAS_path, 'init')
        'SCADA measurements'
        # df_Bus_i = pd.read_excel(f'{MEAS_init_address}', sheet_name='Bus_i')
        df_Bus_i = pd.read_json(f'{MEAS_path}\Init_Bus_i.json', orient=orient)
        if df_Bus_i['bus_name'].dtypes != str:
            df_Bus_i['bus_name'] = df_Bus_i['bus_name'].astype(str)
        df_Bus_i = df_Bus_i.assign(Rii_Vm=0, Rii_SM=0, Rii_0=0, Rii_Psd=0)

        # df_Elem_ft = pd.read_excel(f'{MEAS_init_address}', sheet_name='Elem_ft')
        df_Elem_ft = pd.read_json(f'{MEAS_path}\Init_Elem_ft.json', orient=orient)
        if df_Elem_ft['from_bus'].dtypes != str:
            df_Elem_ft['from_bus'] = df_Elem_ft['from_bus'].astype(str)
        if df_Elem_ft['to_bus'].dtypes != str:
            df_Elem_ft['to_bus'] = df_Elem_ft['to_bus'].astype(str)

        df_Elem_ft = df_Elem_ft.assign(Rii_PQft=0, Rii_Ift=0)
        dss.text(f'compile [{DSS_file_address}]')
        dss.solution_solve()

        Per_Unit = Values_per_unit(self.Sbas3ph_MVA)
        elem_DSS = ['lines', 'transformers']
        df_Vi_PU = data_DSS.Volt_Ang_node_PU()
        df_Vi_PU = df_Vi_PU.drop(['num_nodes', 'ph_1', 'ph_2', 'ph_3', 'Ang1(deg)', 'Ang3(deg)', 'Ang2(deg)'], axis=1)

        df_Elem_PQi_PU = Per_Unit.element_PQij_PU(data_DSS.element_powers_PQij(element=['loads', 'capacitors']))
        df_Elem_PQi_PU = df_Elem_PQi_PU.groupby('from_bus').agg(sum).reset_index()
        df_Elem_PQi_PU = df_Elem_PQi_PU.drop(['num_ph', 'num_cond', 'ph_1', 'ph_2', 'ph_3'], axis=1)
        df_Elem_PQi_PU = df_Elem_PQi_PU.rename(columns={'from_bus': 'bus_name'})

        dfs = [df_Bus_i, df_Vi_PU, df_Elem_PQi_PU]
        df_Bus_i = reduce(lambda left, right: pd.merge(left, right, on='bus_name'), dfs)

        df_Bus_i.loc[:, ['V1m(pu)', 'V2m(pu)', 'V3m(pu)']] = 0
        df_Bus_i.loc[:, ['P1md(pu)', 'P2md(pu)', 'P3md(pu)']] = 0
        df_Bus_i.loc[:, ['Q1md(pu)', 'Q2md(pu)', 'Q3md(pu)']] = 0

        df_Elem_PQft = Per_Unit.element_PQij_PU(data_DSS.element_powers_PQij(element=elem_DSS))
        df_Elem_PQft = df_Elem_PQft[['element_name', 'P1(pu)', 'P2(pu)', 'P3(pu)', 'Q1(pu)', 'Q2(pu)', 'Q3(pu)']]
        df_Elem_Ift = Per_Unit.element_Iij_PU(data_DSS.element_currents_Iij_Ang(element=elem_DSS))
        df_Elem_Ift = df_Elem_Ift[['element_name', 'I1(pu)', 'I2(pu)', 'I3(pu)']]

        df_ft = [df_Elem_ft, df_Elem_PQft, df_Elem_Ift]
        df_Elem_ft = reduce(lambda left, right: pd.merge(left, right, on='element_name'), df_ft)

        df_Elem_ft.loc[:, ['P1mft(pu)', 'P2mft(pu)', 'P3mft(pu)']] = 0
        df_Elem_ft.loc[:, ['Q1mft(pu)', 'Q2mft(pu)', 'Q3mft(pu)']] = 0
        df_Elem_ft.loc[:, ['I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)']] = 0

        # PMU measurements
        # df_Bus_i_PMU = pd.read_excel(f'{MEAS_init_address}', sheet_name='Bus_i_PMU')
        df_Bus_i_PMU = pd.read_json(f'{MEAS_path}\Init_Bus_i_PMU.json', orient=orient)
        df_Bus_i_PMU = df_Bus_i_PMU.assign(Rii_Vm=0)
        df_Bus_i_PMU.loc[:, ['V1m(pu)', 'V2m(pu)', 'V3m(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']] = 0

        df_Vi_PMU = data_DSS.Volt_Ang_node_PU()
        df_Vi_PMU = df_Vi_PMU.drop(['num_nodes', 'ph_1', 'ph_2', 'ph_3'], axis=1)

        # df_Elem_ft_PMU = pd.read_excel(f'{MEAS_init_address}', sheet_name='Elem_ft_PMU')
        df_Elem_ft_PMU = pd.read_json(f'{MEAS_path}\Init_Elem_ft_PMU.json', orient=orient)
        df_Elem_ft_PMU = df_Elem_ft_PMU.assign(Rii_Ift=0)
        df_Elem_ft_PMU.loc[:, ['I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']] = 0

        df_Elem_Ift_PU = Per_Unit.element_Iij_PU(data_DSS.element_currents_Iij_Ang(element=elem_DSS))
        df_Elem_Ift_PU = df_Elem_Ift_PU[
            ['element_name', 'I1(pu)', 'ang1(deg)', 'I2(pu)', 'ang2(deg)', 'I3(pu)', 'ang3(deg)']]

        nVi = df_Bus_i['STS_Vm'].sum()
        nPQi_SM = df_Bus_i['STS_PQd(SM)'].sum()
        nPQi_0 = df_Bus_i['STS_PQd(0)'].sum()
        nPQi_Psd = df_Bus_i['STS_PQd(Psd)'].sum()
        nPQft = df_Elem_ft['STS_PQft'].sum()
        nIft = df_Elem_ft['STS_Ift'].sum()
        nVi_PMU = df_Bus_i_PMU['STS_Vm'].sum()
        nIft_PMU = df_Elem_ft_PMU['STS_Ift'].sum()

        ntotal = nVi + nPQi_SM + nPQi_0 + nPQi_Psd + nPQft + nIft + nVi_PMU + nIft_PMU
        isInt = isinstance(ntotal, numbers.Integral)
        if isInt != True:
            update_logg_file('Error\nAttention: Check the meter statuses in the MEAS_file_format.xlsx file.', 5, log_py)
            exit()

        np.random.seed(seed_DS)
        Rii = np.random.normal(0, 1, size=(ntotal, 1))
        aux_Rii = 0
        if nVi != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_Vm'].isin([1])]
            error = Rii[aux_Rii:nVi]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Bus_i.loc[index, 'Rii_Vm'] = round(df_Bus_i['DS_Vm'][index] * error[aux][0], nDP)
                df_Bus_i.loc[index, 'V1m(pu)'] = round(
                    (df_Bus_i['V1(pu)'][index] * df_Bus_i['Rii_Vm'][index]) + df_Bus_i['V1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'V2m(pu)'] = round(
                    (df_Bus_i['V2(pu)'][index] * df_Bus_i['Rii_Vm'][index]) + df_Bus_i['V2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'V3m(pu)'] = round(
                    (df_Bus_i['V3(pu)'][index] * df_Bus_i['Rii_Vm'][index]) + df_Bus_i['V3(pu)'][index], nDP)
                aux += 1
            aux_Rii = aux_Rii + nVi
        if nPQi_SM != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(SM)'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nPQi_SM]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Bus_i.loc[index, 'Rii_SM'] = round(df_Bus_i['DS_PQd'][index] * error[aux][0], nDP)
                df_Bus_i.loc[index, 'P1md(pu)'] = round(
                    (df_Bus_i['P1(pu)'][index] * df_Bus_i['Rii_SM'][index]) + df_Bus_i['P1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'P2md(pu)'] = round(
                    (df_Bus_i['P2(pu)'][index] * df_Bus_i['Rii_SM'][index]) + df_Bus_i['P2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'P3md(pu)'] = round(
                    (df_Bus_i['P3(pu)'][index] * df_Bus_i['Rii_SM'][index]) + df_Bus_i['P3(pu)'][index], nDP)

                df_Bus_i.loc[index, 'Q1md(pu)'] = round(
                    (df_Bus_i['Q1(pu)'][index] * df_Bus_i['Rii_SM'][index]) + df_Bus_i['Q1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'Q2md(pu)'] = round(
                    (df_Bus_i['Q2(pu)'][index] * df_Bus_i['Rii_SM'][index]) + df_Bus_i['Q2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'Q3md(pu)'] = round(
                    (df_Bus_i['Q3(pu)'][index] * df_Bus_i['Rii_SM'][index]) + df_Bus_i['Q3(pu)'][index], nDP)
                aux += 1
            aux_Rii = aux_Rii + nPQi_SM
        if nPQi_0 != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(0)'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nPQi_0]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Bus_i.loc[index, 'Rii_0'] = round(df_Bus_i['DS_PQd'][index] * error[aux][0], nDP)
                df_Bus_i.loc[index, 'P1md(pu)'] = round((df_Bus_i['P1(pu)'][index] * df_Bus_i['Rii_0'][index]) + \
                                                        df_Bus_i['P1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'P2md(pu)'] = round((df_Bus_i['P2(pu)'][index] * df_Bus_i['Rii_0'][index]) + \
                                                        df_Bus_i['P2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'P3md(pu)'] = round((df_Bus_i['P3(pu)'][index] * df_Bus_i['Rii_0'][index]) + \
                                                        df_Bus_i['P3(pu)'][index], nDP)

                df_Bus_i.loc[index, 'Q1md(pu)'] = round((df_Bus_i['Q1(pu)'][index] * df_Bus_i['Rii_0'][index]) + \
                                                        df_Bus_i['Q1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'Q2md(pu)'] = round((df_Bus_i['Q2(pu)'][index] * df_Bus_i['Rii_0'][index]) + \
                                                        df_Bus_i['Q2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'Q3md(pu)'] = round((df_Bus_i['Q3(pu)'][index] * df_Bus_i['Rii_0'][index]) + \
                                                        df_Bus_i['Q3(pu)'][index], nDP)
                aux += 1
            aux_Rii = aux_Rii + nPQi_0
        if nPQi_Psd != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(Psd)'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nPQi_Psd]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Bus_i.loc[index, 'Rii_Psd'] = round(df_Bus_i['DS_PQd'][index] * error[aux][0], nDP)
                df_Bus_i.loc[index, 'P1md(pu)'] = round((df_Bus_i['P1(pu)'][index] * df_Bus_i['Rii_Psd'][index]) + \
                                                        df_Bus_i['P1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'P2md(pu)'] = round((df_Bus_i['P2(pu)'][index] * df_Bus_i['Rii_Psd'][index]) + \
                                                        df_Bus_i['P2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'P3md(pu)'] = round((df_Bus_i['P3(pu)'][index] * df_Bus_i['Rii_Psd'][index]) + \
                                                        df_Bus_i['P3(pu)'][index], nDP)

                df_Bus_i.loc[index, 'Q1md(pu)'] = round((df_Bus_i['Q1(pu)'][index] * df_Bus_i['Rii_Psd'][index]) + \
                                                        df_Bus_i['Q1(pu)'][index], nDP)
                df_Bus_i.loc[index, 'Q2md(pu)'] = round((df_Bus_i['Q2(pu)'][index] * df_Bus_i['Rii_Psd'][index]) + \
                                                        df_Bus_i['Q2(pu)'][index], nDP)
                df_Bus_i.loc[index, 'Q3md(pu)'] = round((df_Bus_i['Q3(pu)'][index] * df_Bus_i['Rii_Psd'][index]) + \
                                                        df_Bus_i['Q3(pu)'][index], nDP)
                aux += 1
            aux_Rii = aux_Rii + nPQi_Psd
        if nPQft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_PQft'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nPQft]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Elem_ft.loc[index, 'Rii_PQft'] = round(df_Elem_ft['DS_PQft'][index] * error[aux][0], nDP)
                df_Elem_ft.loc[index, 'P1mft(pu)'] = round(
                    (df_Elem_ft['P1(pu)'][index] * df_Elem_ft['Rii_PQft'][index]) + \
                    df_Elem_ft['P1(pu)'][index], nDP)
                df_Elem_ft.loc[index, 'P2mft(pu)'] = round(
                    (df_Elem_ft['P2(pu)'][index] * df_Elem_ft['Rii_PQft'][index]) + \
                    df_Elem_ft['P2(pu)'][index], nDP)
                df_Elem_ft.loc[index, 'P3mft(pu)'] = round(
                    (df_Elem_ft['P3(pu)'][index] * df_Elem_ft['Rii_PQft'][index]) + \
                    df_Elem_ft['P3(pu)'][index], nDP)

                df_Elem_ft.loc[index, 'Q1mft(pu)'] = round(
                    (df_Elem_ft['Q1(pu)'][index] * df_Elem_ft['Rii_PQft'][index]) + \
                    df_Elem_ft['Q1(pu)'][index], nDP)
                df_Elem_ft.loc[index, 'Q2mft(pu)'] = round(
                    (df_Elem_ft['Q2(pu)'][index] * df_Elem_ft['Rii_PQft'][index]) + \
                    df_Elem_ft['Q2(pu)'][index], nDP)
                df_Elem_ft.loc[index, 'Q3mft(pu)'] = round(
                    (df_Elem_ft['Q3(pu)'][index] * df_Elem_ft['Rii_PQft'][index]) + \
                    df_Elem_ft['Q3(pu)'][index], nDP)
                aux += 1

            aux_Rii = aux_Rii + nPQft
        if nIft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_Ift'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nIft]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Elem_ft.loc[index, 'Rii_Ift'] = round(df_Elem_ft['DS_Ift'][index] * error[aux][0], nDP)
                df_Elem_ft.loc[index, 'I1mft(pu)'] = round(
                    (df_Elem_ft['I1(pu)'][index] * df_Elem_ft['Rii_Ift'][index]) + df_Elem_ft['I1(pu)'][index], nDP)
                df_Elem_ft.loc[index, 'I2mft(pu)'] = round(
                    (df_Elem_ft['I2(pu)'][index] * df_Elem_ft['Rii_Ift'][index]) + df_Elem_ft['I2(pu)'][index], nDP)
                df_Elem_ft.loc[index, 'I3mft(pu)'] = round(
                    (df_Elem_ft['I3(pu)'][index] * df_Elem_ft['Rii_Ift'][index]) + df_Elem_ft['I3(pu)'][index], nDP)

            aux_Rii = aux_Rii + nIft
        if nVi_PMU != 0:
            df_aux = df_Bus_i_PMU[df_Bus_i_PMU['STS_Vm'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nVi_PMU]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Bus_i_PMU.loc[index, 'Rii_Vm'] = round(df_Bus_i_PMU['DS_Vm'][index] * error[aux][0], nDP)
                df_Bus_i_PMU.loc[index, 'V1m(pu)'] = round(
                    (df_Vi_PMU['V1(pu)'][index] * df_Bus_i_PMU['Rii_Vm'][index]) + df_Vi_PMU['V1(pu)'][index], nDP)
                df_Bus_i_PMU.loc[index, 'V2m(pu)'] = round(
                    (df_Vi_PMU['V2(pu)'][index] * df_Bus_i_PMU['Rii_Vm'][index]) + df_Vi_PMU['V2(pu)'][index], nDP)
                df_Bus_i_PMU.loc[index, 'V3m(pu)'] = round(
                    (df_Vi_PMU['V3(pu)'][index] * df_Bus_i_PMU['Rii_Vm'][index]) + df_Vi_PMU['V3(pu)'][index], nDP)

                df_Bus_i_PMU.loc[index, 'Ang1m(deg)'] = round(
                    (df_Vi_PMU['Ang1(deg)'][index] * df_Bus_i_PMU['Rii_Vm'][index]) + df_Vi_PMU['Ang1(deg)'][index],
                    nDP)
                df_Bus_i_PMU.loc[index, 'Ang2m(deg)'] = round(
                    (df_Vi_PMU['Ang2(deg)'][index] * df_Bus_i_PMU['Rii_Vm'][index]) + df_Vi_PMU['Ang2(deg)'][index],
                    nDP)
                df_Bus_i_PMU.loc[index, 'Ang3m(deg)'] = round(
                    (df_Vi_PMU['Ang3(deg)'][index] * df_Bus_i_PMU['Rii_Vm'][index]) + df_Vi_PMU['Ang3(deg)'][index],
                    nDP)
                aux += 1

            aux_Rii = aux_Rii + nVi_PMU
        if nIft_PMU != 0:
            df_aux = df_Elem_ft_PMU[df_Elem_ft_PMU['STS_Ift'].isin([1])]
            error = Rii[aux_Rii:aux_Rii + nIft_PMU]
            aux = 0
            for index, row in df_aux.iterrows():
                df_Elem_ft_PMU.loc[index, 'Rii_Ift'] = round(df_Elem_ft_PMU['DS_Ift'][index] * error[aux][0], nDP)
                df_Elem_ft_PMU.loc[index, 'I1mft(pu)'] = round(
                    (df_Elem_Ift_PU['I1(pu)'][index] * df_Elem_ft_PMU['Rii_Ift'][index])
                    + df_Elem_Ift_PU['I1(pu)'][index], nDP)
                df_Elem_ft_PMU.loc[index, 'I2mft(pu)'] = round(
                    (df_Elem_Ift_PU['I2(pu)'][index] * df_Elem_ft_PMU['Rii_Ift'][index])
                    + df_Elem_Ift_PU['I2(pu)'][index], nDP)
                df_Elem_ft_PMU.loc[index, 'I3mft(pu)'] = round(
                    (df_Elem_Ift_PU['I3(pu)'][index] * df_Elem_ft_PMU['Rii_Ift'][index])
                    + df_Elem_Ift_PU['I3(pu)'][index], nDP)

                df_Elem_ft_PMU.loc[index, 'Ang1m(deg)'] = round(
                    (df_Elem_Ift_PU['ang1(deg)'][index] * df_Elem_ft_PMU['Rii_Ift'][index])
                    + df_Elem_Ift_PU['ang1(deg)'][index], nDP)
                df_Elem_ft_PMU.loc[index, 'Ang2m(deg)'] = round(
                    (df_Elem_Ift_PU['ang2(deg)'][index] * df_Elem_ft_PMU['Rii_Ift'][index])
                    + df_Elem_Ift_PU['ang2(deg)'][index], nDP)
                df_Elem_ft_PMU.loc[index, 'Ang3m(deg)'] = round(
                    (df_Elem_Ift_PU['ang3(deg)'][index] * df_Elem_ft_PMU['Rii_Ift'][index])
                    + df_Elem_Ift_PU['ang3(deg)'][index], nDP)

            aux_Rii = aux_Rii + nIft_PMU

        df_Bus_i = df_Bus_i[
            ['bus_name', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
             'STS_Vm', 'Rii_Vm', 'V1m(pu)', 'V2m(pu)', 'V3m(pu)',
             'STS_PQd(SM)', 'Rii_SM', 'STS_PQd(0)', 'Rii_0', 'STS_PQd(Psd)', 'Rii_Psd',
             'P1md(pu)', 'P2md(pu)', 'P3md(pu)', 'Q1md(pu)', 'Q2md(pu)', 'Q3md(pu)']]

        df_Elem_ft = df_Elem_ft[
            ['element_name', 'num_ph', 'from_bus', 'to_bus', 'ph_1', 'ph_2', 'ph_3',
             'STS_PQft', 'Rii_PQft', 'P1mft(pu)', 'P2mft(pu)', 'P3mft(pu)', 'Q1mft(pu)', 'Q2mft(pu)', 'Q3mft(pu)',
             'STS_Ift', 'Rii_Ift', 'I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)']]

        df_Bus_i_PMU = df_Bus_i_PMU[
            ['bus_name', 'num_nodes', 'ph_1', 'ph_2', 'ph_3', 'STS_Vm', 'Rii_Vm',
             'V1m(pu)', 'V2m(pu)', 'V3m(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']]

        df_Elem_ft_PMU = df_Elem_ft_PMU[
            ['element_name', 'num_ph', 'from_bus', 'to_bus', 'ph_1', 'ph_2', 'ph_3', 'STS_Ift', 'Rii_Ift',
             'I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']]

        'Create and export files with extension .JSON'
        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)

        if to_Excel_MEAS == True:
            dict_aux = dict()
            dict_aux['Bus_i'] = df_Bus_i
            dict_aux['Elem_ft'] = df_Elem_ft
            dict_aux['Bus_i_PMU'] = df_Bus_i_PMU
            dict_aux['Elem_ft_PMU'] = df_Elem_ft_PMU
            elem_name = ['Bus_i', 'Elem_ft', 'Bus_i_PMU', 'Elem_ft_PMU']

            try:
                writer = pd.ExcelWriter(f'{MEAS_path}\MEAS_error_DSS.xlsx')
                for name in elem_name:
                    dict_aux[name].to_excel(writer, sheet_name=name, index=False)
                writer.save()
                writer.close()
                update_logg_file(f'The file: MEAS_error_DSS.xlsx, was saved in {MEAS_path}', 2, log_py)

            except PermissionError:
                update_logg_file("Attention !! \nYou must close the MEAS_error_DSS.xlsx file and repeat the process.",
                                 4, log_py)
                exit()

    def generate_init_MEAS_files(self, DSS_file_address, MEAS_path):
        """
        Generate an initial file of measurements, place the names of nodes and elements that can be measured in an .xlsx file.

        :return: MEAS_file_format.xlsx
        """
        dss.text("ClearAll")
        dss.text(f"compile [{DSS_file_address}]")
        dss.solution_solve()

        df_Bus_i = data_DSS.Bus_name_nodes_conn_ph()
        df_Elem_ft = data_DSS.Elem_name_ncond_conn_fb_tb_ph(element=['lines', 'transformers'])

        df_Bus_i[['Unc(%)_Vm', 'STS_Vm', 'Unc(%)_PQd', 'STS_PQd(SM)', 'STS_PQd(0)', 'STS_PQd(Psd)']] = 0
        df_Elem_ft[['Unc(%)_PQft', 'STS_PQft', 'Unc(%)_Ift', 'STS_Ift']] = 0

        df_Bus_i_PMU = data_DSS.Bus_name_nodes_conn_ph()
        df_Elem_ft_PMU = data_DSS.Elem_name_ncond_conn_fb_tb_ph(element=['lines', 'transformers'])

        df_Bus_i_PMU[['Unc(%)_Vm', 'STS_Vm']] = 0
        df_Elem_ft_PMU[['Unc(%)_Ift', 'STS_Ift']] = 0

        'Create and export files with extension .JSON'

        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\Init_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)

        if to_Excel_MEAS == True:
            dict_aux = dict()
            dict_aux['Bus_i'] = df_Bus_i
            dict_aux['Elem_ft'] = df_Elem_ft
            dict_aux['Bus_i_PMU'] = df_Bus_i_PMU
            dict_aux['Elem_ft_PMU'] = df_Elem_ft_PMU
            elem_name = ['Bus_i', 'Elem_ft', 'Bus_i_PMU', 'Elem_ft_PMU']

            try:
                writer = pd.ExcelWriter(f'{MEAS_path}\MEAS_file_format.xlsx')
                for name in elem_name:
                    dict_aux[name].to_excel(writer, sheet_name=name, index=False)
                writer.save()
                writer.close()
                update_logg_file(
                    f'The empty file with the possible measurements was created and saved in: \n{MEAS_path}\MEAS_file_format.xlsx',
                    1, log_py)
            except PermissionError:
                update_logg_file("Attention !! \nYou must close the MEAS_file_format.xlsx file and repeat the process.",
                                 4, log_py)
                exit()

    def add_errors_MEAS_accord_PF_DSS(self, DSS_file_address: str, MEAS_path: str, seed_DS: int, nDP: int = 5):

        #_excel_json('MEAS_file_format', MEAS_path, 'init')
        'SCADA measurements'
        # df_Bus_i = pd.read_excel(f'{MEAS_init_address}', sheet_name='Bus_i')
        df_Bus_i = pd.read_json(f'{MEAS_path}\Init_Bus_i.json', orient=orient)
        if df_Bus_i['bus_name'].dtypes != str:
            df_Bus_i['bus_name'] = df_Bus_i['bus_name'].astype(str)
        df_Bus_i = df_Bus_i.assign(Rii_Vm=0, Rii_SM=0, Rii_0=0, Rii_Psd=0)

        # df_Elem_ft = pd.read_excel(f'{MEAS_init_address}', sheet_name='Elem_ft')
        df_Elem_ft = pd.read_json(f'{MEAS_path}\Init_Elem_ft.json', orient=orient)
        if df_Elem_ft['from_bus'].dtypes != str:
            df_Elem_ft['from_bus'] = df_Elem_ft['from_bus'].astype(str)
        if df_Elem_ft['to_bus'].dtypes != str:
            df_Elem_ft['to_bus'] = df_Elem_ft['to_bus'].astype(str)
        df_Elem_ft = df_Elem_ft.assign(Rii_PQft=0, Rii_Ift=0)

        dss.text(f'compile [{DSS_file_address}]')
        dss.solution_solve()
        Per_Unit = Values_per_unit(self.Sbas3ph_MVA)
        elem_DSS = ['lines', 'transformers']
        df_Vi_PU = data_DSS.Volt_Ang_node_PU()
        df_Vi_PU = df_Vi_PU.drop(['num_nodes', 'ph_1', 'ph_2', 'ph_3', 'Ang1(deg)', 'Ang3(deg)', 'Ang2(deg)'], axis=1)

        df_Elem_PQi_PU = Per_Unit.element_PQij_PU(data_DSS.element_powers_PQij(element=['loads', 'capacitors']))
        df_Elem_PQi_PU = df_Elem_PQi_PU.groupby('from_bus').agg(sum).reset_index()
        df_Elem_PQi_PU = df_Elem_PQi_PU.drop(['num_ph', 'num_cond', 'ph_1', 'ph_2', 'ph_3'], axis=1)
        df_Elem_PQi_PU = df_Elem_PQi_PU.rename(columns={'from_bus': 'bus_name'})

        dfs = [df_Bus_i, df_Vi_PU, df_Elem_PQi_PU]
        df_Bus_i = reduce(lambda left, right: pd.merge(left, right, on='bus_name'), dfs)

        df_Bus_i.loc[:, ['V1m(pu)', 'V2m(pu)', 'V3m(pu)']] = 0
        df_Bus_i.loc[:, ['P1md(pu)', 'P2md(pu)', 'P3md(pu)']] = 0
        df_Bus_i.loc[:, ['Q1md(pu)', 'Q2md(pu)', 'Q3md(pu)']] = 0

        df_Elem_PQft = Per_Unit.element_PQij_PU(data_DSS.element_powers_PQij(element=elem_DSS))
        df_Elem_PQft = df_Elem_PQft[['element_name', 'P1(pu)', 'P2(pu)', 'P3(pu)', 'Q1(pu)', 'Q2(pu)', 'Q3(pu)']]
        df_Elem_Ift = Per_Unit.element_Iij_PU(data_DSS.element_currents_Iij_Ang(element=elem_DSS))
        df_Elem_Ift = df_Elem_Ift[['element_name', 'I1(pu)', 'I2(pu)', 'I3(pu)']]

        df_ft = [df_Elem_ft, df_Elem_PQft, df_Elem_Ift]
        df_Elem_ft = reduce(lambda left, right: pd.merge(left, right, on='element_name'), df_ft)

        df_Elem_ft.loc[:, ['P1mft(pu)', 'P2mft(pu)', 'P3mft(pu)']] = 0
        df_Elem_ft.loc[:, ['Q1mft(pu)', 'Q2mft(pu)', 'Q3mft(pu)']] = 0
        df_Elem_ft.loc[:, ['I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)']] = 0

        # PMU measurements
        # df_Bus_i_PMU = pd.read_excel(f'{MEAS_init_address}', sheet_name='Bus_i_PMU')
        df_Bus_i_PMU = pd.read_json(f'{MEAS_path}\Init_Bus_i_PMU.json', orient=orient)
        df_Bus_i_PMU = df_Bus_i_PMU.assign(Rii_Vm=0)
        df_Bus_i_PMU.loc[:, ['V1m(pu)', 'V2m(pu)', 'V3m(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']] = 0

        df_Vi_PMU = data_DSS.Volt_Ang_node_PU()
        df_Vi_PMU = df_Vi_PMU.drop(['num_nodes', 'ph_1', 'ph_2', 'ph_3'], axis=1)

        # df_Elem_ft_PMU = pd.read_excel(f'{MEAS_init_address}', sheet_name='Elem_ft_PMU')
        df_Elem_ft_PMU = pd.read_json(f'{MEAS_path}\Init_Elem_ft_PMU.json', orient=orient)
        df_Elem_ft_PMU = df_Elem_ft_PMU.assign(Rii_Ift=0)
        df_Elem_ft_PMU.loc[:, ['I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']] = 0

        df_Elem_Ift_PU = Per_Unit.element_Iij_PU(data_DSS.element_currents_Iij_Ang(element=elem_DSS))
        df_Elem_Ift_PU = df_Elem_Ift_PU[
            ['element_name', 'I1(pu)', 'ang1(deg)', 'I2(pu)', 'ang2(deg)', 'I3(pu)', 'ang3(deg)']]

        nVi = df_Bus_i['STS_Vm'].sum()
        nPQi_SM = df_Bus_i['STS_PQd(SM)'].sum()
        nPQi_0 = df_Bus_i['STS_PQd(0)'].sum()
        nPQi_Psd = df_Bus_i['STS_PQd(Psd)'].sum()
        nPQft = df_Elem_ft['STS_PQft'].sum()
        nIft = df_Elem_ft['STS_Ift'].sum()
        nVi_PMU = df_Bus_i_PMU['STS_Vm'].sum()
        nIft_PMU = df_Elem_ft_PMU['STS_Ift'].sum()

        ntotal = nVi + nPQi_SM + nPQi_0 + nPQi_Psd + nPQft + nIft + nVi_PMU + nIft_PMU
        isInt = isinstance(ntotal, numbers.Integral)
        if isInt != True:
            update_logg_file('Error\nAttention: Check the meter statuses in the MEAS_file_format.xlsx file.', 5, log_py)
            exit()

        np.random.seed(seed_DS)
        error_pu = (np.random.normal(loc=0, scale=1, size=ntotal)/100).reshape(ntotal, 1)
        aux_meas = 0
        if nVi != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_Vm'].isin([1])]
            error = error_pu[aux_meas:nVi]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Bus_i['Unc(%)_Vm'][index] / (3 * 100), nDP)
                df_Bus_i.loc[index, 'Rii_Vm'] = std_dev ** 2
                df_Bus_i.loc[index, 'V1m(pu)'] = round((df_Bus_i['V1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'V2m(pu)'] = round((df_Bus_i['V2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'V3m(pu)'] = round((df_Bus_i['V3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nVi
        if nPQi_SM != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(SM)'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nPQi_SM]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Bus_i['Unc(%)_PQd'][index] / (3 * 100), nDP)
                df_Bus_i.loc[index, 'Rii_SM'] = std_dev ** 2
                df_Bus_i.loc[index, 'P1md(pu)'] = round((df_Bus_i['P1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'P2md(pu)'] = round((df_Bus_i['P2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'P3md(pu)'] = round((df_Bus_i['P3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q1md(pu)'] = round((df_Bus_i['Q1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q2md(pu)'] = round((df_Bus_i['Q2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q3md(pu)'] = round((df_Bus_i['Q3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nPQi_SM
        if nPQi_0 != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(0)'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nPQi_0]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Bus_i['Unc(%)_PQd'][index] / (3 * 100), nDP)
                df_Bus_i.loc[index, 'Rii_0'] = std_dev ** 2
                df_Bus_i.loc[index, 'P1md(pu)'] = round((df_Bus_i['P1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'P2md(pu)'] = round((df_Bus_i['P2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'P3md(pu)'] = round((df_Bus_i['P3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q1md(pu)'] = round((df_Bus_i['Q1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q2md(pu)'] = round((df_Bus_i['Q2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q3md(pu)'] = round((df_Bus_i['Q3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nPQi_0
        if nPQi_Psd != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(Psd)'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nPQi_Psd]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Bus_i['Unc(%)_PQd'][index] / (3 * 100), nDP)
                df_Bus_i.loc[index, 'Rii_Psd'] = std_dev ** 2
                df_Bus_i.loc[index, 'P1md(pu)'] = round((df_Bus_i['P1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'P2md(pu)'] = round((df_Bus_i['P2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'P3md(pu)'] = round((df_Bus_i['P3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q1md(pu)'] = round((df_Bus_i['Q1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q2md(pu)'] = round((df_Bus_i['Q2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i.loc[index, 'Q3md(pu)'] = round((df_Bus_i['Q3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nPQi_Psd
        if nPQft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_PQft'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nPQft]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Elem_ft['Unc(%)_PQft'][index] / (3 * 100), nDP)
                df_Elem_ft.loc[index, 'Rii_PQft'] = std_dev ** 2
                df_Elem_ft.loc[index, 'P1mft(pu)'] = round((df_Elem_ft['P1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'P2mft(pu)'] = round((df_Elem_ft['P2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'P3mft(pu)'] = round((df_Elem_ft['P3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'Q1mft(pu)'] = round((df_Elem_ft['Q1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'Q2mft(pu)'] = round((df_Elem_ft['Q2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'Q3mft(pu)'] = round((df_Elem_ft['Q3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nPQft
        if nIft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_Ift'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nIft]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Elem_ft['Unc(%)_Ift'][index] / (3 * 100), nDP)
                df_Elem_ft.loc[index, 'Rii_Ift'] = std_dev ** 2
                df_Elem_ft.loc[index, 'I1mft(pu)'] = round((df_Elem_ft['I1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'I2mft(pu)'] = round((df_Elem_ft['I2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft.loc[index, 'I3mft(pu)'] = round((df_Elem_ft['I3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nIft
        if nVi_PMU != 0:
            df_aux = df_Bus_i_PMU[df_Bus_i_PMU['STS_Vm'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nVi_PMU]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Bus_i_PMU['Unc(%)_Vm'][index] / (3 * 100), nDP)
                df_Bus_i_PMU.loc[index, 'Rii_Vm'] = std_dev ** 2
                df_Bus_i_PMU.loc[index, 'V1m(pu)'] = round((df_Vi_PMU['V1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i_PMU.loc[index, 'V2m(pu)'] = round((df_Vi_PMU['V2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i_PMU.loc[index, 'V3m(pu)'] = round((df_Vi_PMU['V3(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i_PMU.loc[index, 'Ang1m(deg)'] = round((df_Vi_PMU['Ang1(deg)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i_PMU.loc[index, 'Ang2m(deg)'] = round((df_Vi_PMU['Ang2(deg)'][index] + (std_dev * error[aux][0])), nDP)
                df_Bus_i_PMU.loc[index, 'Ang3m(deg)'] = round((df_Vi_PMU['Ang3(deg)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nVi_PMU
        if nIft_PMU != 0:
            df_aux = df_Elem_ft_PMU[df_Elem_ft_PMU['STS_Ift'].isin([1])]
            error = error_pu[aux_meas:aux_meas + nIft_PMU]
            aux = 0
            for index, row in df_aux.iterrows():
                std_dev = round(df_Elem_ft_PMU['Unc(%)_Ift'][index] / (3 * 100), nDP)
                df_Elem_ft_PMU.loc[index, 'Rii_Ift'] = std_dev ** 2
                df_Elem_ft_PMU.loc[index, 'I1mft(pu)'] = round(
                    (df_Elem_Ift_PU['I1(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft_PMU.loc[index, 'I2mft(pu)'] = round(
                    (df_Elem_Ift_PU['I2(pu)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft_PMU.loc[index, 'I3mft(pu)'] = round(
                    (df_Elem_Ift_PU['I3(pu)'][index] + (std_dev * error[aux][0])), nDP)

                df_Elem_ft_PMU.loc[index, 'Ang1m(deg)'] = round(
                    (df_Elem_Ift_PU['ang1(deg)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft_PMU.loc[index, 'Ang2m(deg)'] = round(
                    (df_Elem_Ift_PU['ang2(deg)'][index] + (std_dev * error[aux][0])), nDP)
                df_Elem_ft_PMU.loc[index, 'Ang3m(deg)'] = round(
                    (df_Elem_Ift_PU['ang3(deg)'][index] + (std_dev * error[aux][0])), nDP)
                aux += 1
            aux_meas += nIft_PMU

        df_Bus_i = df_Bus_i[
            ['bus_name', 'num_nodes', 'ph_1', 'ph_2', 'ph_3',
             'STS_Vm', 'Rii_Vm', 'V1m(pu)', 'V2m(pu)', 'V3m(pu)',
             'STS_PQd(SM)', 'Rii_SM', 'STS_PQd(0)', 'Rii_0', 'STS_PQd(Psd)', 'Rii_Psd',
             'P1md(pu)', 'P2md(pu)', 'P3md(pu)', 'Q1md(pu)', 'Q2md(pu)', 'Q3md(pu)']]

        df_Elem_ft = df_Elem_ft[
            ['element_name', 'num_ph', 'from_bus', 'to_bus', 'ph_1', 'ph_2', 'ph_3',
             'STS_PQft', 'Rii_PQft', 'P1mft(pu)', 'P2mft(pu)', 'P3mft(pu)', 'Q1mft(pu)', 'Q2mft(pu)', 'Q3mft(pu)',
             'STS_Ift', 'Rii_Ift', 'I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)']]

        df_Bus_i_PMU = df_Bus_i_PMU[
            ['bus_name', 'num_nodes', 'ph_1', 'ph_2', 'ph_3', 'STS_Vm', 'Rii_Vm',
             'V1m(pu)', 'V2m(pu)', 'V3m(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']]

        df_Elem_ft_PMU = df_Elem_ft_PMU[
            ['element_name', 'num_ph', 'from_bus', 'to_bus', 'ph_1', 'ph_2', 'ph_3', 'STS_Ift', 'Rii_Ift',
             'I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)', 'Ang1m(deg)', 'Ang2m(deg)', 'Ang3m(deg)']]

        'Create and export files with extension .JSON'
        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)

        if to_Excel_MEAS == True:
            dict_aux = dict()
            dict_aux['Bus_i'] = df_Bus_i
            dict_aux['Elem_ft'] = df_Elem_ft
            dict_aux['Bus_i_PMU'] = df_Bus_i_PMU
            dict_aux['Elem_ft_PMU'] = df_Elem_ft_PMU
            elem_name = ['Bus_i', 'Elem_ft', 'Bus_i_PMU', 'Elem_ft_PMU']

            try:
                writer = pd.ExcelWriter(f'{MEAS_path}\MEAS_error_DSS.xlsx')
                for name in elem_name:
                    dict_aux[name].to_excel(writer, sheet_name=name, index=False)
                writer.save()
                writer.close()
                update_logg_file(f'The file: MEAS_error_DSS.xlsx, was saved in {MEAS_path}', 2, log_py)

            except PermissionError:
                update_logg_file("Attention !! \nYou must close the MEAS_error_DSS.xlsx file and repeat the process.",
                                 4, log_py)
                exit()

    def generate_empty_MEAS_files(self, DSS_file_address, MEAS_path):
        """
        Generate an initial file of measurements, place the names of nodes and elements that can be measured in an .xlsx file.

        :return: MEAS_file_format.xlsx
        """
        dss.text("ClearAll")
        dss.text(f"compile [{DSS_file_address}]")
        dss.solution_solve()

        df_Bus_i = data_DSS.Bus_name_nodes_conn_ph()
        df_Elem_ft = data_DSS.Elem_name_ncond_conn_fb_tb_ph(element=['lines', 'transformers'])
        df_Elem_ft = df_Elem_ft.drop(columns=['num_cond', 'conn', 'bus1', 'bus2'])

        df_Bus_i[['STS_Vm', 'Rii_Vm', 'V1m(pu)', 'V2m(pu)', 'V3m(pu)',
                  'STS_PQd(SM)', 'Rii_SM',
                  'STS_PQd(0)', 'Rii_0',
                  'STS_PQd(Psd)', 'Rii_Psd',
                  'P1md(pu)', 'P2md(pu)', 'P3md(pu)',
                  'Q1md(pu)', 'Q2md(pu)', 'Q3md(pu)']] = 0

        df_Elem_ft[['STS_PQft', 'Rii_PQft',
                    'P1mft(pu)', 'P2mft(pu)', 'P3mft(pu)',
                    'Q1mft(pu)', 'Q2mft(pu)', 'Q3mft(pu)',
                    'STS_Ift', 'Rii_Ift',
                    'I1mft(pu)', 'I2mft(pu)', 'I3mft(pu)']] = 0

        df_Bus_i_PMU = data_DSS.Bus_name_nodes_conn_ph()
        df_Elem_ft_PMU = data_DSS.Elem_name_ncond_conn_fb_tb_ph(element=['lines', 'transformers'])
        df_Elem_ft = df_Elem_ft.drop(columns=['num_cond', 'conn', 'bus1', 'bus2'])

        df_Bus_i_PMU[['Rii_Vm', 'STS_Vm']] = 0
        df_Elem_ft_PMU[['Rii_Ift', 'STS_Ift']] = 0

        'Create and export files with extension .JSON'

        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{MEAS_path}\MEAS_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)

        if to_Excel_MEAS == True:
            dict_aux = dict()
            dict_aux['Bus_i'] = df_Bus_i
            dict_aux['Elem_ft'] = df_Elem_ft
            dict_aux['Bus_i_PMU'] = df_Bus_i_PMU
            dict_aux['Elem_ft_PMU'] = df_Elem_ft_PMU
            elem_name = ['Bus_i', 'Elem_ft', 'Bus_i_PMU', 'Elem_ft_PMU']

            try:
                writer = pd.ExcelWriter(f'{MEAS_path}\MEAS_file_format.xlsx')
                for name in elem_name:
                    dict_aux[name].to_excel(writer, sheet_name=name, index=False)
                writer.save()
                writer.close()
                update_logg_file(
                    f'The empty file with the possible measurements was created and saved in: \n{MEAS_path}\MEAS_file_format.xlsx',
                    1, log_py)
            except PermissionError:
                update_logg_file("Attention !! \nYou must close the MEAS_file_format.xlsx file and repeat the process.",
                                 4, log_py)
                exit()


class Normalization_MEAS:
    """
    Class that reads and normalizes data from measurement files, delivers dataframe to be used in the state estimation algorithm.
    """

    def __init__(
            self, MEAS_path: str, MEAS_Pos: bool, Sbas3ph_MVA: float, path_save: str, alg_opt: list,
            seed_DS: int = 1, nDP: int = 5):
        self.MEAS_path = MEAS_path
        self.MEAS_Pos = MEAS_Pos
        self.Sbas3ph_MVA = Sbas3ph_MVA
        self.path_save = path_save
        self.alg_opt = alg_opt
        self.seed_DS = seed_DS
        self.nDP = nDP

    def SCADA_MEAS(self):
        """
        It reads and normalizes the scada system measurements and delivers a dataframe with the following columns:
        'Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'From', 'To', 'Rii']

        :return: df_MEAS
        """
        df_MEAS = pd.DataFrame(columns=['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'From', 'To', 'Rii'])
        # df_Bus_i = pd.read_excel(f'{self.MEAS_path}', sheet_name='Bus_i')
        df_Bus_i = pd.read_json(f'{self.MEAS_path}\MEAS_Bus_i.json', orient=orient)
        if df_Bus_i['bus_name'].dtypes != str:
            df_Bus_i['bus_name'] = df_Bus_i['bus_name'].astype(str)

        # df_Elem_ft = pd.read_excel(f'{self.MEAS_path}', sheet_name='Elem_ft')
        df_Elem_ft = pd.read_json(f'{self.MEAS_path}\MEAS_Elem_ft.json', orient=orient)
        if df_Elem_ft['from_bus'].dtypes != str:
            df_Elem_ft['from_bus'] = df_Elem_ft['from_bus'].astype(str)
        if df_Elem_ft['to_bus'].dtypes != str:
            df_Elem_ft['to_bus'] = df_Elem_ft['to_bus'].astype(str)

        nVi = df_Bus_i['STS_Vm'].sum()
        nPQi_SM = df_Bus_i['STS_PQd(SM)'].sum()
        nPQi_0 = df_Bus_i['STS_PQd(0)'].sum()
        nPQi_Psd = df_Bus_i['STS_PQd(Psd)'].sum()
        nPQft = df_Elem_ft['STS_PQft'].sum()
        nIft = df_Elem_ft['STS_Ift'].sum()

        # Type of measurement,
        # Vi - 1,
        if nVi != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_Vm'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 1,
                     'Value1(pu)': df_aux['V1m(pu)'][index],
                     'Value2(pu)': df_aux['V2m(pu)'][index],
                     'Value3(pu)': df_aux['V3m(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Vm'][index])},
                    ignore_index=True)
        # Pi_SM - 2, Qi_SM - 3,
        if nPQi_SM != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(SM)'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 2,
                     'Value1(pu)': df_aux['P1md(pu)'][index],
                     'Value2(pu)': df_aux['P2md(pu)'][index],
                     'Value3(pu)': df_aux['P3md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_SM'][index])},
                    ignore_index=True)

            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 3,
                     'Value1(pu)': df_aux['Q1md(pu)'][index],
                     'Value2(pu)': df_aux['Q2md(pu)'][index],
                     'Value3(pu)': df_aux['Q3md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_SM'][index])},
                    ignore_index=True)

        # Pi_Psd - 2, Qi_Psd - 3
        if nPQi_Psd != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(Psd)'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 2,
                     'Value1(pu)': df_aux['P1md(pu)'][index],
                     'Value2(pu)': df_aux['P2md(pu)'][index],
                     'Value3(pu)': df_aux['P3md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Psd'][index])},
                    ignore_index=True)

            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 3,
                     'Value1(pu)': df_aux['Q1md(pu)'][index],
                     'Value2(pu)': df_aux['Q2md(pu)'][index],
                     'Value3(pu)': df_aux['Q3md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Psd'][index])},
                    ignore_index=True)

        # Pi_0 - 4, Qi_0 - 5,
        if nPQi_0 != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(0)'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 2,
                     'Value1(pu)': 0,
                     'Value2(pu)': 0,
                     'Value3(pu)': 0,
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_0'][index])},
                    ignore_index=True)
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 3,
                     'Value1(pu)': 0,
                     'Value2(pu)': 0,
                     'Value3(pu)': 0,
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_0'][index])},
                    ignore_index=True)

        # Pft - 4, Qft - 5,
        if nPQft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_PQft'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 4,
                     'Value1(pu)': df_aux['P1mft(pu)'][index],
                     'Value2(pu)': df_aux['P2mft(pu)'][index],
                     'Value3(pu)': df_aux['P3mft(pu)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_PQft'][index])},
                    ignore_index=True)

            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 5,
                     'Value1(pu)': df_aux['Q1mft(pu)'][index],
                     'Value2(pu)': df_aux['Q2mft(pu)'][index],
                     'Value3(pu)': df_aux['Q3mft(pu)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_PQft'][index])},
                    ignore_index=True)
        # |Ift| - 6
        if nIft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_Ift'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 6,
                     'Value1(pu)': df_aux['I1mft(pu)'][index],
                     'Value2(pu)': df_aux['I2mft(pu)'][index],
                     'Value3(pu)': df_aux['I3mft(pu)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_Ift'][index])},
                    ignore_index=True)

        df_MEAS = pd.merge(df_MEAS, data_DSS.allbusnames_aux(), how='left', left_on='From', right_on='bus_name')
        df_MEAS = pd.merge(df_MEAS, data_DSS.allbusnames_aux(), how='left', left_on='To', right_on='bus_name')
        df_MEAS = df_MEAS.drop(columns=['bus_name_x', 'bus_name_y'])
        df_MEAS = df_MEAS.rename(columns={'bus_name_aux_x': 'From_aux', 'bus_name_aux_y': 'To_aux'})
        df_MEAS = df_MEAS[['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'From', 'To', 'From_aux', 'To_aux', 'Rii']]
        df_MEAS = df_MEAS.fillna('')

        if self.alg_opt == alg_mapping['op1'] or \
                self.alg_opt == alg_mapping['op2'] or \
                self.alg_opt == alg_mapping['op3']:
            df_MEAS = df_MEAS.drop(['Value2(pu)', 'Value3(pu)'], axis=1)

        return df_MEAS

    def PMU_MEAS(self):
        """
        Read and normalize the phasor measurements and return a dataframe with the following columns: 'Type',
        'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'Angle1(deg)', 'Angle2(deg)', 'Angle3(deg)', 'From', 'To', 'Rii'.

        :return: df_MEAS_PMU
        """

        df_MEAS_PMU = pd.DataFrame(
            columns=['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'Angle1(deg)', 'Angle2(deg)', 'Angle3(deg)',
                     'From', 'To', 'Rii'])

        # df_Bus_i = pd.read_excel(f'{self.MEAS_path}', sheet_name='Bus_i_PMU')
        df_Bus_i = pd.read_json(f'{self.MEAS_path}\MEAS_Bus_i_PMU.json', orient=orient)

        if df_Bus_i['bus_name'].dtypes != str:
            df_Bus_i['bus_name'] = df_Bus_i['bus_name'].astype(str)

        # df_Elem_ft = pd.read_excel(f'{self.MEAS_path}', sheet_name='Elem_ft_PMU')
        df_Elem_ft = pd.read_json(f'{self.MEAS_path}\MEAS_Elem_ft_PMU.json', orient=orient)

        nVi = df_Bus_i['STS_Vm'].sum()
        nIft = df_Elem_ft['STS_Ift'].sum()

        # Type of measurement,
        # |Vi|-Ang_i   - 7,
        if nVi != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_Vm'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS_PMU = df_MEAS_PMU.append(
                    {'Type': 7,
                     'Value1(pu)': df_aux['V1m(pu)'][index],
                     'Value2(pu)': df_aux['V2m(pu)'][index],
                     'Value3(pu)': df_aux['V3m(pu)'][index],
                     'Angle1(deg)': df_aux['Ang1m(deg)'][index],
                     'Angle2(deg)': df_aux['Ang2m(deg)'][index],
                     'Angle3(deg)': df_aux['Ang3m(deg)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Vm'][index])},
                    ignore_index=True)
        # |Ift|-Ang_ft - 8,
        if nIft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_Ift'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS_PMU = df_MEAS_PMU.append(
                    {'Type': 8,
                     'Value1(pu)': df_aux['I1mft(pu)'][index],
                     'Value2(pu)': df_aux['I2mft(pu)'][index],
                     'Value3(pu)': df_aux['I3mft(pu)'][index],
                     'Angle1(deg)': df_aux['Ang1m(deg)'][index],
                     'Angle2(deg)': df_aux['Ang2m(deg)'][index],
                     'Angle3(deg)': df_aux['Ang3m(deg)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_Ift'][index])},
                    ignore_index=True)

        df_MEAS_PMU = pd.merge(df_MEAS_PMU, data_DSS.allbusnames_aux(), how='left', left_on='From', right_on='bus_name')
        if nIft != 0:
            df_MEAS_PMU = pd.merge(df_MEAS_PMU, data_DSS.allbusnames_aux(), how='left', left_on='To',
                                   right_on='bus_name')
            df_MEAS_PMU = df_MEAS_PMU.drop(columns=['bus_name_x', 'bus_name_y'])
            df_MEAS_PMU = df_MEAS_PMU.rename(columns={'bus_name_aux_x': 'From_aux', 'bus_name_aux_y': 'To_aux'})
        else:
            df_MEAS_PMU = df_MEAS_PMU.drop(columns=['bus_name'])
            df_MEAS_PMU = df_MEAS_PMU.rename(columns={'bus_name_aux': 'From_aux'})
            df_MEAS_PMU['To_aux'] = df_MEAS_PMU['To']

        df_MEAS_PMU = df_MEAS_PMU[['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)',
                                   'Angle1(deg)', 'Angle2(deg)', 'Angle3(deg)',
                                   'From', 'To', 'From_aux', 'To_aux', 'Rii']]
        df_MEAS_PMU = df_MEAS_PMU.fillna('')

        if self.alg_opt == alg_mapping['op1'] or \
                self.alg_opt == alg_mapping['op2'] or \
                self.alg_opt == alg_mapping['op3']:
            df_MEAS_PMU = df_MEAS_PMU.drop(['Value2(pu)', 'Value3(pu)', 'Angle2(deg)', 'Angle3(deg)'], axis=1)

        return df_MEAS_PMU

    def SCADA_PMU_MEAS_Pos(self):

        if self.MEAS_Pos == False:
            'SCADA measurements'
            # df_Bus_i = pd.read_excel(f'{self.MEAS_path}', sheet_name='Bus_i')
            df_Bus_i = pd.read_json(f'{self.MEAS_path}\MEAS_Bus_i.json', orient=orient)

            if df_Bus_i['bus_name'].dtypes != str:
                df_Bus_i['bus_name'] = df_Bus_i['bus_name'].astype(str)

            df_Bus_i = df_Bus_i[['bus_name', 'STS_Vm', 'Rii_Vm',
                                 'STS_PQd(SM)', 'Rii_SM', 'STS_PQd(0)', 'Rii_0', 'STS_PQd(Psd)', 'Rii_Psd']]

            # df_Elem_ft = pd.read_excel(f'{self.MEAS_path}', sheet_name='Elem_ft')
            df_Elem_ft = pd.read_json(f'{self.MEAS_path}\MEAS_Elem_ft.json', orient=orient)
            if df_Elem_ft['from_bus'].dtypes != str:
                df_Elem_ft['from_bus'] = df_Elem_ft['from_bus'].astype(str)
            if df_Elem_ft['to_bus'].dtypes != str:
                df_Elem_ft['to_bus'] = df_Elem_ft['to_bus'].astype(str)
            df_Elem_ft = df_Elem_ft[
                ['element_name', 'from_bus', 'to_bus', 'STS_PQft', 'Rii_PQft', 'STS_Ift', 'Rii_Ift']]
            dss.solution_solve()

            Per_Unit = Values_per_unit(self.Sbas3ph_MVA)
            elem_DSS = ['lines', 'transformers']
            df_Vi_PU = data_DSS.Volt_Ang_node_PU()
            df_Vi_PU = df_Vi_PU.drop([
                'num_nodes', 'ph_1', 'ph_2', 'ph_3', 'V2(pu)', 'V3(pu)', 'Ang1(deg)', 'Ang2(deg)', 'Ang3(deg)'], axis=1)

            df_Elem_PQi_PU = Per_Unit.element_PQij_PU(data_DSS.element_powers_PQij(element=['loads', 'capacitors']))
            df_Elem_PQi_PU = df_Elem_PQi_PU.groupby('from_bus').agg(sum).reset_index()
            df_Elem_PQi_PU = df_Elem_PQi_PU.drop(
                ['num_ph', 'num_cond', 'ph_1', 'ph_2', 'ph_3', 'P2(pu)', 'P3(pu)', 'Q2(pu)', 'Q3(pu)'], axis=1)
            df_Elem_PQi_PU = df_Elem_PQi_PU.rename(columns={'from_bus': 'bus_name'})

            dfs = [df_Bus_i, df_Vi_PU, df_Elem_PQi_PU]
            df_Bus_i = reduce(lambda left, right: pd.merge(left, right, on='bus_name'), dfs)
            df_Bus_i.loc[:, ['V1m(pu)']] = 0
            df_Bus_i.loc[:, ['P1md(pu)']] = 0
            df_Bus_i.loc[:, ['Q1md(pu)']] = 0

            df_Elem_PQft = Per_Unit.element_PQij_PU(data_DSS.element_powers_PQij(element=elem_DSS))
            df_Elem_PQft = df_Elem_PQft[['element_name', 'P1(pu)', 'Q1(pu)']]
            df_Elem_Ift = Per_Unit.element_Iij_PU(data_DSS.element_currents_Iij_Ang(element=elem_DSS))
            df_Elem_Ift = df_Elem_Ift[['element_name', 'I1(pu)']]

            df_ft = [df_Elem_ft, df_Elem_PQft, df_Elem_Ift]
            df_Elem_ft = reduce(lambda left, right: pd.merge(left, right, on='element_name'), df_ft)

            df_Elem_ft.loc[:, ['P1mft(pu)']] = 0
            df_Elem_ft.loc[:, ['Q1mft(pu)']] = 0
            df_Elem_ft.loc[:, ['I1mft(pu)']] = 0

            # PMU measurements
            # df_Bus_i_PMU = pd.read_excel(f'{self.MEAS_path}', sheet_name='Bus_i_PMU')
            df_Bus_i_PMU = pd.read_json(f'{self.MEAS_path}\MEAS_Bus_i_PMU.json', orient=orient)
            if df_Bus_i_PMU['bus_name'].dtypes != str:
                df_Bus_i_PMU['bus_name'] = df_Bus_i_PMU['bus_name'].astype(str)

            df_Bus_i_PMU = df_Bus_i_PMU[['bus_name', 'STS_Vm', 'Rii_Vm']]
            df_Bus_i_PMU.loc[:, ['V1m(pu)', 'Ang1m(deg)']] = 0
            df_Vi_PMU = data_DSS.Volt_Ang_node_PU()
            df_Vi_PMU = df_Vi_PMU[['bus_name', 'V1(pu)', 'Ang1(deg)']]

            df_ft = [df_Bus_i_PMU, df_Vi_PMU]
            df_Bus_i_PMU = reduce(lambda left, right: pd.merge(left, right, on='bus_name'), df_ft)

            # df_Elem_ft_PMU = pd.read_excel(f'{self.MEAS_path}', sheet_name='Elem_ft_PMU')
            df_Elem_ft_PMU = pd.read_json(f'{self.MEAS_path}\MEAS_Elem_ft_PMU.json', orient=orient)

            df_Elem_ft_PMU = df_Elem_ft_PMU[['element_name', 'from_bus', 'to_bus', 'STS_Ift', 'Rii_Ift']]
            df_Elem_ft_PMU.loc[:, ['I1mft(pu)', 'Ang1m(deg)']] = 0

            df_Elem_Ift_PU = Per_Unit.element_Iij_PU(data_DSS.element_currents_Iij_Ang(element=elem_DSS))
            df_Elem_Ift_PU = df_Elem_Ift_PU[['element_name', 'I1(pu)', 'ang1(deg)']]

            df_ft = [df_Elem_ft_PMU, df_Elem_Ift_PU]
            df_Elem_ft_PMU = reduce(lambda left, right: pd.merge(left, right, on='element_name'), df_ft)

            nVi = df_Bus_i['STS_Vm'].sum()
            nPQi_SM = df_Bus_i['STS_PQd(SM)'].sum()
            nPQi_0 = df_Bus_i['STS_PQd(0)'].sum()
            nPQi_Psd = df_Bus_i['STS_PQd(Psd)'].sum()
            nPQft = df_Elem_ft['STS_PQft'].sum()
            nIft = df_Elem_ft['STS_Ift'].sum()
            nVi_PMU = df_Bus_i_PMU['STS_Vm'].sum()
            nIft_PMU = df_Elem_ft_PMU['STS_Ift'].sum()

            ntotal = nVi + nPQi_SM + nPQi_0 + nPQi_Psd + nPQft + nIft + nVi_PMU + nIft_PMU
            np.random.seed(self.seed_DS)
            error_pu = (np.random.normal(loc=0, scale=1, size=ntotal)/100).reshape(ntotal, 1)
            aux_meas = 0
            if nVi != 0:
                df_aux = df_Bus_i[df_Bus_i['STS_Vm'].isin([1])]
                error = error_pu[aux_meas:nVi]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Bus_i['Rii_Vm'][index] ** 0.5
                    df_Bus_i.loc[index, 'V1m(pu)'] = round(
                        (df_Bus_i['V1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nVi
            if nPQi_SM != 0:
                df_aux = df_Bus_i[df_Bus_i['STS_PQd(SM)'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nPQi_SM]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Bus_i['Rii_SM'][index] ** 0.5
                    df_Bus_i.loc[index, 'P1md(pu)'] = round(
                        (df_Bus_i['P1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    df_Bus_i.loc[index, 'Q1md(pu)'] = round(
                        (df_Bus_i['Q1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nPQi_SM
            if nPQi_0 != 0:
                df_aux = df_Bus_i[df_Bus_i['STS_PQd(0)'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nPQi_0]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Bus_i['Rii_0'][index] ** 0.5
                    df_Bus_i.loc[index, 'P1md(pu)'] = round(
                        (df_Bus_i['P1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    df_Bus_i.loc[index, 'Q1md(pu)'] = round(
                        (df_Bus_i['Q1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nPQi_0
            if nPQi_Psd != 0:
                df_aux = df_Bus_i[df_Bus_i['STS_PQd(Psd)'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nPQi_Psd]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Bus_i['Rii_Psd'][index] ** 0.5
                    df_Bus_i.loc[index, 'P1md(pu)'] = round(
                        (df_Bus_i['P1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    df_Bus_i.loc[index, 'Q1md(pu)'] = round(
                        (df_Bus_i['Q1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nPQi_Psd
            if nPQft != 0:
                df_aux = df_Elem_ft[df_Elem_ft['STS_PQft'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nPQft]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Elem_ft['Rii_PQft'][index] ** 0.5
                    df_Elem_ft.loc[index, 'P1mft(pu)'] = round(
                        (df_Elem_ft['P1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    df_Elem_ft.loc[index, 'Q1mft(pu)'] = round(
                        (df_Elem_ft['Q1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nPQft
            if nIft != 0:
                df_aux = df_Elem_ft[df_Elem_ft['STS_Ift'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nIft]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Elem_ft['Rii_Ift'][index] ** 0.5
                    df_Elem_ft.loc[index, 'I1mft(pu)'] = round(
                        (df_Elem_ft['I1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nIft
            if nVi_PMU != 0:
                df_aux = df_Bus_i_PMU[df_Bus_i_PMU['STS_Vm'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nVi_PMU]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Bus_i_PMU['Rii_Vm'][index] ** 0.5
                    df_Bus_i_PMU.loc[index, 'V1m(pu)'] = round(
                        (df_Bus_i_PMU['V1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    df_Bus_i_PMU.loc[index, 'Ang1m(deg)'] = round(
                        (df_Bus_i_PMU['Ang1(deg)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1
                aux_meas += nVi_PMU
            if nIft_PMU != 0:
                df_aux = df_Elem_ft_PMU[df_Elem_ft_PMU['STS_Ift'].isin([1])]
                error = error_pu[aux_meas:aux_meas + nIft_PMU]
                aux = 0
                for index, row in df_aux.iterrows():
                    std_dev = df_Elem_ft_PMU['Rii_Ift'][index] ** 0.5
                    df_Elem_ft_PMU.loc[index, 'I1mft(pu)'] = round(
                        (df_Elem_ft_PMU['I1(pu)'][index] + (std_dev * error[aux][0])), self.nDP)
                    df_Elem_ft_PMU.loc[index, 'Ang1m(deg)'] = round(
                        (df_Elem_ft_PMU['ang1(deg)'][index] + (std_dev * error[aux][0])), self.nDP)
                    aux += 1

            df_Bus_i = df_Bus_i[
                ['bus_name', 'STS_Vm', 'Rii_Vm', 'V1m(pu)', 'STS_PQd(SM)', 'Rii_SM', 'STS_PQd(0)', 'Rii_0',
                 'STS_PQd(Psd)', 'Rii_Psd', 'P1md(pu)', 'Q1md(pu)']]

            df_Elem_ft = df_Elem_ft[
                ['element_name', 'from_bus', 'to_bus', 'STS_PQft', 'Rii_PQft', 'P1mft(pu)', 'Q1mft(pu)', 'STS_Ift',
                 'Rii_Ift', 'I1mft(pu)']]

            df_Bus_i_PMU = df_Bus_i_PMU[
                ['bus_name', 'STS_Vm', 'Rii_Vm', 'V1m(pu)', 'Ang1m(deg)']]

            df_Elem_ft_PMU = df_Elem_ft_PMU[
                ['element_name', 'from_bus', 'to_bus', 'STS_Ift', 'Rii_Ift', 'I1mft(pu)', 'Ang1m(deg)']]

            'Create and export files with extension .JSON'
            Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
            with open(f"{self.MEAS_path}\Pos_MEAS_Bus_i.json", "w") as outfile:
                outfile.write(Bus_i_init)

            Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
            with open(f"{self.MEAS_path}\Pos_MEAS_Elem_ft.json", "w") as outfile:
                outfile.write(Elem_ft_init)

            Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
            with open(f"{self.MEAS_path}\Pos_MEAS_Bus_i_PMU.json", "w") as outfile:
                outfile.write(Bus_i_PMU_init)

            Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
            with open(f"{self.MEAS_path}\Pos_MEAS_Elem_ft_PMU.json", "w") as outfile:
                outfile.write(Elem_ft_PMU_init)

            if to_Excel_MEAS == True:
                try:
                    dict_aux = dict()
                    dict_aux['Bus_i'] = df_Bus_i
                    dict_aux['Elem_ft'] = df_Elem_ft
                    dict_aux['Bus_i_PMU'] = df_Bus_i_PMU
                    dict_aux['Elem_ft_PMU'] = df_Elem_ft_PMU
                    elem_name = ['Bus_i', 'Elem_ft', 'Bus_i_PMU', 'Elem_ft_PMU']

                    writer = pd.ExcelWriter(f'{self.MEAS_path}\Pos_MEAS_error_DSS.xlsx')
                    for name in elem_name:
                        dict_aux[name].to_excel(writer, sheet_name=name, index=False)
                    writer.save()
                    writer.close()
                    update_logg_file(f'The file: MEAS_SeqPos_error_DSS.xlsx, was saved in:\n{self.MEAS_path}', 2,
                                     log_py)
                except PermissionError:
                    update_logg_file(
                        "Attention !! \nYou must close the Pos_MEAS_error_DSS.xlsx file and repeat the process.", 4,
                        log_py)
                    exit()

        else:
            df_Bus_i = pd.read_json(f'{self.MEAS_path}\Pos_MEAS_Bus_i.json', orient=orient)
            df_Elem_ft = pd.read_json(f'{self.MEAS_path}\Pos_MEAS_Elem_ft.json', orient=orient)
            df_Bus_i_PMU = pd.read_json(f'{self.MEAS_path}\Pos_MEAS_Bus_i_PMU.json', orient=orient)
            df_Elem_ft_PMU = pd.read_json(f'{self.MEAS_path}\Pos_MEAS_Elem_ft_PMU.json', orient=orient)

        # SCADA to_Excel_MEAS
        df_MEAS = pd.DataFrame(columns=['Type', 'Value1(pu)', 'From', 'To', 'Rii'])

        if df_Bus_i['bus_name'].dtypes != str:
            df_Bus_i['bus_name'] = df_Bus_i['bus_name'].astype(str)

        if df_Elem_ft['from_bus'].dtypes != str:
            df_Elem_ft['from_bus'] = df_Elem_ft['from_bus'].astype(str)

        if df_Elem_ft['to_bus'].dtypes != str:
            df_Elem_ft['to_bus'] = df_Elem_ft['to_bus'].astype(str)

        nVi = df_Bus_i['STS_Vm'].sum()
        nPQi_SM = df_Bus_i['STS_PQd(SM)'].sum()
        nPQi_0 = df_Bus_i['STS_PQd(0)'].sum()
        nPQi_Psd = df_Bus_i['STS_PQd(Psd)'].sum()
        nPQft = df_Elem_ft['STS_PQft'].sum()
        nIft = df_Elem_ft['STS_Ift'].sum()

        # Type of measurement,
        # Vi - 1,
        if nVi != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_Vm'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 1,
                     'Value1(pu)': df_aux['V1m(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Vm'][index])},
                    ignore_index=True)
        # Pi_SM - 2, Qi_SM - 3,
        if nPQi_SM != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(SM)'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 2,
                     'Value1(pu)': df_aux['P1md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_SM'][index])},
                    ignore_index=True)

            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 3,
                     'Value1(pu)': df_aux['Q1md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_SM'][index])},
                    ignore_index=True)

        # Pi_Psd - 2, Qi_Psd - 3
        if nPQi_Psd != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(Psd)'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 2,
                     'Value1(pu)': df_aux['P1md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Psd'][index])},
                    ignore_index=True)

            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 3,
                     'Value1(pu)': df_aux['Q1md(pu)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Psd'][index])},
                    ignore_index=True)

        # Pi_0 - 4, Qi_0 - 5,
        if nPQi_0 != 0:
            df_aux = df_Bus_i[df_Bus_i['STS_PQd(0)'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 2,
                     'Value1(pu)': 0,
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_0'][index])},
                    ignore_index=True)
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 3,
                     'Value1(pu)': 0,
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_0'][index])},
                    ignore_index=True)

        # Pft - 4, Qft - 5,
        if nPQft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_PQft'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 4,
                     'Value1(pu)': df_aux['P1mft(pu)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_PQft'][index])},
                    ignore_index=True)

            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 5,
                     'Value1(pu)': df_aux['Q1mft(pu)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_PQft'][index])},
                    ignore_index=True)
        # |Ift| - 6
        if nIft != 0:
            df_aux = df_Elem_ft[df_Elem_ft['STS_Ift'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS = df_MEAS.append(
                    {'Type': 6,
                     'Value1(pu)': df_aux['I1mft(pu)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_Ift'][index])},
                    ignore_index=True)

        df_MEAS = pd.merge(df_MEAS, data_DSS.allbusnames_aux(), how='left', left_on='From', right_on='bus_name')
        df_MEAS = pd.merge(df_MEAS, data_DSS.allbusnames_aux(), how='left', left_on='To', right_on='bus_name')
        df_MEAS = df_MEAS.drop(columns=['bus_name_x', 'bus_name_y'])
        df_MEAS = df_MEAS.rename(columns={'bus_name_aux_x': 'From_aux', 'bus_name_aux_y': 'To_aux'})
        df_MEAS = df_MEAS[['Type', 'Value1(pu)', 'From', 'To', 'From_aux', 'To_aux', 'Rii']]
        df_MEAS = df_MEAS.fillna('')

        # PMU to_Excel_MEAS
        df_MEAS_PMU = pd.DataFrame(columns=['Type', 'Value1(pu)', 'Angle1(deg)', 'From', 'To', 'Rii'])

        if df_Bus_i_PMU['bus_name'].dtypes != str:
            df_Bus_i_PMU['bus_name'] = df_Bus_i_PMU['bus_name'].astype(str)

        if df_Elem_ft_PMU['from_bus'].dtypes != str:
            df_Elem_ft_PMU['from_bus'] = df_Elem_ft_PMU['from_bus'].astype(str)
        if df_Elem_ft_PMU['to_bus'].dtypes != str:
            df_Elem_ft_PMU['to_bus'] = df_Elem_ft_PMU['to_bus'].astype(str)

        nVi = df_Bus_i_PMU['STS_Vm'].sum()
        nIft = df_Elem_ft_PMU['STS_Ift'].sum()

        # Type of measurement,
        # |Vi|-Ang_i   - 7,
        if nVi != 0:
            df_aux = df_Bus_i_PMU[df_Bus_i_PMU['STS_Vm'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS_PMU = df_MEAS_PMU.append(
                    {'Type': 7,
                     'Value1(pu)': df_aux['V1m(pu)'][index],
                     'Angle1(deg)': df_aux['Ang1m(deg)'][index],
                     'From': df_aux['bus_name'][index],
                     'Rii': abs(df_aux['Rii_Vm'][index])},
                    ignore_index=True)
        # |Ift|-Ang_ft - 8,
        if nIft != 0:
            df_aux = df_Elem_ft_PMU[df_Elem_ft_PMU['STS_Ift'].isin([1])]
            for index, row in df_aux.iterrows():
                df_MEAS_PMU = df_MEAS_PMU.append(
                    {'Type': 8,
                     'Value1(pu)': df_aux['I1mft(pu)'][index],
                     'Angle1(deg)': df_aux['Ang1m(deg)'][index],
                     'From': df_aux['from_bus'][index],
                     'To': df_aux['to_bus'][index],
                     'Rii': abs(df_aux['Rii_Ift'][index])},
                    ignore_index=True)

        df_MEAS_PMU = pd.merge(df_MEAS_PMU, data_DSS.allbusnames_aux(), how='left', left_on='From', right_on='bus_name')
        if nIft != 0:
            df_MEAS_PMU = pd.merge(df_MEAS_PMU, data_DSS.allbusnames_aux(), how='left', left_on='To',
                                   right_on='bus_name')
            df_MEAS_PMU = df_MEAS_PMU.drop(columns=['bus_name_x', 'bus_name_y'])
            df_MEAS_PMU = df_MEAS_PMU.rename(columns={'bus_name_aux_x': 'From_aux', 'bus_name_aux_y': 'To_aux'})
        else:
            df_MEAS_PMU = df_MEAS_PMU.drop(columns=['bus_name'])
            df_MEAS_PMU = df_MEAS_PMU.rename(columns={'bus_name_aux': 'From_aux'})
            df_MEAS_PMU['To_aux'] = df_MEAS_PMU['To']

        df_MEAS_PMU = df_MEAS_PMU[['Type', 'Value1(pu)', 'Angle1(deg)', 'From', 'To', 'From_aux', 'To_aux', 'Rii']]

        return df_MEAS, df_MEAS_PMU

    def SCADA_measurements(self):

        np.random.seed(self.seed_DS)
        df_MEAS = pd.DataFrame(columns=['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'From', 'To', 'Rii'])

        # Type of measurement,
        # Vi-1, Pi(SM-Psd-0)-2, Qi(SM-Psd-0)-3, Pft-4, Qft-5, |Ift|-6
        elem_value_DSS = ['vsources', 'transformers', 'lines', 'loads', 'capacitors']
        Per_Unit = Values_per_unit(dss, self.Sbas3ph_MVA)
        df_Vi_DSS_PU = data_DSS.Volt_Ang_node_PU()
        df_PQ_DSS_PU = Per_Unit.element_PQij_PU(
            df_element_power=data_DSS.element_powers_PQij(element=elem_value_DSS))
        df_If_DSS_PU = Per_Unit.element_Iij_PU(
            df_element_currents=data_DSS.element_currents_Iij_Ang(element=elem_value_DSS))

        'common or traditional measures'
        df_Vi_MEAS = pd.read_excel(f'{self.MEAS_path}', sheet_name='|Vi|')
        df_PQi_MEAS = pd.read_excel(f'{self.MEAS_path}', sheet_name='PQi')
        df_PQf_MEAS = pd.read_excel(f'{self.MEAS_path}', sheet_name='PQf')
        df_PQi0_MEAS = pd.read_excel(f'{self.MEAS_path}', sheet_name='PQi0')
        df_PQi_pseudo_MEAS = pd.read_excel(f'{self.MEAS_path}', sheet_name='PQi_pseudo')
        df_If_MEAS = pd.read_excel(f'{self.MEAS_path}', sheet_name='|If|')

        nVi = len(df_Vi_MEAS)
        nPQi = len(df_PQi_MEAS)
        nPQi0 = len(df_PQi0_MEAS)
        nPQi_pseudo = len(df_PQi_pseudo_MEAS)
        nPQf = len(df_PQf_MEAS)
        nIf = len(df_If_MEAS)

        ntotal = nVi + nPQi + nPQf + nPQi0 + nPQi_pseudo + nIf
        Rii = np.random.normal(0, 1, size=(ntotal, 1))

        aux_Rii = 0
        if nVi != 0:
            Rii_Vi = Rii[aux_Rii:nVi].ravel() * df_Vi_MEAS['DS']
            aux_Rii = aux_Rii + nVi
        if nPQi != 0:
            Rii_PQi = Rii[aux_Rii:aux_Rii + nPQi].ravel() * df_PQi_MEAS['DS']
            aux_Rii = aux_Rii + nPQi
        if nPQi0 != 0:
            Rii_PQi0 = Rii[aux_Rii:aux_Rii + nPQi0].ravel() * df_PQi0_MEAS['DS']
            aux_Rii = aux_Rii + nPQi0
        if nPQi_pseudo != 0:
            Rii_PQi_pseudo = Rii[aux_Rii:aux_Rii + nPQi_pseudo].ravel() * df_PQi_pseudo_MEAS['DS']
            aux_Rii = aux_Rii + nPQi_pseudo
        if nPQf != 0:
            Rii_PQf = Rii[aux_Rii:aux_Rii + nPQf].ravel() * df_PQf_MEAS['DS']
            aux_Rii = aux_Rii + nPQf
        if nIf != 0:
            Rii_If = Rii[aux_Rii:aux_Rii + nIf].ravel() * df_If_MEAS['DS']
            aux_Rii = aux_Rii + nIf

        if df_Vi_MEAS.empty == True:
            pass
        else:
            for index, row in df_Vi_MEAS.iterrows():
                df_Vi_aux = df_Vi_DSS_PU[df_Vi_DSS_PU['bus_name'] == df_Vi_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Vi_aux['V1(pu)'] * Rii_Vi[index] + df_Vi_aux['V1(pu)']), 4)
                Value_2_EST = round(float(df_Vi_aux['V2(pu)'] * Rii_Vi[index] + df_Vi_aux['V2(pu)']), 4)
                Value_3_EST = round(float(df_Vi_aux['V3(pu)'] * Rii_Vi[index] + df_Vi_aux['V3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 1, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Vi_aux['bus_name'][0], 'Rii': Rii_Vi[index]}, ignore_index=True)

        if df_PQi_MEAS.empty == True:
            pass
        else:
            df_PQi_DSS = df_PQ_DSS_PU.copy()
            df_mask = df_PQi_DSS['to_bus'] == ''
            df_PQi_DSS = df_PQi_DSS[df_mask]
            df_PQi_DSS = df_PQi_DSS.groupby('from_bus').agg(sum).reset_index()
            df_Pi_DSS = df_PQi_DSS.copy()
            df_Pi_DSS = df_Pi_DSS.drop(columns=['Q1(pu)', 'Q2(pu)', 'Q3(pu)'])

            for index, row in df_PQi_MEAS.iterrows():
                df_Pi_aux = df_Pi_DSS[df_Pi_DSS['from_bus'] == df_PQi_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Pi_aux['P1(pu)'] * Rii_PQi[index] + df_Pi_aux['P1(pu)']), 4)
                Value_2_EST = round(float(df_Pi_aux['P2(pu)'] * Rii_PQi[index] + df_Pi_aux['P2(pu)']), 4)
                Value_3_EST = round(float(df_Pi_aux['P3(pu)'] * Rii_PQi[index] + df_Pi_aux['P3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 2, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Pi_aux['from_bus'][0], 'Rii': Rii_PQi[index]}, ignore_index=True)

            df_Qi_DSS = df_PQi_DSS.copy()
            df_Qi_DSS = df_Qi_DSS.drop(columns=['P1(pu)', 'P2(pu)', 'P3(pu)'])
            for index, row in df_PQi_MEAS.iterrows():
                df_Qi_aux = df_Qi_DSS[df_Qi_DSS['from_bus'] == df_PQi_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Qi_aux['Q1(pu)'] * Rii_PQi[index] + df_Qi_aux['Q1(pu)']), 4)
                Value_2_EST = round(float(df_Qi_aux['Q2(pu)'] * Rii_PQi[index] + df_Qi_aux['Q2(pu)']), 4)
                Value_3_EST = round(float(df_Qi_aux['Q3(pu)'] * Rii_PQi[index] + df_Qi_aux['Q3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 3, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Qi_aux['from_bus'][0], 'Rii': Rii_PQi[index]}, ignore_index=True)

        if df_PQi0_MEAS.empty == True:
            pass
        else:
            df_PQi_DSS = df_PQ_DSS_PU.copy()
            df_mask = df_PQi_DSS['to_bus'] == ''
            df_PQi_DSS = df_PQi_DSS[df_mask]
            df_PQi_DSS = df_PQi_DSS.groupby('from_bus').agg(sum).reset_index()

            df_Pi_DSS = df_PQi_DSS.copy()
            df_Pi_DSS = df_Pi_DSS.drop(columns=['Q1(pu)', 'Q2(pu)', 'Q3(pu)'])

            for index, row in df_PQi0_MEAS.iterrows():
                df_Pi0_aux = df_Pi_DSS[df_Pi_DSS['from_bus'] == df_PQi0_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Pi0_aux['P1(pu)'] * Rii_PQi0[index] + df_Pi0_aux['P1(pu)']), 4)
                Value_2_EST = round(float(df_Pi0_aux['P2(pu)'] * Rii_PQi0[index] + df_Pi0_aux['P2(pu)']), 4)
                Value_3_EST = round(float(df_Pi0_aux['P3(pu)'] * Rii_PQi0[index] + df_Pi0_aux['P3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 2, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Pi0_aux['from_bus'][0], 'Rii': Rii_PQi0[index]}, ignore_index=True)

            df_Qi_DSS = df_PQi_DSS.copy()
            df_Qi_DSS = df_Qi_DSS.drop(columns=['P1(pu)', 'P2(pu)', 'P3(pu)'])
            for index, row in df_PQi0_MEAS.iterrows():
                df_Qi0_aux = df_Qi_DSS[df_Qi_DSS['from_bus'] == df_PQi0_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Qi0_aux['Q1(pu)'] * Rii_PQi0[index] + df_Qi0_aux['Q1(pu)']), 4)
                Value_2_EST = round(float(df_Qi0_aux['Q2(pu)'] * Rii_PQi0[index] + df_Qi0_aux['Q2(pu)']), 4)
                Value_3_EST = round(float(df_Qi0_aux['Q3(pu)'] * Rii_PQi0[index] + df_Qi0_aux['Q3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 3, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Qi0_aux['from_bus'][0], 'Rii': Rii_PQi0[index]}, ignore_index=True)

        if df_PQi_pseudo_MEAS.empty == True:
            pass
        else:
            df_PQi_DSS = df_PQ_DSS_PU.copy()
            df_mask = df_PQi_DSS['to_bus'] == ''
            df_PQi_DSS = df_PQi_DSS[df_mask]
            df_PQi_DSS = df_PQi_DSS.groupby('from_bus').agg(sum).reset_index()

            df_Pi_DSS = df_PQi_DSS.copy()
            df_Pi_DSS = df_Pi_DSS.drop(columns=['Q1(pu)', 'Q2(pu)', 'Q3(pu)'])

            for index, row in df_PQi_pseudo_MEAS.iterrows():
                df_Pi_aux = df_Pi_DSS[df_Pi_DSS['from_bus'] == df_PQi_pseudo_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Pi_aux['P1(pu)'] * Rii_PQi_pseudo[index] + df_Pi_aux['P1(pu)']), 4)
                Value_2_EST = round(float(df_Pi_aux['P2(pu)'] * Rii_PQi_pseudo[index] + df_Pi_aux['P2(pu)']), 4)
                Value_3_EST = round(float(df_Pi_aux['P3(pu)'] * Rii_PQi_pseudo[index] + df_Pi_aux['P3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 2, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Pi_aux['from_bus'][0], 'Rii': Rii_PQi_pseudo[index]}, ignore_index=True)

            df_Qi_DSS = df_PQi_DSS.copy()
            df_Qi_DSS = df_Qi_DSS.drop(columns=['P1(pu)', 'P2(pu)', 'P3(pu)'])
            for index, row in df_PQi_pseudo_MEAS.iterrows():
                df_Qi_aux = df_Qi_DSS[df_Qi_DSS['from_bus'] == df_PQi_pseudo_MEAS['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Qi_aux['Q1(pu)'] * Rii_PQi_pseudo[index] + df_Qi_aux['Q1(pu)']), 4)
                Value_2_EST = round(float(df_Qi_aux['Q2(pu)'] * Rii_PQi_pseudo[index] + df_Qi_aux['Q2(pu)']), 4)
                Value_3_EST = round(float(df_Qi_aux['Q3(pu)'] * Rii_PQi_pseudo[index] + df_Qi_aux['Q3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 3, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': df_Qi_aux['from_bus'][0], 'Rii': Rii_PQi_pseudo[index]}, ignore_index=True)

        if df_PQf_MEAS.empty == True:
            pass
        else:
            df_PQf_DSS = df_PQ_DSS_PU.copy()
            df_PQf_MEAS['Elem_name'] = df_PQf_MEAS['Element'] + '.' + df_PQf_MEAS['Name_DSS']
            df_PQf_DSS = df_PQf_DSS[df_PQf_DSS['element_name'].isin(list(df_PQf_MEAS['Elem_name']))]

            df_Pf_DSS = df_PQf_DSS.copy()
            df_Pf_DSS = df_Pf_DSS.drop(columns=['Q1(pu)', 'Q2(pu)', 'Q3(pu)', 'conn'])
            for index, row in df_PQf_MEAS.iterrows():
                name, from_DSS, to_DSS = [df_PQf_MEAS['Elem_name'][index]], [df_PQf_MEAS['from_DSS'][index]], [
                    df_PQf_MEAS['to_DSS'][index]]
                filter = df_Pf_DSS[
                    df_Pf_DSS.element_name.isin(name) & df_Pf_DSS.from_bus.isin(from_DSS) & df_Pf_DSS.to_bus.isin(
                        to_DSS)].reset_index()
                Value_1_EST = round(float(filter['P1(pu)'] * Rii_PQf[index] + filter['P1(pu)']), 4)
                Value_2_EST = round(float(filter['P2(pu)'] * Rii_PQf[index] + filter['P2(pu)']), 4)
                Value_3_EST = round(float(filter['P3(pu)'] * Rii_PQf[index] + filter['P3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 4, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': filter['from_bus'][0], 'To': filter['to_bus'][0], 'Rii': Rii_PQf[index]},
                    ignore_index=True)

            df_Qf_DSS = df_PQf_DSS.copy()
            df_Qf_DSS = df_Qf_DSS.drop(columns=['P1(pu)', 'P2(pu)', 'P3(pu)', 'conn'])
            for index, row in df_PQf_MEAS.iterrows():
                name, from_DSS, to_DSS = [df_PQf_MEAS['Elem_name'][index]], [df_PQf_MEAS['from_DSS'][index]], [
                    df_PQf_MEAS['to_DSS'][index]]
                filter = df_Qf_DSS[
                    df_Qf_DSS.element_name.isin(name) & df_Qf_DSS.from_bus.isin(from_DSS) & df_Qf_DSS.to_bus.isin(
                        to_DSS)].reset_index()
                Value_1_EST = round(float(filter['Q1(pu)'] * Rii_PQf[index] + filter['Q1(pu)']), 4)
                Value_2_EST = round(float(filter['Q2(pu)'] * Rii_PQf[index] + filter['Q2(pu)']), 4)
                Value_3_EST = round(float(filter['Q3(pu)'] * Rii_PQf[index] + filter['Q3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 5, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': filter['from_bus'][0], 'To': filter['to_bus'][0], 'Rii': Rii_PQf[index]},
                    ignore_index=True)

        if df_If_MEAS.empty == True:
            pass
        else:
            df_If_DSS = df_If_DSS_PU.copy()
            df_If_MEAS['Elem_name'] = df_If_MEAS['Element'] + '.' + df_If_MEAS['Name_DSS']
            df_If_DSS = df_If_DSS[df_If_DSS['element_name'].isin(list(df_If_MEAS['Elem_name']))]
            df_If_DSS = df_If_DSS.drop(columns=['ang1(deg)', 'ang2(deg)', 'ang3(deg)', 'conn'])
            for index, row in df_If_MEAS.iterrows():
                name, from_DSS, to_DSS = [df_If_MEAS['Elem_name'][index]], [df_If_MEAS['from_DSS'][index]], [
                    df_If_MEAS['to_DSS'][index]]
                filter = df_If_DSS[
                    df_If_DSS.element_name.isin(name) & df_If_DSS.from_bus.isin(from_DSS) & df_If_DSS.to_bus.isin(
                        to_DSS)].reset_index()
                Value_1_EST = round(float(filter['I1(pu)'] * Rii_If[index] + filter['I1(pu)']), 4)
                Value_2_EST = round(float(filter['I2(pu)'] * Rii_If[index] + filter['I2(pu)']), 4)
                Value_3_EST = round(float(filter['I3(pu)'] * Rii_If[index] + filter['I3(pu)']), 4)
                df_MEAS = df_MEAS.append(
                    {'Type': 6, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'From': filter['from_bus'][0], 'To': filter['to_bus'][0], 'Rii': Rii_If[index]}, ignore_index=True)

        df_MEAS = pd.merge(df_MEAS, data_DSS.allbusnames_aux(), how='left', left_on='From', right_on='bus_name')
        df_MEAS = pd.merge(df_MEAS, data_DSS.allbusnames_aux(), how='left', left_on='To', right_on='bus_name')
        df_MEAS = df_MEAS.drop(columns=['bus_name_x', 'bus_name_y'])
        df_MEAS = df_MEAS.rename(columns={'bus_name_aux_x': 'From_aux', 'bus_name_aux_y': 'To_aux'})
        df_MEAS = df_MEAS[['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)', 'From', 'To', 'From_aux', 'To_aux', 'Rii']]
        df_MEAS = df_MEAS.fillna('')

        return df_MEAS

    def PMU_measurements(self):

        np.random.seed(self.seed_DS)
        df_MEAS_PMU = pd.DataFrame(columns=['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)',
                                            'Angle1(deg)', 'Angle2(deg)', 'Angle3(deg)',
                                            'From', 'To', 'Rii'])

        # Type of measurement,
        # |Vi|_Ang -8,  |Iij|_Ang -9,
        elem_value_DSS = ['vsources', 'transformers', 'lines', 'loads', 'capacitors']
        Per_Unit = Values_per_unit(dss, self.Sbas3ph_MVA)
        df_Vi_DSS_PU = data_DSS.Volt_Ang_node_PU()
        df_If_DSS_PU = Per_Unit.element_Iij_PU(
            df_element_currents=data_DSS.element_currents_Iij_Ang(element=elem_value_DSS))

        'phasor measurements'
        df_Vi_PMU = pd.read_excel(f'{self.MEAS_path}', sheet_name='|Vi|_Ang')
        df_If_PMU = pd.read_excel(f'{self.MEAS_path}', sheet_name='|If|_Ang')

        nVi_PMU = len(df_Vi_PMU)
        nIf_PMU = len(df_If_PMU)

        ntotal = nVi_PMU + nIf_PMU
        Rii = np.random.normal(0, 1, size=(ntotal, 1))

        aux_Rii = 0

        'PMU'
        if nVi_PMU != 0:
            Rii_Vi_PMU = Rii[aux_Rii:nVi_PMU].ravel() * df_Vi_PMU['DS']
            aux_Rii = aux_Rii + nVi_PMU
        if nIf_PMU != 0:
            Rii_If_PMU = Rii[aux_Rii:aux_Rii + nIf_PMU].ravel() * df_If_PMU['DS']
            aux_Rii = aux_Rii + nIf_PMU

        if df_Vi_PMU.empty == True:
            pass
        else:
            for index, row in df_Vi_PMU.iterrows():
                df_Vi_aux = df_Vi_DSS_PU[df_Vi_DSS_PU['bus_name'] == df_Vi_PMU['from_DSS'][index]].reset_index()
                Value_1_EST = round(float(df_Vi_aux['V1(pu)'] * Rii_Vi_PMU[index] + df_Vi_aux['V1(pu)']), 4)
                Value_2_EST = round(float(df_Vi_aux['V2(pu)'] * Rii_Vi_PMU[index] + df_Vi_aux['V2(pu)']), 4)
                Value_3_EST = round(float(df_Vi_aux['V3(pu)'] * Rii_Vi_PMU[index] + df_Vi_aux['V3(pu)']), 4)

                Angle_1_EST = round(float(df_Vi_aux['Ang1(deg)'] * Rii_Vi_PMU[index] + df_Vi_aux['Ang1(deg)']), 4)
                Angle_2_EST = round(float(df_Vi_aux['Ang2(deg)'] * Rii_Vi_PMU[index] + df_Vi_aux['Ang2(deg)']), 4)
                Angle_3_EST = round(float(df_Vi_aux['Ang3(deg)'] * Rii_Vi_PMU[index] + df_Vi_aux['Ang3(deg)']), 4)

                df_MEAS_PMU = df_MEAS_PMU.append(
                    {'Type': 8, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'Angle1(deg)': Angle_1_EST, 'Angle2(deg)': Angle_2_EST, 'Angle3(deg)': Angle_3_EST,
                     'From': df_Vi_aux['bus_name'][0], 'Rii': Rii_Vi_PMU[index]}, ignore_index=True)

        if df_If_PMU.empty == True:
            pass
        else:
            df_If_DSS = df_If_DSS_PU.copy()
            df_If_PMU['Elem_name'] = df_If_PMU['Element'] + '.' + df_If_PMU['Name_DSS']
            df_If_DSS = df_If_DSS[df_If_DSS['element_name'].isin(list(df_If_PMU['Elem_name']))]
            df_If_DSS = df_If_DSS.drop(columns=['conn'])
            for index, row in df_If_PMU.iterrows():
                name, from_DSS, to_DSS = [df_If_PMU['Elem_name'][index]], [df_If_PMU['from_DSS'][index]], [
                    df_If_PMU['to_DSS'][index]]
                filter = df_If_DSS[
                    df_If_DSS.element_name.isin(name) & df_If_DSS.from_bus.isin(from_DSS) & df_If_DSS.to_bus.isin(
                        to_DSS)].reset_index()
                Value_1_EST = round(float(filter['I1(pu)'] * Rii_If_PMU[index] + filter['I1(pu)']), 4)
                Value_2_EST = round(float(filter['I2(pu)'] * Rii_If_PMU[index] + filter['I2(pu)']), 4)
                Value_3_EST = round(float(filter['I3(pu)'] * Rii_If_PMU[index] + filter['I3(pu)']), 4)

                Angle_1_EST = round(float(filter['ang1(deg)'] * Rii_Vi_PMU[index] + filter['ang1(deg)']), 4)
                Angle_2_EST = round(float(filter['ang2(deg)'] * Rii_Vi_PMU[index] + filter['ang2(deg)']), 4)
                Angle_3_EST = round(float(filter['ang3(deg)'] * Rii_Vi_PMU[index] + filter['ang3(deg)']), 4)

                df_MEAS_PMU = df_MEAS_PMU.append(
                    {'Type': 9, 'Value1(pu)': Value_1_EST, 'Value2(pu)': Value_2_EST, 'Value3(pu)': Value_3_EST,
                     'Angle1(deg)': Angle_1_EST, 'Angle2(deg)': Angle_2_EST, 'Angle3(deg)': Angle_3_EST,
                     'From': filter['from_bus'][0], 'To': filter['to_bus'][0], 'Rii': Rii_If_PMU[index]},
                    ignore_index=True)

        df_MEAS_PMU = pd.merge(df_MEAS_PMU, data_DSS.allbusnames_aux(), how='left', left_on='From', right_on='bus_name')
        df_MEAS_PMU = pd.merge(df_MEAS_PMU, data_DSS.allbusnames_aux(), how='left', left_on='To', right_on='bus_name')
        df_MEAS_PMU = df_MEAS_PMU.drop(columns=['bus_name_x', 'bus_name_y'])
        df_MEAS_PMU = df_MEAS_PMU.rename(columns={'bus_name_aux_x': 'From_aux', 'bus_name_aux_y': 'To_aux'})
        df_MEAS_PMU = df_MEAS_PMU[['Type', 'Value1(pu)', 'Value2(pu)', 'Value3(pu)',
                                   'Angle1(deg)', 'Angle2(deg)', 'Angle3(deg)',
                                   'From', 'To', 'From_aux', 'To_aux', 'Rii']]
        df_MEAS_PMU = df_MEAS_PMU.fillna('')

        return df_MEAS_PMU
