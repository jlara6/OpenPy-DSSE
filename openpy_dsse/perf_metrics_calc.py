# -*- coding: utf-8 -*-
# @Time    : 30/12/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm
import pandas as pd
from .error_handling_logging import orient, indent

class performance_metrics:
    def __init__(self, V_Bus: pd.DataFrame, I_Elem: pd.DataFrame):
        self.V_Bus = V_Bus
        self.I_Elem = I_Elem

    def Mean_Absolute_Error(self):
        dict_MAE = dict()
        if not self.V_Bus.empty:
            n = len(self.V_Bus)
            sum_mod = 0
            sum_ang = 0
            for index, col in self.V_Bus.iterrows():
                sum_mod = abs(self.V_Bus['V1(pu)_DSS'][index] - self.V_Bus['V1(pu)_EST'][index])
                sum_ang = abs(self.V_Bus['Ang1(deg)_DSS'][index] - self.V_Bus['Ang1(deg)_EST'][index])
                sum_mod += sum_mod
                sum_ang += sum_ang
            dict_MAE['V1(pu)'] = format(sum_mod / n, '.2E')
            dict_MAE['AngV1(deg)'] = format(sum_ang / n, '.2E')

        if not self.I_Elem.empty:
            n = len(self.I_Elem)
            sum_mod = 0
            sum_ang = 0
            for index, col in self.I_Elem.iterrows():
                sum_mod = abs(self.I_Elem['I1(pu)_DSS'][index] - self.I_Elem['I1(pu)_EST'][index])
                sum_ang = abs(self.I_Elem['Ang1(deg)_DSS'][index] - self.I_Elem['Ang1(deg)_EST'][index])

                sum_mod += sum_mod
                sum_ang += sum_ang

            dict_MAE['I1(pu)'] = format(sum_mod / n, '.2E')
            dict_MAE['AngI1(deg)'] = format(sum_ang / n, '.2E')

        df_MAE = pd.DataFrame([[key, dict_MAE[key]] for key in dict_MAE.keys()], columns=['Variable', 'MAE'])
        return df_MAE

    def Mean_Absolute_Percentage_Error(self):
        dict_MAPE = dict()
        if not self.V_Bus.empty:
            n = len(self.V_Bus)
            sum_mod = 0
            sum_ang = 0
            for index, col in self.V_Bus.iterrows():
                sum_mod = abs(
                    self.V_Bus['V1(pu)_EST'][index] - self.V_Bus['V1(pu)_DSS'][index]
                ) / self.V_Bus['V1(pu)_DSS'][index]
                sum_ang = abs(
                    self.V_Bus['Ang1(deg)_EST'][index] - self.V_Bus['Ang1(deg)_DSS'][index]
                ) / self.V_Bus['Ang1(deg)_DSS'][index]
                sum_mod += sum_mod
                sum_ang += sum_ang
            dict_MAPE['V1(pu)'] = format(sum_mod / n, '.2E')
            dict_MAPE['AngV1(deg)'] = format(sum_ang / n, '.2E')

        if not self.I_Elem.empty:
            n = len(self.I_Elem)
            sum_mod = 0
            sum_ang = 0
            for index, col in self.I_Elem.iterrows():
                sum_mod = abs(
                    self.I_Elem['I1(pu)_EST'][index] - self.I_Elem['I1(pu)_DSS'][index]
                ) / self.I_Elem['I1(pu)_DSS'][index]
                sum_ang = abs(
                    self.I_Elem['Ang1(deg)_EST'][index] - self.I_Elem['Ang1(deg)_DSS'][index]
                ) / self.I_Elem['Ang1(deg)_DSS'][index]
                sum_mod += sum_mod
                sum_ang += sum_ang

            dict_MAPE['I1(pu)'] = format(sum_mod / n, '.2E')
            dict_MAPE['AngI1(deg)'] = format(sum_ang / n, '.2E')

        df_MAPE = pd.DataFrame([[key, dict_MAPE[key]] for key in dict_MAPE.keys()], columns=['Variable', 'MAPE'])

        return df_MAPE

    def Root_Mean_Square_Error(self):
        dict_RMSE = dict()
        if not self.V_Bus.empty:
            n = len(self.V_Bus)
            sum_mod = 0
            sum_ang = 0
            for index, col in self.V_Bus.iterrows():
                sum_mod = abs(
                    self.V_Bus['V1(pu)_EST'][index] - self.V_Bus['V1(pu)_DSS'][index]
                ) ** 2
                sum_ang = abs(
                    self.V_Bus['Ang1(deg)_EST'][index] - self.V_Bus['Ang1(deg)_DSS'][index]
                ) ** 2
                sum_mod += sum_mod
                sum_ang += sum_ang

            dict_RMSE['V1(pu)'] = format((sum_mod / n) ** 0.5, '.2E')
            dict_RMSE['AngV1(deg)'] = format((sum_ang / n) ** 0.5, '.2E')

        if not self.I_Elem.empty:
            n = len(self.I_Elem)
            sum_mod = 0
            sum_ang = 0
            for index, col in self.I_Elem.iterrows():
                sum_mod = abs(
                    self.I_Elem['I1(pu)_EST'][index] - self.I_Elem['I1(pu)_DSS'][index]
                ) ** 2
                sum_ang = abs(
                    self.I_Elem['Ang1(deg)_EST'][index] - self.I_Elem['Ang1(deg)_DSS'][index]
                ) ** 2
                sum_mod += sum_mod
                sum_ang += sum_ang


            dict_RMSE['I1(pu)'] = format((sum_mod / n) ** 0.5, '.2E')
            dict_RMSE['AngI1(deg)'] = format((sum_ang / n) ** 0.5, '.2E')

        df_RMSE = pd.DataFrame([[key, dict_RMSE[key]] for key in dict_RMSE.keys()], columns=['Variable', 'RMSE'])

        return df_RMSE

    def _dict_merge(
            self,
            MAE: bool,
            MAPE: bool,
            RMSE: bool,
            perf_dict: dict,
            View_res: bool,
            path_save: str,
            name_project: str
    ):
        if MAE and MAPE and RMSE:
            df_dict =perf_dict['MAE'].merge(perf_dict['MAPE'], on='Variable').merge(perf_dict['RMSE'], on='Variable')
        elif MAE and MAPE:
            df_dict = perf_dict['MAE'].merge(perf_dict['MAPE'], on='Variable')
        elif MAE and RMSE:
            df_dict = perf_dict['MAE'].merge(perf_dict['RMSE'], on='Variable')
        elif MAPE and RMSE:
            df_dict = perf_dict['MAPE'].merge(perf_dict['RMSE'], on='Variable')
        elif MAE:
            df_dict = perf_dict['MAE']
        elif MAPE:
            df_dict = perf_dict['MAPE']
        elif RMSE:
            df_dict = perf_dict['RMSE']

        if View_res:
            print(df_dict)
        if path_save is not None:
            df_dict.to_excel(f'{path_save}\Metrics_{name_project}.xlsx', index=False)
            df_dict_json = df_dict.to_json(orient=orient, indent=indent)
            with open(f"{path_save}\Metrics_{name_project}.json", "w") as outfile:
                outfile.write(df_dict_json)
        return df_dict