import py_open_dsse

dsse = py_open_dsse.init_DSSE() #Start the class.

if __name__ == '__main__':
    pass
    net = dsse.test_circuit(Typ_cir='Pos', case=1)

    #dsse.empty_MEAS_files(DSS_path=net['DSS_file'], MEAS_path=net['MEAS_path'])
    #dsse.empty_init_files_MEAS_Unc(DSS_path=net['DSS_file'], MEAS_path_save=net['MEAS_path'])
    dsse.add_error_files_MEAS(DSS_path=net['DSS_file'], MEAS_path=net['MEAS_path'])

    #execute the state estimation algorithm
    Results = dsse.estimate(
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


