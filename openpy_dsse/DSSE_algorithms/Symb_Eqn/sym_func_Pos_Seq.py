# -*- coding: utf-8 -*-
# @Time    : 03/03/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

from sympy import Matrix,  symbols,  diff
from sympy import sin,  cos,  atan,  lambdify,  atan2,  I
import math
import numpy as np
from numpy import real as re
from numpy import imag as im

'Se definen las variables simbolicas para posteriormente utilizarlas en las ecuaciones de cálculo'
'de flujo de P y Q por las lineas'
V_i = symbols('V_i', real=True)
theta_i = symbols('theta_i', real=True)
V_j = symbols('V_j', real=True)
theta_j = symbols('theta_j', real=True)
G = symbols('G', real=True)
B = symbols('B', real=True)

'Real an reactive power inyection'
def Pi():
    """
    Symbolic equation of Pi, in matrix format
    :return: P_i
    """
    #P_i = V_i * ((V_j * (G * cos(theta_i - theta_j) + B * sin(theta_i - theta_j)))) - V_i * ((V_i * (G * cos(theta_i - theta_i) + B * sin(theta_i - theta_i))))
    #P_i = 3 * P_i
    P_i = V_i * V_j * (G * cos(theta_i - theta_j) + B * sin(theta_i - theta_j))
    P_i = 3 * P_i

    return P_i

def Qi():
    """
    Symbolic equation of Qi, in matrix format

    :return: Q_i
    """
    #Q_i = V_i * ((V_j * (G * sin(theta_i - theta_j) - B * cos(theta_i - theta_j)))) - V_i * ((V_i * (G * sin(theta_i - theta_i) - B * cos(theta_i - theta_i))))
    Q_i = V_i * V_j * (G * sin(theta_i - theta_j) - B * cos(theta_i - theta_j))
    Q_i = 3 * Q_i

    return Q_i

'Real an reactive power flows'
def Pij():
    """
    Symbolic equation of Pij, in matrix format

    :return: P_ij
    """
    P_ij = V_i * ((V_j * (G * cos(theta_i - theta_j) + B * sin(theta_i - theta_j)))) - \
           V_i * ((V_i * (G * cos(theta_i - theta_i) + B * sin(theta_i - theta_i))))

    P_ij = 3 * P_ij

    return P_ij

def Qij():
    """
    Symbolic equation of Qij, in matrix format

    :return: Q_ij
    """
    '''
    Vi = np.array(V_i * (cos(theta_i) + I * sin(theta_i)))
    Vj = np.array(V_j * (cos(theta_j) + I * sin(theta_j)))
    Vt = np.array(Vi - Vj)
    Y = np.array(G + I * B)
    I_ij = np.dot(Y, Vt)
    Q_ij = 3 * Vi * np.conj(I_ij)
    '''
    Q_ij = V_i * ((V_j * (G * sin(theta_i - theta_j) - B * cos(theta_i - theta_j)))) - \
           V_i * ((V_i * (G * sin(theta_i - theta_i) - B * cos(theta_i - theta_i))))
    Q_ij = 3 * Q_ij

    return Q_ij

'Circuit current, module and angle'
def Iij():
    """
    Symbolic equation of |Iij|, in matrix format

    :return: Iij
    """
    P_ij = V_i * ((V_j * (G * cos(theta_i - theta_j) + B * sin(theta_i - theta_j)))) - \
           V_i * ((V_i * (G * cos(theta_i - theta_i) + B * sin(theta_i - theta_i))))
    #P_ij = 3 * P_ij
    Q_ij = V_i * ((V_j * (G * sin(theta_i - theta_j) - B * cos(theta_i - theta_j)))) - \
           V_i * ((V_i * (G * sin(theta_i - theta_i) - B * cos(theta_i - theta_i))))

    #Q_ij = 3 * Q_ij

    I_ij = pow(((P_ij) ** 2 + (Q_ij) ** 2),  0.5) / V_i

    return I_ij

