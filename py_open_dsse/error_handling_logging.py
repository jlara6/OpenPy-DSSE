# -*- coding: utf-8 -*-
# @Time    : 12/10/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import logging
import os
import pandas as pd
from colorama import init, Fore, Back, Style

script_path = os.path.dirname(os.path.abspath(__file__))
logger_aux = logging.getLogger(__name__)

orient, indent = "index", 1
to_Excel_MEAS = False
Logg_option = False


def update_logg_file(msg: str, Typ: int = 0, logger=logger_aux, Logg: bool = Logg_option, Print: bool = True):
    """
    Creates or updates the log_py file. In addition, it prints the message formatted according to the type.

    :param msg: Message text to be displayed by console or saved in the log_py file
    :param logger: From function logging.getLogger(__name__)
    :param Typ: May be: 0(pass), 1(debug), 2(info) 3(warning), 4(error), and 5 (critical). Default=0
    :param Logg: boolean to enable or disable log_py file. Default=True
    :param Print: Display the message by console. Default=True
    :return: py_open_dsse.log_py
    """
    if Logg == True:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(msg)s'
        # To override the default severity of logging
        logger.setLevel('DEBUG')
        # logger = logging.getLogger(__name__)

        # Use FileHandler() to log_py to a file
        file_handler = logging.FileHandler(f"{script_path}\py_open_dsse.log")
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)

        # Don't forget to add the file handler
        logger.addHandler(file_handler)
        if Typ == 1:
            logger.debug(msg)
        if Typ == 2:
            logger.info(msg)
        if Typ == 3:
            logger.warning(msg)
        if Typ == 4:
            logger.error(msg)
        if Typ == 5:
            logger.critical(msg)

    if Print == True:
        if Typ == 0:
            print(Style.DIM + msg)
        else:
            #print('_' * 64)
            if Typ == 1:
                'debug'
                print(Style.NORMAL + msg + Style.RESET_ALL)
            if Typ == 2:
                'info'
                print(Style.BRIGHT + msg + Style.RESET_ALL)
            if Typ == 3:
                'warning'
                print(Fore.YELLOW + msg + Style.RESET_ALL)
            if Typ == 4:
                'error'
                print(Fore.RED + msg + Style.RESET_ALL)
            if Typ == 5:
                'critical'
                print(Fore.RED + Style.BRIGHT + msg + Style.RESET_ALL)

def empty_init_files_MEAS_SD_EH(DSS_path, path_save, log_py):
    aux_DSS = DSS_path is None
    aux_path = path_save is None

    if aux_DSS and aux_path:
        update_logg_file('Error\nYou must enter the OpenDSS file address and a path to save the file.', 4, log_py)
        exit()
    elif aux_DSS:
        update_logg_file('Error\nYou must enter the OpenDSS file path.', 4, log_py)
        exit()
    elif aux_path:
        update_logg_file('Error\nYou must indicate a path where the .json files will be saved.', 4, log_py)
        exit()

def add_error_file_MEAS_EH(DSS_path, path_save, log_py):
    aux_DSS = DSS_path is None
    aux_path = path_save is None

    if aux_DSS and aux_path:
        update_logg_file(
            'Error\nYou must enter: DSS_path, MEAS_path. More information in the documentation', 5, log_py)
        exit()
    elif aux_DSS:
        update_logg_file('Error\nYou must enter the OpenDSS file path.', 4, log_py)
        exit()

    elif aux_path:
        update_logg_file('Error\nYou must enter a path for saving the file.', 4, log_py)
        exit()

def empty_MEAS_files_EH(DSS_path, path_save, log_py):
    aux_DSS = DSS_path is None
    aux_path = path_save is None

    if aux_DSS and aux_path:
        update_logg_file('Error\nYou must enter the OpenDSS file address and a path to save the file.', 4, log_py)
        exit()
    elif aux_DSS:
        update_logg_file('Error\nYou must enter the OpenDSS file path.', 4, log_py)
        exit()
    elif aux_path:
        update_logg_file('Error\nYou must indicate a path where the .json files will be saved.', 4, log_py)
        exit()

def estimate_EH(DSS_path, MEAS_path, path_save, Typ_cir, MEAS_SeqPos_path, log_py):
    pass


def _excel_json(excel_name, save_path, option):
    df_Bus_i = pd.read_excel(f'{save_path}\{excel_name}.xlsx', sheet_name='Bus_i')
    df_Elem_ft = pd.read_excel(f'{save_path}\{excel_name}.xlsx', sheet_name='Elem_ft')
    df_Bus_i_PMU = pd.read_excel(f'{save_path}\{excel_name}.xlsx', sheet_name='Bus_i_PMU')
    df_Elem_ft_PMU = pd.read_excel(f'{save_path}\{excel_name}.xlsx', sheet_name='Elem_ft_PMU')

    if option == 'init':
        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\Init_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\Init_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\Init_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\Init_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)

    elif option == 'meas':
        Bus_i_init = df_Bus_i.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\MEAS_Bus_i.json", "w") as outfile:
            outfile.write(Bus_i_init)

        Elem_ft_init = df_Elem_ft.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\MEAS_Elem_ft.json", "w") as outfile:
            outfile.write(Elem_ft_init)

        Bus_i_PMU_init = df_Bus_i_PMU.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\MEAS_Bus_i_PMU.json", "w") as outfile:
            outfile.write(Bus_i_PMU_init)

        Elem_ft_PMU_init = df_Elem_ft_PMU.to_json(orient=orient, indent=indent)
        with open(f"{save_path}\MEAS_Elem_ft_PMU.json", "w") as outfile:
            outfile.write(Elem_ft_PMU_init)
