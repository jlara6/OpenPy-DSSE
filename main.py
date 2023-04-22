import openpy_dsse
from sympy.integrals.rubi.utility_function import Rest

dsse = openpy_dsse.init_DSSE(
    init_values='flat'
) #Start the class.

if __name__ == '__main__':
    net = dsse.test_circuit(
        Typ_cir='1ph',
        case=2
    )
    #net = dsse.test_circuit(Typ_cir='Pos', case=2)

    dsse.empty_MEAS_files(DSS_path=net['DSS_file'], MEAS_path=net['MEAS_path'])
    #dsse.empty_init_files_MEAS_Unc(DSS_path=net['DSS_file'], MEAS_path_save=net['MEAS_path'])
    dsse.add_error_files_MEAS(
        DSS_path=net['DSS_file'],
        MEAS_path=net['MEAS_path']
    )

    #execute the state estimation algorithm
    V_Ang_EST = dsse.estimate(
        DSS_path=net['DSS_file'],
        MEAS_path=net['MEAS_path'],
        path_save=net['save_path'],
        Typ_cir=net['Typ_cir'],
        name_project=net['name_project'],
        View_res=True,
        summary=True,
        DSS_coll=True,
        MEAS_Pos=True,
        #method='nonlinear'
        #method='linear_PMU',
    )
    I_Angle_EST = dsse.param_elect_from_EST(
        EST_df=V_Ang_EST['df_EST'],
        I_Ang_EST=True,
        View_res=False,
        name_project=net['name_project'],
        path_save=net['save_path'],
    )
    metrics = dsse.performance_metrics(
        V_Bus=V_Ang_EST,
        I_Elem=I_Angle_EST,
        MAPE=True,
        MAE=True,
        RMSE=True,
        name_project=net['name_project'],
        path_save=net['save_path']
    )
    dsse.Plot_results(
        V_Bus=V_Ang_EST,
        I_Elem=I_Angle_EST,
        name_project=net['name_project'],
        path_save=net['save_path'],
        View=False
    )