def angIij():
    """
    Symbolic equation of Iang_δij, in matrix format

    :return: angI_ij
    """

    P_ij = V_i * ((V_j * (G * cos(theta_i - theta_j) + B * sin(theta_i - theta_j)))) - \
           V_i * ((V_i * (G * cos(theta_i - theta_i) + B * sin(theta_i - theta_i))))

    Q_ij = V_i * ((V_j * (G * sin(theta_i - theta_j) - B * cos(theta_i - theta_j)))) - \
           V_i * ((V_i * (G * sin(theta_i - theta_i) - B * cos(theta_i - theta_i))))

    '''
    angI_ij = theta_i - atan(Q_ij/P_ij)
    '''
    angI_ij = theta_i -atan2(Q_ij,  P_ij)

    return angI_ij

def Iijrec():
    """
    Symbolic equation of Iij_rectangular, in matrix format

    :return: I_ij
    """
    Vi = np.array(V_i * (cos(theta_i) + I * sin(theta_i)))
    Vj = np.array(V_j * (cos(theta_j) + I * sin(theta_j)))

    Vt = np.array(Vi - Vj)

    Y = np.array(G + I * B)

    #I_ij = np.dot(Y, Vt)
    I_ij = np.dot(Y, Vt)

    return I_ij


'----------------------------------------------------------------------------------------------------------------------'
'''
Symbolic equations that form the Jacobian matrix

___________|_____θ_____|_____V_____|
____|Vi|___|____H11____|____H12____|
_____Pi____|____H21____|____H22____|
_____Qi____|____H31____|____H32____|
____Pij____|____H41____|____H42____|
____Qij____|____H51____|____H52____|
___|Iij|___|____H61____|____H62____|
____|Vi|___|____H71____|____H72____|
_____θi____|____H81____|____H82____|
___|Iij|___|____H91____|____H92____|
____δij____|____H01____|____H02____|
'''
'----------------------------------------------------------------------------------------------------------------------'


def H21i_a():
    """
    Symbolic equation of ∂Pi/∂θi part (a), in matrix format
    Eq. available in ''Formulation of Three-Phase State Estimation Problem Using a Virtual Reference'

    :return: H21i_a
    """
    '''
    H21i= Matrix([[diff(P_i()[0], theta_i1), diff(P_i()[0], theta_i2), diff(P_i()[0], theta_i3)],
                  [diff(P_i()[1], theta_i1), diff(P_i()[1], theta_i2), diff(P_i()[1], theta_i3)], 
                  [diff(P_i()[2], theta_i1), diff(P_i()[2], theta_i2), diff(P_i()[2], theta_i3)]])
    '''
    # Eq. (16)
    H21i_a = diff(Pi(), theta_i)

    return H21i_a


def H21i_b():
    """
    Symbolic equation of ∂Pi/∂θi part (b), in matrix format
    Eq. available in ''Formulation of Three-Phase State Estimation Problem Using a Virtual Reference'

    :return: H21i_b
    """
    H21i_b = -Qi()

    return H21i_b

def H21j():
    """
    Symbolic equation of ∂Pi/∂θj, in matrix format

    :return: H21j
    """
    #Eq. (17)
    H21j= diff(Pi(), theta_j)
    return H21j

def H22i_a():
    """
    Symbolic equation of ∂Pi/∂Vi part (a), in matrix format

    :return: H22i_a
    """

    H22i_a= diff(Pi(), V_i)

    return H22i_a


def H22i_b():
    """
    Symbolic equation of ∂Pi/∂Vi part (b), in matrix format

    :return: H22i_b
    """

    H22i_b = Pi()

    return H22i_b

def H22j():
    """
    Symbolic equation of ∂Pi/∂Vj, in matrix format

    :return: H22j
    """
    H22j= diff(Pi(), V_j)

    return H22j

'H31i(∂Qi/∂θi), H31j(∂Qi/∂θj), H32i(∂Qi/∂Vi) and H32j(∂Qi/∂Vj) are the derivatives of reactive injection power at node "i" and "j" respectively'
def H31i_a():
    """
    Symbolic equation of ∂Qi/∂θi part (a), in matrix format
    Eq. available in ''Formulation of Three-Phase State Estimation Problem Using a Virtual Reference

    :return: H31i_a
    """

    #Eq. (19)
    H31i_a= diff(Qi(), theta_i)

    return H31i_a

