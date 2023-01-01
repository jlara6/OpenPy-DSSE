# -*- coding: utf-8 -*-
# @Time    : 18/08/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from .OpenDSS_data_extraction import *

class _Plot_results_DSS_EST:
    def __init__(
            self,
            name_project: str,
            path_save: str,
            no_PU: bool,
            View: bool
    ):
        self.no_PU = no_PU
        self.path_save = path_save
        self.name_project = name_project
        self.View = View

    def _Vi_Angi_1ph_Pos(
            self,
            df_DSS_EST: pd.DataFrame
    ):
        df_DSS_EST = df_DSS_EST.rename(columns={'bus_name': 'Bus name'})
        if self.no_PU:
            df_Vi_no_pu = df_DSS_EST.copy()
            for index, row in df_DSS_EST.iterrows():
                dss.circuit_set_active_bus(df_DSS_EST['Bus name'][index])
                kVbase = dss.bus_kv_base()
                df_Vi_no_pu['V1(kV)_EST'][index] = df_DSS_EST['V1(pu)_EST'][index] * kVbase
                df_Vi_no_pu['V1(kV)_DSS'][index] = df_DSS_EST['V1(pu)_DSS'][index] * kVbase
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 7))
            df1 = pd.melt(
                df_DSS_EST,
                id_vars=['Bus name'],
                value_vars=['V1(kV)_DSS', 'V1(kV)_EST'])
            df1['Bus name'] = df1['Bus name'].astype(str)
            sns.lineplot(
                x="Bus name",
                hue="variable",
                y="value",
                data=df1,
                ax=axes[0],
                palette='deep')
            axes[0].set_ylabel('kV')
            axes[0].legend(loc='best')
            axes[0].tick_params(axis='x', rotation=90)
            axes[0].grid(axis='y', linestyle='--', linewidth=0.5)

            df2 = pd.melt(
                df_DSS_EST,
                id_vars=['Bus name'],
                value_vars=['Ang1(deg)_DSS', 'Ang1(deg)_EST'])
            df2['Bus name'] = df2['Bus name'].astype(str)
            sns.lineplot(
                x="Bus name",
                hue="variable",
                y="value",
                data=df2,
                ax=axes[1],
                palette='deep')
            axes[1].set_ylabel('deg')
            axes[1].legend(loc='best')
            axes[1].tick_params(axis='x', rotation=90)
            axes[1].grid(axis='y', linestyle='--', linewidth=0.5)
            if self.path_save is not None:
                plt.savefig(f'{self.path_save}./Vi_DSS_EST_PU_{self.name_project}.png')
            if self.View:
                plt.show()
        else:
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 7))
            df1 = pd.melt(
                df_DSS_EST,
                id_vars=['Bus name'],
                value_vars=['V1(pu)_DSS', 'V1(pu)_EST'])
            df1['Bus name'] = df1['Bus name'].astype(str)
            sns.lineplot(
                x="Bus name",
                hue="variable",
                y="value",
                data=df1,
                ax=axes[0],
                palette='deep')
            axes[0].set_ylabel('p.u.')
            axes[0].legend(loc='best')
            axes[0].tick_params(axis='x', rotation=90)
            axes[0].grid(axis='y', linestyle='--', linewidth=0.5)

            df2 = pd.melt(
                df_DSS_EST,
                id_vars=['Bus name'],
                value_vars=['Ang1(deg)_DSS', 'Ang1(deg)_EST'])
            df2['Bus name'] = df2['Bus name'].astype(str)
            sns.lineplot(
                x="Bus name",
                hue="variable",
                y="value",
                data=df2,
                ax=axes[1],
                palette='deep')
            axes[1].set_ylabel('deg')
            axes[1].legend(loc='best')
            axes[1].tick_params(axis='x', rotation=90)
            axes[1].grid(axis='y', linestyle='--', linewidth=0.5)
            if self.path_save is not None:
                plt.savefig(f'{self.path_save}./Vi_DSS_EST_PU_{self.name_project}.png')
            if self.View:
                plt.show()
    def _Iij_Angij_1ph_Pos(
            self,
            df_DSS_EST: pd.DataFrame,
            SbasMVA_3ph: float = None):
        df_DSS_EST = df_DSS_EST.rename(
            columns={'element_name': 'Element name'}
        )
        df_DSS_EST['Element name'] = df_DSS_EST['Element name'].replace({'Line.': ''}, regex=True)
        if self.no_PU == True:
            I_ang_no_pu = df_DSS_EST.copy()
            I_ang_no_pu = I_ang_no_pu.rename(
                columns={'I1(pu)_EST': 'I1(A)_EST', 'I1(pu)_DSS': 'I1(A)_DSS'}
            )
            for index, row in I_ang_no_pu.iterrows():
                dss.circuit_set_active_bus(I_ang_no_pu['from_bus'][index])
                kVbase = dss.bus_kv_base()
                Ibas = ((SbasMVA_3ph / 3) * 1000) / kVbase
                I_ang_no_pu['I1(A)_EST'][index] = I_ang_no_pu['I1(A)_EST'][index] * Ibas
                I_ang_no_pu['I1(A)_DSS'][index] = I_ang_no_pu['I1(A)_DSS'][index] * Ibas
            fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 7))
            df1 = pd.melt(
                df_DSS_EST,
                id_vars=['Element name'],
                value_vars=['I1(A)_DSS', 'I1(A)_EST'])
            df1['Element name'] = df1['Element name'].astype(str)
            sns.lineplot(
                x="Bus name",
                hue="variable",
                y="value",
                data=df1,
                ax=axes[0],
                palette='deep')
            axes[0].set_ylabel('A')
            axes[0].legend(loc='best')
            axes[0].tick_params(axis='x', rotation=90)
            axes[0].grid(axis='y', linestyle='--', linewidth=0.5)
            df2 = pd.melt(
                df_DSS_EST,
                id_vars=['Element name'],
                value_vars=['Ang1(deg)_DSS', 'Ang1(deg)_EST'])
            df2['Element name'] = df2['Element name'].astype(str)
            sns.lineplot(
                x="Bus name",
                hue="variable",
                y="value",
                data=df2,
                ax=axes[1],
                palette='deep')
            axes[1].set_ylabel('deg')
            axes[1].legend(loc='best')
            axes[1].tick_params(axis='x', rotation=90)
            axes[1].grid(axis='y', linestyle='--', linewidth=0.5)
            if self.path_save is not None:
                plt.savefig(f'{self.path_save}./Iij_DSS_EST_no_PU_{self.name_project}.png')
            if self.View:
                plt.show()
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 7))
        df1 = pd.melt(
            df_DSS_EST,
            id_vars=['Element name'],
            value_vars=['I1(pu)_DSS', 'I1(pu)_EST'])
        df1['Element name'] = df1['Element name'].astype(str)
        sns.lineplot(
            x="Element name",
            hue="variable",
            y="value",
            data=df1,
            ax=axes[0],
            palette='deep')
        axes[0].set_ylabel('p.u.')
        axes[0].legend(loc='best')
        axes[0].tick_params(axis='x', rotation=90)
        axes[0].grid(axis='y', linestyle='--', linewidth=0.5)
        df2 = pd.melt(
            df_DSS_EST,
            id_vars=['Element name'],
            value_vars=['Ang1(deg)_DSS', 'Ang1(deg)_EST'])
        df2['Element name'] = df2['Element name'].astype(str)
        sns.lineplot(
            x="Element name",
            hue="variable",
            y="value",
            data=df2,
            ax=axes[1],
            palette='deep')
        axes[1].set_ylabel('deg')
        axes[1].legend(loc='best')
        axes[1].tick_params(axis='x', rotation=90)
        axes[1].grid(axis='y', linestyle='--', linewidth=0.5)
        if self.path_save is not None:
            plt.savefig(f'{self.path_save}./Iij_DSS_EST_no_PU_{self.name_project}.png')
        if self.View:
            plt.show()