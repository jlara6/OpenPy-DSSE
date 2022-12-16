# py_open_dsse

Es una librería de código abierto desarrollado en lenguaje Python para la estimación de redes de distribución (DSSE, por sus siglas en ingles).Se comunica con el software libre de simulacion de redes electricas (OpenDSS) y recolecta los resultados del flujo de potencia y los parámetros del sistema de distribución y ejecuta la DSSE, obteniendo un estado estimado según el tipo y ubicación de mediciones.

Es desarrollada en el marco del proyecto OpenREiD (Software integral de simulación y optimización de redes eléctricas de distribución), del Instituto de Energía Eléctrica (IEE), UNSJ - CONICET, San Juan - Argentina.

**Índice**

- [Instalación](#id1)
- [Como usar](#id2)
  - [Mediciones](#id3)
    - [Definicion y creación medidores](#id4)
    - [Generar mediciones a partir de resultados de OpenDSS](#id5)
  - [Ejecutar el algoritmo de estimación de estado](#id6)
  - [Ejemplos de prueba](#id7)
- [Licencia](#id8)

<div id='id1' />
## Instalación

Con pip

``pip install py_open_dsse``

Sin pip, es necesario clonar o descargar el repositorio. En la carpeta ``dist`` se encuentra el archivode extensión ``.whl``, copiando la ruta del archivo y en la consola de comados:

``pip install {path-save-files}/py_open_dsse-{version}-py3-none-any.whl’``

<div id='id2' />
## Como usar <a name="id1"></a>

Primero, en el IDE (Entorno de Desarrollo Integrado) de preferencia, importamos la librería:

```Python
import py_open_dsse
```

Llamamos a la clase objeto que contiene todas las funciones de la libreria, de la siguiente manera:

```Python
dsse = py_open_dsse.init_DSSE()
```

La clase ``init_DSSE()``, tiene valores por defecto como muestra la tabla 1 y se pueden modificar según sea el caso.

**Tabla 1.** Descripción y atributos de la función ``init_DSSE()``
| **Parámetro** | **Descripción** | **Valor por defecto** |
|:---:|-----|:---:|
| ``Sbas3ph_MVA`` | Potencia base trifásica del sistema | ``30`` |
| ``tolerance`` | Tolerancia de convergencia del algoritmo seleccionado | ``1e-3`` |
| ``max_iter``| Número máximo de iteraciones del algoritmo seleccionado | ``30`` |
| ``init_values`` | Valores iniciales para la estimación del estado. Con ``flat``' empezar con 1.0 p.u. / 0° en todos los buses y con ``dss`` inicia con los resultados de tensión y ángulo de OpenDSS. | ``Flat`` |

Una vez inicializada la clase, podemos usar las funciones que se describen a continuación.

<div id='id3' />

### Mediciones

<div id='id4' />

#### Definicion y creación medidores

La librería soporta medidores y su varianza de error respectiva descritas en la tabla 2.

**Tabla 2.** Tipo de mediciones de la libreria ``py_open_dsse``.

|              **Medición**              |                                **Descripción**                               |
|:--------------------------------------:|----------------------------------------------------------------------------  |
| $\left\|V_{i}\right\|$                 | Magnitud de tensión de nodo.                                                 |
| $PQ_{ft}$                              | Flujo de potencia entre nodos.                                               |
| $\left\|I_{ft}\right\|$                | Magnitud de corriente de rama.                                               |
| $PQ_{i}^{SM}$                          | Potencia de inyección o consumo de nodo obtenido por un medidor inteligente. |
| $PQ_{i}^{0}$                           | Potencia de nodo pasivo o de inyección cero.                                 |
| $PQ_{i}^{PSD}$                         | Potencia de inyección de nodo artificial conocida como pseudomedición.       |
| $\left\|V_{i}\right\|\angle \theta$    | Medición fasorial de voltaje.                                                |
| $\left\|I_{ft}\right\|\angle \delta$   | Medición fasorial de corriente.                                              |

La datos de las mediciones por fase **𝜌 (1, 2, 3)** y varianza del error de medición ``Rii`` de una red modelada en OpenDSS. Deben ser ingresada en los archivos ``MEAS_Bus_i.json``, ``MEAS_Elem_ft.json``, ``MEAS_Bus_i_PMU.json`` y ``MEAS_Elem_ft_PMU.json``. Los archivos ``.json`` de mediciones sin datos, son generados con la función ``empty_MEAS_files()`` y se debe ingresar los  parámetros de la tabla 3.

**Tabla 3.** Parámetros y descripción de la función ``empty_file_MEAS()``
|    **Parámetro**   |                           **Descripción**                             | **Valor por defecto**     |
|:------------------:|-----------------------------------------------------------------------|:-------------------------:|
| ``DSS_path``       | Ruta del archivo de OpenDSS.                                          | ``None``                  |
| ``MEAS_path_save`` | Ruta donde se guardará los archivos ``.json`` generados por la función| ``None``                  |

La descripción de los identificadores que pude ser modificados se detalla en las tablas 4, 5, 6 y 7. Los demás identificadores en de los archivos ``.json``, son características de nodo o elementos extraído de la circuito modelado en OpenDSS, estos datos no deben modificarse puesto que afectarían al resultado del algoritmo de estimación de estado.

**Tabla 4.** Descripción de identificadores del archivo ``MEAS_Bus_i.json``.

| **Identificador**     |                                       **Descripción**                                       |
|:---------------------:|---------------------------------------------------------------------------------------------|
| ``STS_Vm``            | Estado (1: Activado, 0: Desactivado)                                                        |
| ``Rii_Vm``            | Varianza de error de medición de magnitud de tensión.                                       |
| ``Vρm(pu)``           | Medición de magnitud de tensión voltaje en la fase 𝜌                                        |
| ``STS_PQd(SM)``       | Estado (1: Activado, 0: Desactivado)                                                        |
| ``Rii_SM``            | Varianza de error de medición de potencia de inyección o consumo de un medidor inteligente. |
| ``STS_PQd(0)``        | Estado (1: Activado, 0: Desactivado)                                                        |
| ``Rii_0``             | Varianza de error de medición de potencia de inyección cero o pasivo.                       |
| ``STS_PQd(Psd)``      | Estado (1: Activado, 0: Desactivado)                                                        |
| ``Rii_Psd``           | Varianza de error de medición de potencia de inyección de pseudo medición                   |
| ``Pρmd(pu)``          | Medición de inyección de potencia activa en la fase 𝜌                                       |
| ``Qρmd(pu)``          | Medición de inyección de potencia reactiva en la fase 𝜌                                     |

**Tabla 5.** Descripción de identificadores del archivo ``MEAS_Elem_ft.json``.

| **Identificador**     | **Descripción**                                             |
|-----------------------|-------------------------------------------------------------|
| ``STS_PQft``          | Estado (1: Activado, 0: Desactivado)                        |
| ``Rii_PQft``          | Varianza de error de medición de flujo de potencia de rama. |
| ``Pρmft(pu)``         | Medición de potencia activa de rama en la fase 𝜌            |
| ``Qρmft(pu)``         | Medición de potencia reactiva de rama en la fase 𝜌          |
| ``STS_Ift``           | Estado (1: Activado, 0: Desactivado)                        |
| ``Rii_Ift``           | Varianza de error de magnitud de corriente de rama.         |
| ``Iρmft(pu)``         | Medición de magnitud de corriente de rama en la fase 𝜌      |

**Tabla 6.** Descripción de identificadores del archivo ``MEAS_Bus_i_PMU.json``.
| **Identificador**     |                   **Descripción**                  |
|:---------------------:|--------------------------------------------------  |
| ``STS_Vm``            | Estado (1: Activado, 0: Desactivado)               |
| ``Rii_Vm``            | Varianza de error de medición fasorial de tensión. |
| ``Vρm(pu)``           | Medición de magnitud de tensión en la fase 𝜌       |
| ``Angρm(deg)``        | Medición de ángulo de tensión en la fase 𝜌         |

**Tabla 7.** Descripción de identificadores del archivo ``MEAS_Elem_ft_PMU.json``.
| **Identificador**      |                     **Descripción**                      |
|:-----------------:|----------------------------------------------------  |
| ``STS_Ift``       | Estado (1: Activado, 0: Desactivado)                 |
| ``Rii_Ift``       | Varianza de error de medición fasorial de corriente. |
| ``Iρmft(pu)``     | Medición de magnitud de corriente en la fase 𝜌       |
| ``Angρm(deg)``    | Medición de ángulo de corriente en la fase 𝜌         |

<div id='id5' />

#### Generar mediciones a partir de resultados de OpenDSS

##### Mediciones iniciales con incertidumbre de error de medición

La función ``empty_init_files_MEAS_Unc()``, genera archivos ``.json`` donde se coloca todos los nodos y elementos que pueden participar como medición en el algoritmo de estimación de estado. Para ello se debe indicar los parametro de la tabla 8.

**Tabla 8.** Atributos de la función ``empty_init_files_MEAS_Unc()``
|    **Parámetro**   |                           **Descripción**                               | **Valor por defecto** |
|:------------------:|-------------------------------------------------------------------------|:---------------------:|
| ``DSS_path``       | Ruta del archivo de OpenDSS.                                            | ``None``              |
| ``MEAS_path_save`` | Ruta donde se guardará los archivos ``.json`` generados por la función  | ``None``              |

En la ruta ``MEAS_path_save``, genera los archivos ``Init_Bus_i.json``, ``Init_Elem_ft.json``, ``Init_Bus_i_PMU.json`` y ``Init_Elem_ft_PMU.json``. Según el caso de estudio se puede ir modificando el estado del medidor ``STS`` (1: Activado, 0: Desactivado) y la incetudmbre del error de medición en ``Unc(%)``.

##### Agregar errores aleatorios y generar achivos de mediciones

Con los archivos ``.json`` generados por la función ``empty_files_MEAS()`` y los cambios indicados por el usuario, con la función ``add_error_files_MEAS()`` y los parámetros descritos en la tabla 9.

**Tabla 9.** Atributos de la función ``add_error_files_MEAS()``
| **Parámetro** |                        **Descripción**                        | **Valor por defecto** |
|:-------------:|---------------------------------------------------------------|:---------------------:|
| ``DSS_path``  | Ruta del archivo de OpenDSS.                                  | ``None``              |
| ``MEAS_path`` | Ruta de los archivos ``.json`` iniciales                      | ``None``              |
| ``seed_DS``   | Semilla de generación de errores aleatorios                   | ``1``                 |

Agrega errores aleatorios de una distribución normal a los resultados del flujo de potencia de OpenDSS, para usarlo como una medición. El resultado de generar errores aleaptos se encuentra en los archivos ``MEAS_Bus_i.json``, ``MEAS_Elem_ft.json``, ``MEAS_Bus_i_PMU.json`` y ``MEAS_Elem_ft_PMU.json``, guardados en ``MEAS_path``.

<div id='id6' />

### Ejecutar el algoritmo de estimación de estado

Para ejecutar el algoritmo de estimación de estado, se llama a funcion ``estimate()``, es necesario ingresar o cambiar parámetros detallados en la tabla 10

**Tabla 10.** Parámetros y descripción de la función ``estimate()``

|   **Parámetro**  |                                   **Descripción**                                      | **Valor por defecto** |
|:----------------:|--------------------------------------------------------------------------------------- |:---------------------:|
| ``DSS_path``     | Ruta del archivo de OpenDSS.                                                           | ``None``              |
| ``MEAS_path``    | Ruta donde se encuentran los archivos de mediciones.                                   | ``None``              |
| ``path_save``    | Ruta donde se guardará los resultados                                                  | ``None``              |
| ``Typ_cir``      | Tipo de circuito, puede ser ``1ph`` o ``Pos``                                          | ``None``              |
| ``ALG``          | Tipo de variables de estado del algoritmo. Por el momento ``NV``                       | ``NV``                |
| ``coord``        | Tipo de coordenadas para resolver. Por el momento ``polar``                            | ``Polar``             |
| ``method``       | Metodo de solución, puede ser ``nonlinear``, ``linear_PMU`` y ``nonlinear_PMU``        | ``nonlinear_PMU``     |
| ``name_project`` | Nombre del proyecto                                                                    | ``Default``           |
| ``View_res``     | Muestra por consola el resultado del algoritmo seleccionado                            | ``False``             |
| ``DSS_coll``     | Muestra junto al estado estimado, el estado real de acuerdo a OpenDSS                  | ``False``             |
| ``summary``      | Muestra por consola un resumen de la simulación                                        | ``False``             |
| ``MEAS_Pos``     | ``True`` si es un circuito``Pos``,Toma los archivos ``.json`` de secuencia positiva| ``False``             |

<div id='id7' />

## Ejemplos de prueba

En la ruta ``:{Python_library_path}/py_open_dsse/examples``, se encuentran los archivos ``.DSS`` y ``.json`` de mediciones de circuitos monofásico (``1ph``) y equivalente de secuencia positiva (``Pos``) detallados en la tabla 11.

**Tabla 11.** Ejemplos de prueba
| **Circuito** | **Tpy_circ** | **Case** |
|:------------:|:------------:|:--------:|
|     4Node    |      1ph     |     1    |
|  15NodeIEEE  |      1ph     |     2    |
|  13NodeIEEE  |      Pos     |     1    |
|  37NodeIEEE  |      Pos     |     2    |

La función ``test_circuit(Typ_cir, case)``, devuelve un diccionario con las llaves ``'DSS_file'``, ``'MEAS_path'``, ``'save_path'``, ``'name_project'`` y ``'Typ_cir'`` que correspoden a la ruta de archivos ``.DSS``, ruta de archivos de mediciones ``.json``, ruta donde se guardara resultados y tipo de circuito respectivamente.

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

### Licencia

Licencia: CC BY-NC-SA 4.0

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />

Este trabajo se encuentra bajo la licencia <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