def H31i_b():
    """
    Symbolic equation of ∂Qi/∂θi part (b), in matrix format

    :return: H31i_b
    """
    H31i_b = Pi()

    return H31i_b

def H31j():
    """
    Symbolic equation of ∂Qi/∂θj, in matrix format

    :return: H31j
    """
    #Eq. (20)
    H31j= diff(Qi(), theta_j)
    return H31j

def H32i_a():
    """
    Symbolic equation of ∂Qi/∂Vi part (a), in matrix format

    :return: H32i_a
    """

    H32i_a = diff(Qi(), V_i)

    return H32i_a

def H32i_b():
    """
    Symbolic equation of ∂Qi/∂Vi part (b), in matrix format

    :return: H32i_b
    """

    H32i_b= Qi()

    return H32i_b

def H32j():
    """
    Symbolic equation of ∂Qi/∂Vj, in matrix format

    :return: H32j
    """
    H32j = diff(Qi(), V_j)

    return H32j

'----------------------------------------------------------------------------------------------------------------------'
'H41i(∂Pij/∂θi), H41j(∂Pij/∂θj), H42i(∂Pij/∂Vi) and H42j(∂Pij/∂Vj) are the derivatives of the active power of flow at node "i" and "j" respectively'
def H41i():
    """
    Symbolic equation of ∂Pij/∂θi, in matrix format

    :return: H41i
    """
    H41i = diff(Pij(), theta_i)

    return H41i

def H41j():
    """
    Symbolic equation of ∂Pij/∂θj, in matrix format

    :return: H41j
    """

    H41j = diff(Pij(), theta_j)

    return H41j

def H42i():
    """
    Symbolic equation of ∂Pij/∂Vi, in matrix format

    :return: H42i
    """

    H42i= diff(Pij(), V_i)

    return H42i

def H42j():
    """
    Symbolic equation of ∂Pij/∂Vj, in matrix format

    :return: H42j
    """
    H42j= diff(Pij(), V_j)

    return H42j

'----------------------------------------------------------------------------------------------------------------------'
'H51i(∂Qij/∂θi), H51j(∂Qij/∂θj), H52i(∂Qij/∂Vi) and H52j(∂Qij/∂Vj)'
'Are the derivatives of the reactive power of flow at node "i" and "j" respectively'
def H51i():
    """
    Symbolic equation of ∂Qij/∂θi, in matrix format

    :return: H51i
    """
    H51i = diff(Qij(), theta_i)

    return H51i

def H51j():
    """
    Symbolic equation of ∂Qij/∂θj, in matrix format

    :return: H51j
    """
    H51j = diff(Qij(), theta_j)

    return H51j

def H52i():
    """
    Symbolic equation of ∂Qij/∂Vi, in matrix format

    :return: H52i
    """

    H52i = diff(Qij(), V_i)
    return H52i

def H52j():
    """
    Symbolic equation of ∂Qij/∂Vj, in matrix format

    :return: H52j
    """

    H52j = diff(Qij(), V_j)

    return H52j

'----------------------------------------------------------------------------------------------------------------------'
'H61i(∂|Iij|/∂θi), H61j(∂|Iij|/∂θj), H62i(∂|Iij|/∂Vi) and H62j(∂|Iij|/∂Vj)'
'Are the derivatives of the current module between node "i" and "j" respectively'
def H61i():
    """
    Symbolic equation of ∂|Iij|/∂θi, in matrix format

    :return: H61i
    """
    H61i = diff(Iij(), theta_i)

    return H61i

def H61j():
    """
    Symbolic equation of ∂|Iij|/∂θj, in matrix format

    :return: H61j
    """
    H61j= diff(Iij(), theta_j)

    return H61j

def H62i():
    """
    Symbolic equation of ∂|Iij|/∂Vi, in matrix format

    :return: H62i
    """

    H62i= diff(Iij(), V_i)

    return H62i

