# py_open_dsse

It is an open-source library developed in Python for estimating distribution networks (DSSE). It communicates with the free software for the simulation of electrical networks (OpenDSS) and collects the results of power flow and distribution system parameters and executes the DSSE, obtaining an estimated state according to the type and location of measurements.

It is developed within the framework of the OpenREiD project (Integral software for simulation and optimization of electrical distribution networks), of the Instituto de Energía Eléctrica (IEE), UNSJ - CONICET, San Juan - Argentina.

**Index**

- [Installation](#id1)
- [How to use](#id2)
  - [Measurements](#id3)
    - [Definition and creation of meters](#id4)
    - [Generate metrics from OpenDSS results](#id5)
  - [Run the state estimation algorithm](#id6)
  - [Sample tests](#id7)
- [License](#id8)

<div id='id1' />
## Installation

With pip

``pip install py-open-dsse``

Without pip, clone or download the repository, in the dist folder is the .whl file, copy the location of the file, and in the CMD:

``pip install {path-save-files}/py_open_dsse-{version}-py3-none-any.whl’``

<div id='id2'/>

## How to use  <a name="id1"></a>

First, in the IDE (Integrated Development Environment) of preference, we import the library:

```Python
import py_open_dsse
```

The object class that contains all the functions of the library is activated as follows:

```Python
dsse = py_open_dsse.init_DSSE()
```

The class ``init_DSSE()``, has default values as shown in table 1 and can be modified as appropriate.

**Table 1.** Description and attributes of function ``init_DSSE()``
| **Parameters** | **Description** | **Default value** |
|:---:|---|:---:|
| ``Sbas3ph_MVA`` | Three-phase system base power     | ``30`` |
| ``tolerance`` | Convergence tolerance of selected algorithm | ``1e-3`` |
| ``max_iter`` | Maximum number of iterations of the selected algorithm | ``30`` |
| ``init_values`` | Initial values for state estimation. With ``flat`` start with 1.0 p.u. / 0° on all buses and with ``dss`` start with OpenDSS voltage and angle results| ``flat`` |

Once the class is initialized, we can use the functions described below.

<div id='id3' />

### Measurements

<div id='id4' />

#### Definition and creation of meters

The library supports meters and their respective error variance described in Table 2.

**Tabla 2.** Measurement type of the ``py_open_dsse`` library.

|              **Meter**                 |                                **Description**                |
|:--------------------------------------:|---------------------------------------------------------------|
| $\left\|V_{i}\right\|$                 | Node voltage magnitude.                                       |
| $PQ_{ft}$                              | Branch power flow                                             |
| $\left\|I_{ft}\right\|$                | Magnitude of branch current.                                  |
| $PQ_{i}^{SM}$                          | Injection power or node consumption obtained by a smart meter |
| $PQ_{i}^{0}$                           | Passive node or zero injection power.                         |
| $PQ_{i}^{PSD}$                         | Artificial node injection power known as pseudo-measurement   |
| $\left\|V_{i}\right\|\angle \theta$    | Voltage phasor measurement                                    |
| $\left\|I_{ft}\right\|\angle \delta$   | Current phasor measurement                                              |

The measurement data per phase **𝜌 (1, 2, 3)** and measurement error variance ``Rii`` of a network modeled in OpenDSS. They must be entered in the ``MEAS_Bus_i.json``, ``MEAS_Elem_ft.json``, ``MEAS_Bus_i_PMU.json`` and ``MEAS_Elem_ft_PMU.json`` files. The ``.json`` measurement files without data are generated with the ``empty_MEAS_files()`` function and the parameters from table 3 must be entered.

**Table 3.** Parameters and description of ``empty_file_MEAS()`` function
|    **Parameter**   |                           **Description**                         |**Default value** |
|:------------------:|-------------------------------------------------------------------|:----------------:|
| ``DSS_path``       | A path of the ``.DSS`` files of the circuit modeled in OpenDSS    | ``None ``        |
| ``MEAS_path_save`` | Path where the measurement ``.json`` files will be saved          | ``None ``        |

The description of the identifiers that can be modified is detailed in tables 4, 5, 6, and 7. The other identifiers in the ``.json`` files, are node characteristics or elements extracted from the circuit modeled in OpenDSS, these data should not be modified since they would affect the result of the state estimation algorithm.

**Table 4.** Description of identifiers of the ``MEAS_Bus_i.json`` file.

| **Identifier**     |                                       **Description**                         |
|:---------------------:|-------------------------------------------------------------------------------|
| ``STS_Vm``            | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_Vm``            | Variance of voltage magnitude measurement error.                              |
| ``Vρm(pu)``           | Measurement of voltage magnitude voltage in phase 𝜌.                          |
| ``STS_PQd(SM)``       | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_SM``            | Measurement error variance of injection power or consumption of a smart meter.|
| ``STS_PQd(0)``        | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_0``             | Zero or passive injection power measurement error variance.                   |
| ``STS_PQd(Psd)``      | Status (1: Enabled, 0: Disabled)                                              |
| ``Rii_Psd``           | Measurement error variance of pseudo power injection measurement              |
| ``Pρmd(pu)``          | Measurement of active power injection in phase 𝜌.                             |
| ``Qρmd(pu)``          | Measurement of reactive power injection in phase 𝜌.                           |

**Table 5.** Description of identifiers of the ``MEAS_Elem_ft.json`` file.

| **Identifier**        | **Description**                                    |
|:---------------------:|----------------------------------------------------|
| ``STS_PQft``          | Status (1: Enabled, 0: Disabled)                   |
| ``Rii_PQft``          | Branch power flow measurement error variance.      |
| ``Pρmft(pu)``         | Measurement of branch active power in phase 𝜌.     |
| ``Qρmft(pu)``         | Measurement of branch reactive power in phase 𝜌.   |
| ``STS_Ift``           | Status (1: Enabled, 0: Disabled)                   |
| ``Rii_Ift``           | Branch current magnitude error variance.           |
| ``Iρmft(pu)``         | Measurement of branch current magnitude in phase 𝜌.|

**Table 6.** Description of identifiers of the ``MEAS_Elem_ft_PMU.json`` file.
| **Identifier**     |                   **Description**           |
|:---------------------:|---------------------------------------------|
| ``STS_Vm``            | Status (1: Enabled, 0: Disabled)            |
| ``Rii_Vm``            | Variance of voltage phasor measurement error|
| ``Vρm(pu)``           | Measurement of voltage magnitude in phase 𝜌 |
| ``Angρm(deg)``        | Measurement of volage angle in phase 𝜌      |

**Table 7.** Description of identifiers of the ``MEAS_Elem_ft_PMU.json`` file.
| **Identifier**    |                 **Description**             |
|:-----------------:|---------------------------------------------|
| ``STS_Ift``       | Status (1: Enabled, 0: Disabled)            |
| ``Rii_Ift``       | Variance of current phasor measurement error|
| ``Iρmft(pu)``     | Measurement of current magnitude in phase 𝜌 |
| ``Angρm(deg)``    | Measurement of current angle in phase 𝜌     |

<div id='id5' />

#### Generate metrics from OpenDSS results

##### Initial measurements with uncertainty of measurement error

The ``empty_init_files_MEAS_Unc()`` function generates ``.json`` files where all the nodes and elements that can participate as measurement in the state estimation algorithm are placed. For this purpose, the parameters of table 8 must be specified.

**Table 8.** Parameters and description of ``empty_file_MEAS()`` function
|    **Parameters**   |                           **Description**                     | **Default value** |
|:------------------:|----------------------------------------------------------------|:-----------------:|
| ``DSS_path``       | A path of the ``.DSS`` files of the circuit modeled in OpenDSS | ``None``          |
| ``MEAS_path_save`` | Path where the measurement ``.json`` files will be saved       | ``None``          |

In the ``MEAS_path_save`` path, it generates the files ``Init_Bus_i.json``, ``Init_Elem_ft.json``, ``Init_Bus_i_PMU.json`` and ``Init_Elem_ft_PMU.json``. Depending on the case study, the ``STS`` meter status (1: Enabled, 0: Disabled) and the measurement error rate in ``Unc(%)`` can be modified.

##### Adding random errors and generating measurement files

With the ``.json`` files generated by the ``empty_file_MEAS()`` function and the changes indicated by the user, with the ``add_error_file_MEAS()`` function and the Parameters described in Table 9.

**Table 9.** Atributos de la función ``add_error_files_MEAS()``
| **Parameters** |                        **Description**                        | **Default value**|
|:--------------:|---------------------------------------------------------------|:----------------:|
| ``DSS_path``   | A path of the ``.DSS`` files of the circuit modeled in OpenDSS| ``None``         |
| ``MEAS_path``  | Path of initial ``.json`` files                               | ``None``         |
| ``seed_DS``    | Random error generation seed                                  | ``1``            |

Adds random errors from a normal distribution to the OpenDSS power flow results, for use as a measurement. The result of generating random errors is contained in the files ``MEAS_Bus_i.json``, ``MEAS_Elem_ft.json``, ``MEAS_Bus_i_PMU.json`` and ``MEAS_Elem_ft_PMU.json``, stored in ``MEAS_path``.

<div id='id6' />

### Run the state estimation algorithm

To run the state estimation algorithm, function ``estimate()`` is called, it is necessary to enter or change parameters detailed in table 10. 

**Table 10.** Parameters and description of ``estimate()`` function

|   **Parameters** |                                   **Description**                                  | **Default value** |
|:----------------:|------------------------------------------------------------------------------------|:---------------------:|
| ``DSS_path``     | A path of the ``.DSS`` files of the circuit modeled in OpenDSS.                    | ``None``              |
| ``MEAS_path``    | Path where measurement files are located.                                          | ``None``              |
| ``path_save``    | Path where the results will be saved                                               | ``None``              |
| ``Typ_cir``      | Circuit type, can be ``1ph`` or ``Pos``.                                           | ``None``              |
| ``ALG``          | Type of algorithm state variables. At the moment ``NV``                            | ``NV``                |
| ``coord``        | Type of coordinates to solve. For the moment ``polar``.                            | ``Polar``             |
| ``method``       | Solution method, can be ``nonlinear``, ``linear_PMU`` and ``nonlinear_PMU``.| ``nonlinear_PMU``|
| ``name_project`` | Project name                                                                       | ``Default``           |
| ``View_res``     | Displays the result of the selected algorithm by console                           | ``False``             |
| ``DSS_coll``     | Displays next to the estimated status, the actual status according to OpenDSS      | ``False``             |
| ``summary``      | Displays a summary of the simulation by console                                    | ``False``             |
| ``MEAS_Pos``     | ``True`` if it is a ``Pos`` circuit, take the ``.json`` files in positive sequence.| ``False``             |

<div id='id7' />

## Sample tests

In the path ``:{Python_library_path}/py_open_dsse/examples``, the ``.DSS`` and ``.json`` files of single-phase (``1ph``) and positive sequence equivalent (``Pos``) circuit measurements detailed in Table 11 are located.

**Table 11.** Sample tests
| **Circuit** | **Tpy_circ** | **Case** |
|:------------:|:------------:|:--------:|
|     4Node    |      1ph     |     1    |
|  15NodeIEEE  |      1ph     |     2    |
|  13NodeIEEE  |      Pos     |     1    |
|  37NodeIEEE  |      Pos     |     2    |

The function ``test_circuit(Typ_cir, case)``, returns a dictionary with the keys ``'DSS_file'``, ``'MEAS_path'``, ``'save_path'``, ``'name_project'`` and ``'Typ_cir'`` which correspond to the ``.DSS`` file path, measurement file path, path where results will be saved and circuit type respectively.
```Python
import py_open_dsse

dsse = py_open_dsse.init_DSSE() #Start the class.

if __name__ == '__main__':
    net = dsse.test_circuit(Typ_cir='1ph', case=1)
    
    #dsse.empty_init_files_MEAS_Unc(DSS_path=net['DSS_file'], MEAS_path=net['MEAS_path'])
    #dsse.add_error_files_MEAS(DSS_path=net['DSS_file'], MEAS_path=net['MEAS_path'])
    #dsse.empty_MEAS_files(DSS_path=net['DSS_file'], MEAS_path=net['MEAS_path'])

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
        #MEAS_Pos=True,
        #method='nonlinear'
        #method='linear_PMU',
    )
```

<div id='id8' />

### License

License: CC BY-NC-SA 4.0

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />

This work has a license <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
