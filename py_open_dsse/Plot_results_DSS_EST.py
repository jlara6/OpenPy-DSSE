# -*- coding: utf-8 -*-
# @Time    : 18/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from .OpenDSS_data_extraction import *

class Plot_results_EST:

    def __init__(self, name_project: str, path_save: str, no_PU: bool = False, MAPE: bool = False, MAE: bool = False,
                 RMSE: bool = False):

        self.no_PU = no_PU
        self.MAPE = MAPE
        self.MAE = MAE
        self.RMSE = RMSE
        self.path_save = path_save
        self.name_project = name_project

    def Vi_Angi_1ph(self, V_Ang_from_DSS: pd.DataFrame, df_Results_DSSE: pd.DataFrame, Vi_DSS_EST: bool = False):
        '''

        :param V_Ang_from_DSS:
        :param df_Results_DSSE:
        :param Vi_DSS_EST:
        :param Vi_MAPE:
        :param self.in_PU:
        :param self.no_PU:
        :return:
        '''

        'calculation between actual and addresses_algorithm and drawing of errors'
        'Voltage'
        V_Ang_from_DSS = V_Ang_from_DSS.drop(
            ['num_nodes', 'ph_1', 'ph_2', 'ph_3', 'V2(pu)', 'V3(pu)', 'Ang2(deg)', 'Ang3(deg)'], axis=1)

        df_Vi_pu = V_Ang_from_DSS.merge(df_Results_DSSE, on='Bus Nro.')
        df_Vi_pu = df_Vi_pu.rename(columns={'V1(pu)_x': 'V1(pu)_DSS', 'Ang1(deg)_x': 'Ang1(deg)_DSS',
                                            'V1(pu)_y': 'V1(pu)_EST', 'Ang1(deg)_y': 'Ang1(deg)_EST',
                                            'bus_name': 'Bus name'})

        df_Vi_no_pu = df_Vi_pu.copy()
        df_Vi_no_pu = df_Vi_no_pu.rename(
            columns={'V1(pu)_EST': 'V1(kV)_EST', 'V1(pu)_DSS': 'V1(kV)_DSS'})

        for index, row in df_Vi_pu.iterrows():
            dss.circuit_set_active_bus(df_Vi_pu['Bus name'][index])
            kVbase = dss.bus_kv_base()
            df_Vi_no_pu['V1(kV)_EST'][index] = df_Vi_pu['V1(pu)_EST'][index] * kVbase
            df_Vi_no_pu['V1(kV)_DSS'][index] = df_Vi_pu['V1(pu)_DSS'][index] * kVbase

        if Vi_DSS_EST == True:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            df_Vi_pu[['Bus name', 'V1(pu)_DSS', 'V1(pu)_EST']].plot(kind='line', x='Bus name', ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            df_Vi_pu[['Bus name', 'Ang1(deg)_DSS', 'Ang1(deg)_EST']].plot(kind='bar', x='Bus name', ax=ax2)
            fig.suptitle('Voltage and angle of the state estimator and OpenDSS')
            ##fig.tight_layout()
            plt.savefig(f'{self.path_save}./Vi_DSS_EST_PU_{self.name_project}.png')

            if self.no_PU == True:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
                fig.suptitle('Voltage and angle of the state estimator and OpenDSS')
                df_Vi_no_pu[['Bus name', 'V1(kV)_DSS', 'V1(kV)_EST']].plot(kind='line', x='Bus name', ax=ax1)
                ax1.tick_params(axis='x', rotation=90)
                df_Vi_no_pu[['Bus name', 'Ang1(deg)_DSS', 'Ang1(deg)_EST']].plot(kind='bar', x='Bus name', ax=ax2)
                fig.suptitle('Voltage and angle of the state estimator and OpenDSS')
                ##fig.tight_layout()

                plt.savefig(f'{self.path_save}./Vi_DSS_EST_no_PU_{self.name_project}.png')

        if self.MAPE == True:
            error = pd.DataFrame()
            error['Error V(%)'] = ((df_Vi_pu['V1(pu)_EST'] - df_Vi_pu['V1(pu)_DSS']).abs() / (
                df_Vi_pu['V1(pu)_DSS']).abs()) * 100
            error['Error Ang(%)'] = (((df_Vi_pu['Ang1(deg)_EST'] + 100) - (df_Vi_pu['Ang1(deg)_DSS'] + 100)).abs() / (
                (df_Vi_pu['Ang1(deg)_DSS'] + 100)).abs()) * 100
            error['Bus'] = df_Vi_pu['Bus name']

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Mean Absolute Percentage Error (MAPE) of voltage and angle')
            sns.barplot(data=error, x='Bus', y='Error V(%)', palette="rocket", ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            sns.barplot(data=error, x='Bus', y='Error Ang(%)', palette="rocket", ax=ax2)
            ax2.tick_params(axis='x', rotation=90)
            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Vi_MAPE_{self.name_project}.png')

        if self.MAE == True:
            error = pd.DataFrame()
            error['Error V(%)'] = (df_Vi_pu['V1(pu)_EST'] - df_Vi_pu['V1(pu)_DSS']).abs()
            error['Error Ang(%)'] = ((df_Vi_pu['Ang1(deg)_EST'] + 100) - (df_Vi_pu['Ang1(deg)_DSS'] + 100)).abs()
            error['Bus'] = df_Vi_pu['Bus name']

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Mean absolute error (MAE) of voltage and angle')
            sns.barplot(data=error, x='Bus', y='Error V(%)', palette="rocket", ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            sns.barplot(data=error, x='Bus', y='Error Ang(%)', palette="rocket", ax=ax2)
            ax2.tick_params(axis='x', rotation=90)
            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Vi_MAE_{self.name_project}.png')

        if self.RMSE == True:
            error = pd.DataFrame()
            error['Error V(%)'] = ((df_Vi_pu['V1(pu)_EST'] - df_Vi_pu['V1(pu)_DSS']) ** 2) ** 0.5
            error['Error Ang(%)'] = ((df_Vi_pu['Ang1(deg)_EST']) - (df_Vi_pu['Ang1(deg)_DSS']) ** 2) ** 0.5
            error['Bus'] = df_Vi_pu['Bus name']

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Root Mean Square Error (RMSE) of voltage and angle')
            sns.barplot(data=error, x='Bus', y='Error V(%)', palette="rocket", ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            sns.barplot(data=error, x='Bus', y='Error Ang(%)', palette="rocket", ax=ax2)
            ax2.tick_params(axis='x', rotation=90)

            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Vi_RMSE_{self.name_project}.png')

    def Iij_Angij_1ph(self, I_elem_pu_DSS: pd.DataFrame, DF_currents_estimate: pd.DataFrame, SbasMVA_3ph: float):

        I_ang_pu = I_elem_pu_DSS.merge(DF_currents_estimate, on='element_name')
        I_ang_pu = I_ang_pu.drop(columns=['from_bus_y', 'to_bus_y'])
        I_ang_pu = I_ang_pu.rename(
            columns={'from_bus_x': 'from_bus', 'to_bus_y': 'to_bus',
                     'I1(pu)_x': 'I1(pu)_DSS', 'ang1(deg)_x': 'ang1(deg)_DSS',
                     'I1(pu)_y': 'I1(pu)_EST', 'ang1(deg)_y': 'ang1(deg)_EST',
                     'element_name': 'Element name'})
        I_ang_pu['Element name'] = I_ang_pu['Element name'].replace({'Line.': ''}, regex=True)

        'Current and angle graph in unit values'
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
        fig.suptitle('Current and angle of the state estimator and OpenDSS')
        I_ang_pu[['Element name', 'I1(pu)_DSS', 'I1(pu)_EST']].plot(kind='line', x='Element name', ax=ax1)
        ax1.tick_params(axis='x', rotation=90)
        I_ang_pu[['Element name', 'ang1(deg)_DSS', 'ang1(deg)_EST']].plot(kind='bar', x='Element name', ax=ax2)
        # fig.tight_layout()
        plt.savefig(f'{self.path_save}./Iij_DSS_EST_PU_{self.name_project}.png')

        if self.no_PU == True:
            I_ang_no_pu = I_ang_pu.copy()
            I_ang_no_pu = I_ang_no_pu.rename(
                columns={'I1(pu)_EST': 'I1(A)_EST', 'I1(pu)_DSS': 'I1(A)_DSS'})

            for index, row in I_ang_no_pu.iterrows():
                dss.circuit_set_active_bus(I_ang_no_pu['from_bus'][index])
                kVbase = dss.bus_kv_base()
                Ibas = ((SbasMVA_3ph / 3) * 1000) / kVbase
                I_ang_no_pu['I1(A)_EST'][index] = I_ang_no_pu['I1(A)_EST'][index] * Ibas
                I_ang_no_pu['I1(A)_DSS'][index] = I_ang_no_pu['I1(A)_DSS'][index] * Ibas

            'Current and angle graph in real values'
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Current and angle of the state estimator and OpenDSS')
            I_ang_no_pu[['Element name', 'I1(A)_DSS', 'I1(A)_EST']].plot(kind='line', x='Element name', ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            I_ang_no_pu[['Element name', 'ang1(deg)_DSS', 'ang1(deg)_EST']].plot(kind='bar', x='Element name', ax=ax2)
            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Iij_DSS_EST_no_PU_{self.name_project}.png')

        if self.MAPE == True:
            error = pd.DataFrame()
            error['Element name'] = I_ang_pu['Element name']
            error['Error |I|(%)'] = ((I_ang_pu['I1(pu)_EST'] - I_ang_pu['I1(pu)_DSS']).abs() / (
                I_ang_pu['I1(pu)_DSS']).abs()) * 100
            error['Error Ang(%)'] = ((I_ang_pu['ang1(deg)_EST'] - I_ang_pu['ang1(deg)_DSS']).abs() / (
                I_ang_pu['ang1(deg)_DSS']).abs()) * 100

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Mean Absolute Percentage Error (MAPE) of current and angle')
            sns.barplot(data=error, x='Element name', y='Error |I|(%)', palette="rocket", ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            sns.barplot(data=error, x='Element name', y='Error Ang(%)', palette="rocket", ax=ax2)
            ax2.tick_params(axis='x', rotation=90)
            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Iij_MAPE_{self.name_project}.png')

        if self.MAE == True:
            error = pd.DataFrame()
            error['Element name'] = I_ang_pu['Element name']
            error['Error |I|(pu)'] = (I_ang_pu['I1(pu)_EST'] - I_ang_pu['I1(pu)_DSS']).abs()
            error['Error Ang(deg)'] = ((I_ang_pu['ang1(deg)_EST'] + 100) - (I_ang_pu['ang1(deg)_DSS'] + 100)).abs()

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Mean absolute error (MAE) of current and angle')
            sns.barplot(data=error, x='Element name', y='Error |I|(pu)', palette="rocket", ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            sns.barplot(data=error, x='Element name', y='Error Ang(deg)', palette="rocket", ax=ax2)
            ax2.tick_params(axis='x', rotation=90)
            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Iij_MAE_{self.name_project}.png')

        if self.RMSE == True:
            error = pd.DataFrame()
            error['Element name'] = I_ang_pu['Element name']
            error['Error |I|(pu)'] = ((I_ang_pu['I1(pu)_EST'] - I_ang_pu['I1(pu)_DSS']) ** 2) ** 0.5
            error['Error Ang(deg)'] = ((I_ang_pu['ang1(deg)_EST']) - (I_ang_pu['ang1(deg)_DSS']) ** 2) ** 0.5

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), sharex=True)
            fig.suptitle('Root Mean Square Error (RMSE) of current and angle')
            sns.barplot(data=error, x='Element name', y='Error |I|(pu)', palette="rocket", ax=ax1)
            ax1.tick_params(axis='x', rotation=90)
            sns.barplot(data=error, x='Element name', y='Error Ang(deg)', palette="rocket", ax=ax2)
            ax2.tick_params(axis='x', rotation=90)
            # fig.tight_layout()
            plt.savefig(f'{self.path_save}./Iij_RMSE_{self.name_project}.png')