def H62j():
    """
    Symbolic equation of ∂|Iij|/∂Vj, in matrix format

    :return: H62j
    """

    H62j= diff(Iij(), V_j)

    return H62j


def H61i_rec():
    """
    Symbolic equation of ∂Iijrec/∂θi, in matrix format

    :return: H62j
    """

    H61i= diff(Iijrec(), theta_i)

    return H61i

def H61j_rec():
    """
    Symbolic equation of ∂Iijrec/∂θj, in matrix format

    :return: H62j
    """

    H61j= diff(Iijrec(), theta_j)

    return H61j

def H62i_rec():
    """
    Symbolic equation of ∂Iijrec/∂θi, in matrix format

    :return: H62j
    """

    H62i= diff(Iijrec(), V_i)

    return H62i

def H62j_rec():
    """
    Symbolic equation of ∂Iijrec/∂θj, in matrix format

    :return: H62j
    """

    H62j= diff(Iijrec(), V_j)

    return H62j

'----------------------------------------------------------------------------------------------------------------------'
'H01i(∂δij/∂θi), H01j(∂δij/∂θj) , H02i(∂δij/∂Vi) and H02j(∂δij/∂Vj)'
'Are the derivatives of the current angle between node "i" and "j" respectively'
def H01i():
    """
    Symbolic equation of ∂δij/∂θi, in matrix format

    :return: H01i
    """
    H01i= diff(angIij(), theta_i)

    return H01i

def H01j():
    """
    Symbolic equation of ∂δij/∂θj, in matrix format

    :return: H01j
    """
    H01j= diff(angIij(), theta_j)

    return H01j

def H02i():
    """
    Symbolic equation of ∂δij/∂Vi, in matrix format

    :return: H02i
    """
    H02i = diff(angIij(), V_i)

    return H02i

def H02j():
    """
    Symbolic equation of ∂δij/∂Vj, in matrix format

    :return: H02j
    """
    H02j = diff(angIij(), V_j)
    return H02j
def sym_func_Pi_Qi():
    """
    Symbolic equations of active and reactive power at node i
    P_i = lambdify(Y_Vij, P_i(), 'numpy')
    Q_i = lambdify(Y_Vij, Q_i(), 'numpy')

    :return:P_i, Q_i
    """
    Y_Vij = [G, B,
             V_i, theta_i,
             V_j, theta_j]
    # (Pi)
    P_i = lambdify(Y_Vij, Pi(), 'numpy')
    # (Qi)
    Q_i = lambdify(Y_Vij, Qi(), 'numpy')

    return P_i, Q_i

def sym_func_Pij_Qij():
    """
    Symbolic equations of active and reactive power between node i and j
    P_ij = lambdify(Y_Vij, P_ij(), 'numpy')
    Q_ij = lambdify(Y_Vij, Q_ij(), 'numpy')

    :return: P_ij, Q_ij
    """
    Y_Vij = [G,B,
             V_i,theta_i,
             V_j,theta_j]
    # (Pij)
    P_ij = lambdify(Y_Vij, Pij(), 'numpy')
    # (Qij)
    Q_ij = lambdify(Y_Vij, Qij(), 'numpy')

    return P_ij, Q_ij

def sym_func_Iij():
    """
    Symbolic equations of current module and angle between node i and j
    I_ij = lambdify(Y_Vij,  Iij(),  'numpy')
    angI_ij = lambdify(Y_Vij,  angIij(),  'numpy')

    :return:I_ij, angI_ij
    """
    Y_Vij = [G,  B,
             V_i,  theta_i,
             V_j,  theta_j]
    # (Iij)
    I_ij = lambdify(Y_Vij, Iij(), 'numpy')
    # (δij-PMU)
    angI_ij = lambdify(Y_Vij, angIij(), 'numpy')

    return I_ij, angI_ij

def sym_func_Iij_rec():
    """
    Symbolic equations in rectangular form of current between node i and j
    Iij_rec = lambdify(Y_Vij, Iijrec(), 'numpy')

    :return: Iij_rec
    """
    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]
    Iij_rec = lambdify(Y_Vij, Iijrec(), 'numpy')

    return Iij_rec


def sym_func_H21_H22():
    """
    Symbolic equation of H21(∂Pi/∂θ) and H22(∂Pi/∂V)

    :return: H21i_eq_a, H21i_eq_b, H21j_eq, H22i_eq_a, H22i_eq_b, H22j_eq
    """
    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    H21i_eq_a = lambdify(Y_Vij, H21i_a(), 'numpy')
    H21i_eq_b = lambdify(Y_Vij, H21i_b(), 'numpy')
    H21j_eq = lambdify(Y_Vij, H21j(), 'numpy')
    H22i_eq_a = lambdify(Y_Vij, H22i_a(), 'numpy')
    H22i_eq_b = lambdify(Y_Vij, H22i_b(), 'numpy')
    H22j_eq = lambdify(Y_Vij, H22j(), 'numpy')

    return H21i_eq_a, H21i_eq_b, H21j_eq, H22i_eq_a, H22i_eq_b, H22j_eq


def sym_func_H31_H32():
    """
    Symbolic equation of H31(∂Qi/∂θ) and H32(∂Qi/∂V)

    :return: H31i_eq_a, H31i_eq_b, H31j_eq, H32i_eq_a, H32i_eq_b, H32j_eq
    """
    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    # Ec. de derivada de Q_i con respecto al tetha i cuando i=i y phase = phase
    H31i_eq_a = lambdify(Y_Vij, H31i_a(), 'numpy')
    H31i_eq_b = lambdify(Y_Vij, H31i_b(), 'numpy')

    # Ec. de derivada de Q_i con respecto al tetha j cuando i!=i
    # Ec(20)
    H31j_eq = lambdify(Y_Vij, H31j(), 'numpy')
    H32i_eq_a = lambdify(Y_Vij, H32i_a(), 'numpy')
    H32i_eq_b = lambdify(Y_Vij, H32i_b(), 'numpy')
    H32j_eq = lambdify(Y_Vij, H32j(), 'numpy')

    return H31i_eq_a, H31i_eq_b, H31j_eq, H32i_eq_a, H32i_eq_b, H32j_eq


def sym_func_H41_H42():
    """
    Symbolic equation of H41(∂Pij/∂θ) and H42(Pij/∂V)

    :return: H41i_eq, H41j_eq, H42i_eq, H42j_eq
    """
    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    H41i_eq = lambdify(Y_Vij, H41i(), 'numpy')
    H41j_eq = lambdify(Y_Vij, H41j(), 'numpy')
    H42i_eq = lambdify(Y_Vij, H42i(), 'numpy')
    H42j_eq = lambdify(Y_Vij, H42j(), 'numpy')

    return H41i_eq, H41j_eq, H42i_eq, H42j_eq


def sym_func_H51_H52():
    """
    Symbolic equation of H51(∂Qij/∂θ) and H52(Qij/∂V)

    :return: H51i_eq, H51j_eq, H52i_eq, H52j_eq
    """
    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    H51i_eq = lambdify(Y_Vij, H51i(), 'numpy')
    H51j_eq = lambdify(Y_Vij, H51j(), 'numpy')
    H52i_eq = lambdify(Y_Vij, H52i(), 'numpy')
    H52j_eq = lambdify(Y_Vij, H52j(), 'numpy')

    return H51i_eq, H51j_eq, H52i_eq, H52j_eq


def sym_func_H61_H62():
    """
    Symbolic equation of H61(∂|Iij|/∂θ) and H62(|Iij|/∂V)

    :return: H61i_eq, H61j_eq, H62i_eq, H62j_eq
    """
    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    H61i_eq = lambdify(Y_Vij, H61i(), 'numpy')
    H61j_eq = lambdify(Y_Vij, H61j(), 'numpy')
    H62i_eq = lambdify(Y_Vij, H62i(), 'numpy')
    H62j_eq = lambdify(Y_Vij, H62j(), 'numpy')

    return H61i_eq, H61j_eq, H62i_eq, H62j_eq


def sym_func_H61_H62_rec():
    """
    Symbolic equation of H61(∂Iij_rec/∂θ) and H62(Iij_rec/∂V)

    :return: H61i_rec_eq, H61j_rec_eq, H62i_rec_eq, H62j_rec_eq
    """

    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    H61i_rec_eq = lambdify(Y_Vij, H61i_rec(), 'numpy')
    H61j_rec_eq = lambdify(Y_Vij, H61j_rec(), 'numpy')
    H62i_rec_eq = lambdify(Y_Vij, H62i_rec(), 'numpy')
    H62j_rec_eq = lambdify(Y_Vij, H62j_rec(), 'numpy')

    return H61i_rec_eq, H61j_rec_eq, H62i_rec_eq, H62j_rec_eq


def sym_func_H01_H02():
    """
    Symbolic equation of H01(∂δij/∂θ) and H02(∂δij/∂V)

    :return: H01i_eq, H01j_eq, H02i_eq,  H02j_eq
    """

    Y_Vij = [G, B, V_i, theta_i, V_j, theta_j]

    H01i_eq = lambdify(Y_Vij, H01i(), 'numpy')
    H01j_eq = lambdify(Y_Vij, H01j(), 'numpy')
    H02i_eq = lambdify(Y_Vij, H02i(), 'numpy')
    H02j_eq = lambdify(Y_Vij, H02j(), 'numpy')

    return H01i_eq, H01j_eq, H02i_eq, H02j_eq


def func_lambdify():
    datos = [G, B, V_i, theta_i, V_j, theta_j]

    f1 = lambdify(datos, P_i(), 'numpy')
    f2 = lambdify(datos, Q_i(), 'numpy')

    f3 = lambdify(datos, P_ij(), 'numpy')
    f4 = lambdify(datos, Q_ij(), 'numpy')

    f5 = lambdify(datos, Iij(), 'numpy')
    f5_ang = lambdify(datos, angIij(), 'numpy')

    'H21(∂Pi /∂θ) and H22(∂Pi /∂V)'
    f5_a = lambdify(datos, H21i_a(), 'numpy')
    f5_b = lambdify(datos, H21i_b(), 'numpy')
    f6 = lambdify(datos, H21j(), 'numpy')
    f7_a = lambdify(datos, H22i_a(), 'numpy')
    f7_b = lambdify(datos, H22i_b(), 'numpy')
    f8 = lambdify(datos, H22j(), 'numpy')

    f9_a = lambdify(datos, H31i_a(), 'numpy')
    f9_b = lambdify(datos, H31i_b(), 'numpy')
    f10 = lambdify(datos, H31j(), 'numpy')
    f11_a = lambdify(datos, H32i_a(), 'numpy')
    f11_b = lambdify(datos, H32i_b(), 'numpy')
    f12 = lambdify(datos, H32j(), 'numpy')

    f13 = lambdify(datos, H41i(), 'numpy')
    f14 = lambdify(datos, H41j(), 'numpy')
    f15 = lambdify(datos, H42i(), 'numpy')
    f16 = lambdify(datos, H42j(), 'numpy')

    f17 = lambdify(datos, H51i(), 'numpy')
    f18 = lambdify(datos, H51j(), 'numpy')
    f19 = lambdify(datos, H52i(), 'numpy')
    f20 = lambdify(datos, H52j(), 'numpy')

    f21 = lambdify(datos, H61i(), 'numpy')
    f22 = lambdify(datos, H61j(), 'numpy')
    f23 = lambdify(datos, H62i(), 'numpy')
    f24 = lambdify(datos, H62j(), 'numpy')

    f25 = lambdify(datos, H01i(), 'numpy')
    f26 = lambdify(datos, H01j(), 'numpy')
    f27 = lambdify(datos, H02i(), 'numpy')
    f28 = lambdify(datos, H02j(), 'numpy')

    return f1, f2, f3, f4, f5, f5_ang, f5_a, f5_b, f6, f7_a, f7_b, f8, f9_a, f9_b, f10, f11_a, f11_b, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21, f22, f23, f24, f25, f26, f27, f28
