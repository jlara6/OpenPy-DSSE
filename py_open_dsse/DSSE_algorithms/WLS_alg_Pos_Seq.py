# -*- coding: utf-8 -*-
# @Time    : 03/03/2022
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import logging
import cmath
from py_open_dsse.YBus_Matrix_Pos_Seq import *
from .Symb_Eqn.sym_func_Pos_Seq import *
from ..base_DSSE import functions_DSSE
from ..error_handling_logging import update_logg_file

fx_aux = functions_DSSE()
log_py = logging.getLogger(__name__)

data_DSS = OpenDSS_data_collection()


def vector_Ri_seq(num_Rii, Ri_m) -> np.array:
    """
    Function that creates the measurement error vector according to the number

    :param num_Rii: Number of existing measurements
    :param Ri_m: vector containing the error associated with each type of meter
    :return: Rii
    """
    Rii = np.zeros([num_Rii, 1])
    aux_Rii = 0
    for k in range(0, len(Ri_m)):
        if Ri_m[k] < 10 ** (-4):
            Ri_m[k] = 10 ** (-4)
        Rii[aux_Rii, 0] = Ri_m[k]
        aux_Rii += 1
    return Rii

def vector_Ri_pmu_seq(nvi_pmu, nii_pmu, Ri_mang_pmu, Ri_ang_pmu) -> np.array:
    """
    Function that creates the measurement error vector according to the number of PMUs

    :param nvi_pmu: Measurement number type vi (PMU)
    :param nii_pmu: Measurement number type ii (PMU)
    :param Ri_mang_pmu: vector containing the error associated with each type of meter
    :param Ri_ang_pmu: vector containing the error associated with each type of meter

    :return: Rii_pmu
    """
    Rii_pmu = np.zeros([(nvi_pmu * 2 + nii_pmu * 2), 1])
    aux_Rii_pmu = 0
    aux_pos = nvi_pmu
    
    for i in range(0, nvi_pmu):
        Rii_pmu[aux_Rii_pmu, 0] = Ri_mang_pmu[i]
        aux_Rii_pmu += 1
        
    for m in range(0, nvi_pmu):
        Rii_pmu[aux_Rii_pmu, 0] = Ri_ang_pmu[m]
        aux_Rii_pmu += 1

    for k in range(0, nii_pmu):
        Rii_pmu[aux_Rii_pmu, 0] = Ri_mang_pmu[k + aux_pos]
        aux_Rii_pmu += 1

    for n in range(0, nii_pmu):
        Rii_pmu[aux_Rii_pmu, 0] = Ri_ang_pmu[n + aux_pos]
        aux_Rii_pmu += 1

    return Rii_pmu

class WLS_Pos_state_estimator:

    def __init__(self, tolerance: int, num_iter_max: int, DF_MEAS_SCADA: pd.DataFrame, DF_MEAS_PMU: pd.DataFrame,
                 DF_Volt_Ang_initial: pd.DataFrame, YBus_Matrix: np.array):
        '''

        :param tolerance:
        :param num_iter_max:
        :param DF_MEAS_SCADA:
        :param DF_Volt_Ang_initial: initial values of the state estimator
        :param YBus_Matrix: Corresponds to the Y_Bus Matrix of the system.
        '''
        self.tolerance = tolerance
        self.num_iter_max = num_iter_max
        self.DF_MEAS_SCADA = DF_MEAS_SCADA
        self.DF_MEAS_PMU = DF_MEAS_PMU
        self.DF_Volt_Ang_initial = DF_Volt_Ang_initial
        self.YBus_Matrix = YBus_Matrix

    def WLS_linear_nonlinear_PMU(self):
        # Bus Data
        nbus = len(self.DF_Volt_Ang_initial)

        # Type of measurement:
        # |Vi|-1, Pi(SM, Psd)-2, Qi(SM, Psd)-3, Pi_0-4, Qi_0-5, Pft-6, Qft-7, |Ift|-8 (SCADA measurements)
        measurement_data = np.array(self.DF_MEAS_SCADA)
        m_type = np.array([measurement_data[:, 0]]).T
        z_value = np.array([measurement_data[:, 1]]).T
        fbus_m = np.array([measurement_data[:, 4]]).T
        tbus_m = np.array([measurement_data[:, 5]]).T
        Ri_m = np.array([measurement_data[:, 6]]).T

        # Identification of more measurements and location by the m_type of
        'SCADA measurements'
        'Vi (Bus voltage), pi and qi (Injection powers), pf and qf (Power Flow), finally ii (Line current magnitude)'
        vi = np.argwhere(m_type == 1)
        pi = np.argwhere(m_type == 2)
        qi = np.argwhere(m_type == 3)
        pf = np.argwhere(m_type == 4)
        qf = np.argwhere(m_type == 5)
        ii = np.argwhere(m_type == 6)

        nvi = len(vi)
        npi = len(pi)
        nqi = len(qi)
        npf = len(pf)
        nqf = len(qf)
        nii = len(ii)

        'Total number of measurements'
        nro_measurements = nvi + npi + nqi + npf + nqf + nii
        num_MEAS = {'|Vi|': nvi, 'Pi': npi, 'Qi': nqi, 'Pij': npf, 'Qij': nqf, '|Iij|': nii}
        # Measurement redundancy check
        fx_aux.check_observability(nbus, nro_measurements, log_py)

        'Creation and ordering of the vector of SCADA measurements'
        'SCADA measurements'
        matrix_calc = Zm_hcalc_Jacobian_Pos(vi, pi, qi, pf, qf, ii, nvi, npi, nqi, npf, nqf, nii)
        Z_MEAS = matrix_calc.Z_SCADA(z_value)

        'Form the inverse Rii matrix according to the number of available measurements'
        'SCADA measurements'
        Rii_total = np.diagflat(vector_Ri_seq(len(vi) + len(pi) + len(qi) + len(pf) + len(qf) + len(ii), Ri_m))

        'Initial voltage and angle values'
        Matrix_Mang_Ang_initial = np.array(self.DF_Volt_Ang_initial)
        bus_name = np.array([Matrix_Mang_Ang_initial[:, 1]]).T
        num_nodes = len(np.array([Matrix_Mang_Ang_initial[:, 2]]).T)
        V1_Magn = np.array([Matrix_Mang_Ang_initial[:, 3]]).T
        Ang1_rdn = np.array([Matrix_Mang_Ang_initial[:, 4]]).T
        E = np.concatenate((Ang1_rdn[1:, :1], V1_Magn), 0)

        n_Iter = 0
        tol = 5
        n_Iter_ee = self.num_iter_max

        # while Iter < 1:
        while tol > self.tolerance:

            h_calculate = matrix_calc.h_calculate(fbus_m, tbus_m, V1_Magn, Ang1_rdn, nbus, self.YBus_Matrix)
            'residual vector between the vector z(m) existing measurements and h(x) calculated measurements'
            residual = Z_MEAS - h_calculate
            # Jacobian..
            # SCADA measurements
            H = matrix_calc.Jacobian(fbus_m, tbus_m, V1_Magn, Ang1_rdn, nbus, self.YBus_Matrix)
            # Gain Matrix, Gm..
            Gm = H.T @ np.linalg.inv(Rii_total) @ H
            # P, L, U = observability_LU_Decomposition(Gm)
            G_inv = fx_aux.calculate_Ginv(Gm, log_py)

            delta_E = G_inv @ (H.T @ np.linalg.inv(Rii_total) @ residual)
            E = E + delta_E

            Ang1_rdn[1:, :] = E[0:nbus - 1]
            theta_degre = Ang1_rdn * 180 / math.pi
            V1_Magn = E[nbus - 1::]
            n_Iter = n_Iter + 1

            if n_Iter < n_Iter_ee:
                tol = max(np.absolute(delta_E))[0]

            if n_Iter_ee <= n_Iter:
                fx_aux.check_num_max_iter(self.num_iter_max, n_Iter, tol, log_py)

        if self.DF_MEAS_PMU.empty == True:

            Ang1_deg = Ang1_rdn * 180 / math.pi
            V1_Magn = np.array(V1_Magn).astype(None)
            Ang1_deg = np.array(Ang1_deg).astype(None)
            DSSE_results = np.concatenate((bus_name, np.round(V1_Magn, 4), np.round(Ang1_deg, 4)), 1)
            DF_DSSE_results = pd.DataFrame(DSSE_results, columns=['Bus Nro.', 'V1(pu)_EST', 'Ang1(deg)_EST'])

            return DF_DSSE_results, n_Iter, tol, num_MEAS

    def WLS_nonlinear_PMU(self):
        """
        Weighted Least Squares Algorithm Sequence that considers measurements of |Vi|, Pi, Qi, Pij, Qij, |Iij|

        """
        # Bus Data
        nbus = len(self.DF_Volt_Ang_initial)
        'SCADA measurements'
        # Type of measurement, Vi-1, Pi-2, Qi-3, Pij-4, Qij-5, Iij-6 (SCADA measurements)
        measurement_data = np.array(self.DF_MEAS_SCADA)
        m_type = np.array([measurement_data[:, 0]]).T
        z_value = np.array([measurement_data[:, 1]]).T
        fbus_m = np.array([measurement_data[:, 4]]).T
        tbus_m = np.array([measurement_data[:, 5]]).T
        Ri_m = np.array([measurement_data[:, 6]]).T

        'Identification of more measurements and location by the m_type of:'
        'Vi (Bus voltage), pi and qi (Injection powers), pf and qf (Flow powers), finally ii (Line current magnitude)'
        vi = np.argwhere(m_type == 1)
        pi = np.argwhere(m_type == 2)
        qi = np.argwhere(m_type == 3)
        pf = np.argwhere(m_type == 4)
        qf = np.argwhere(m_type == 5)
        ii = np.argwhere(m_type == 6)

        nvi = len(vi)
        npi = len(pi)
        nqi = len(qi)
        npf = len(pf)
        nqf = len(qf)
        nii = len(ii)

        # Type of measurement, Vi_ph-7, Iij_ph-8 (Phasor measurements (PMU))
        # Transform measurements from degrees to radians: Vi_ph-7, Iij_ph-8
        for m in range(len(self.DF_MEAS_PMU)):
            if self.DF_MEAS_PMU.at[m, 'Type'] == 7:
                self.DF_MEAS_PMU.at[m, 'Angle1(deg)'] = math.radians(self.DF_MEAS_PMU.at[m, 'Angle1(deg)'])

            elif self.DF_MEAS_PMU.at[m, 'Type'] == 8:
                self.DF_MEAS_PMU.at[m, 'Angle1(deg)'] = math.radians(self.DF_MEAS_PMU.at[m, 'Angle1(deg)'])

        m_pmu = np.array(self.DF_MEAS_PMU)
        m_type_pmu = np.array([m_pmu[:, 0]]).T
        z_magn_value = np.array([m_pmu[:, 1]]).T
        z_ang_value = np.array([m_pmu[:, 2]]).T
        fbus_pmu = np.array([m_pmu[:, 5]]).T
        tbus_pmu = np.array([m_pmu[:, 6]]).T
        Ri_mang = np.array([m_pmu[:, 7]]).T
        Ri_ang = np.array([m_pmu[:, 7]]).T

        'PMU'
        vi_pmu = np.argwhere(m_type_pmu == 7)
        ii_pmu = np.argwhere(m_type_pmu == 8)
        nvi_pmu = len(vi_pmu)
        nii_pmu = len(ii_pmu)

        'Total number of measurements'
        nro_measurements = nvi + npi + nqi + npf + nqf + nii + nvi_pmu + nii_pmu
        num_MEAS = {'|Vi|': nvi, 'Pi': npi, 'Qi': nqi, 'Pij': npf, 'Qij': nqf, '|Iij|': nii,
                    'Vi|θ': nvi_pmu, 'Iij|δ': nii_pmu}
        # Measurement redundancy check
        fx_aux.check_observability(nbus, nro_measurements, log_py)

        'Creation and ordering of the vector of SCADA measurements'
        'SCADA measurements'
        matrix_calc_SCADA = Zm_hcalc_Jacobian_Pos(vi, pi, qi, pf, qf, ii, nvi, npi, nqi, npf, nqf, nii)
        matrix_calc_PMU = Zm_hcalc_Jacobian_PMU_SeqPos(vi_pmu, ii_pmu, nvi_pmu, nii_pmu)

        Z_Scada = matrix_calc_SCADA.Z_SCADA(z_value)

        'Phasor measurements(PMU)'
        Vph_magn = np.zeros([nvi_pmu, 1])
        Vph_ang = np.zeros([nvi_pmu, 1])
        for k in range(0, nvi_pmu):
            Vph_magn[k] = z_magn_value[k]
            Vph_ang[k] = z_ang_value[k]

        Iij_real_m = np.zeros([nii_pmu, 1])
        Iij_imag_m = np.zeros([nii_pmu, 1])

        for m in range(0, nii_pmu):
            Iij_real_m[m] = re(cmath.rect(z_magn_value[nvi_pmu + m], z_ang_value[nvi_pmu + m])) * -1
            Iij_imag_m[m] = im(cmath.rect(z_magn_value[nvi_pmu + m], z_ang_value[nvi_pmu + m])) * -1

        Z_med_pmu = np.concatenate((Vph_magn, Vph_ang, Iij_real_m, Iij_imag_m), 0)
        Z_MEAS = np.concatenate((Z_Scada, Z_med_pmu), 0)

        'Form the inverse Rii matrix according to the number of available measurements'
        'SCADA measurements'
        num_Rii = len(vi) + len(pi) + len(qi) + len(pf) + len(qf) + len(ii)
        Rii = vector_Ri_seq(num_Rii, Ri_m)
        Rii_total = np.diagflat(Rii)

        'Phasor measurements (PMU)'
        Rii_pmu = vector_Ri_pmu_seq(nvi_pmu, nii_pmu, Ri_mang, Ri_ang)

        Rii_total = np.concatenate((Rii, Rii_pmu), 0)
        Rii_total = np.diagflat(Rii_total)

        'Initial voltage and angle values'
        Matrix_Mang_Ang_initial = np.array(self.DF_Volt_Ang_initial)
        bus_name = np.array([Matrix_Mang_Ang_initial[:, 1]]).T
        num_nodes = len(np.array([Matrix_Mang_Ang_initial[:, 2]]).T)
        Vsp = np.array([Matrix_Mang_Ang_initial[:, 3]]).T
        theta = np.array([Matrix_Mang_Ang_initial[:, 4]]).T
        E = np.concatenate((theta[1:, :1], Vsp), 0)

        n_Iter = 0
        tol = 5
        n_Iter_ee = self.num_iter_max

        while tol > self.tolerance:
            h_SCADA = matrix_calc_SCADA.h_calculate(fbus_m, tbus_m, Vsp, theta, nbus, self.YBus_Matrix)
            h_PMU = matrix_calc_PMU.h_calc_PMU(fbus_pmu, tbus_pmu, Vsp, theta, self.YBus_Matrix)
            h_calculate = np.concatenate((h_SCADA, h_PMU), 0)

            'residual vector between the vector z(m) existing measurements and h(x) calculated measurements'
            residual = Z_MEAS - h_calculate
            # Jacobian..
            # SCADA measurements
            H_SCD = matrix_calc_SCADA.Jacobian(fbus_m, tbus_m, Vsp, theta, nbus, self.YBus_Matrix)
            H_PMU = matrix_calc_PMU.Jacobian_PMU(fbus_pmu, tbus_pmu, Vsp, theta, nbus, self.YBus_Matrix)

            H = np.concatenate((H_SCD, H_PMU), 0)

            # Gain Matrix, Gm..
            Gm = H.T @ np.linalg.inv(Rii_total) @ H
            # P, L, U = observability_LU_Decomposition(Gm)
            G_inv = fx_aux.calculate_Ginv(Gm, log_py)

            delta_E = G_inv @ (H.T @ np.linalg.inv(Rii_total) @ residual)
            E = E + delta_E

            theta[1:, :] = E[0:nbus - 1]
            Vsp = E[nbus - 1::]
            n_Iter = n_Iter + 1

            if n_Iter < n_Iter_ee:
                tol = max(np.absolute(delta_E))[0]

            if n_Iter_ee <= n_Iter:
                fx_aux.check_num_max_iter(self.num_iter_max, n_Iter, tol, log_py)

        theta = theta * 180 / math.pi
        Vsp = np.array(Vsp).astype(None)
        theta = np.array(theta).astype(None)
        DSSE_results = np.concatenate((bus_name, np.round(Vsp, 4), np.round(theta, 4)), 1)
        DF_DSSE_results = pd.DataFrame(DSSE_results, columns=['Bus Nro.', 'V1(pu)_EST', 'Ang1(deg)_EST'])

        return DF_DSSE_results, n_Iter, tol, num_MEAS

class Zm_hcalc_Jacobian_Pos:

    def __init__(self, vi, pi, qi, pf, qf, ii, nvi, npi, nqi, npf, nqf, nii):
        self.vi = vi
        self.pi = pi
        self.qi = qi
        self.pf = pf
        self.qf = qf
        self.ii = ii
        self.nvi = nvi
        self.npi = npi
        self.nqi = nqi
        self.npf = npf
        self.nqf = nqf
        self.nii = nii

    def Z_SCADA(self, z_value):
        """
        Creation and ordering of the vector of SCADA measurements

        :param z_value: vector of SCADA measurements
        :return:
        """
        'z1 the voltage vector |Vi| measured'
        z1 = np.zeros([self.nvi, 1])
        for i in range(0, self.nvi):
            m = int(self.vi[i, 0])
            z1[i] = z_value[m]

        'z2: Active injection power vector (Pi) measured'
        z2 = np.zeros([self.npi, 1])
        for i in range(0, self.npi):
            m = int(self.pi[i, 0])
            z2[i] = z_value[m]

        'z3: measured injection reactive power vector (Qi)'
        z3 = np.zeros([self.nqi, 1])
        for i in range(0, self.nqi):
            m = int(self.qi[i, 0])
            z3[i] = z_value[m]

        'z4: Flow active power vector (Pij) measured'
        z4 = np.zeros([self.npf, 1])
        for i in range(0, self.npf):
            m = int(self.pf[i, 0])
            z4[i] = z_value[m]

        'z5: Flow reactive power vector (Qij) measured'
        z5 = np.zeros([self.nqf, 1])
        for i in range(0, self.nqf):
            m = int(self.qf[i, 0])
            z5[i] = z_value[m]

        'z6: current vector |Iij| measured'
        z6 = np.zeros([self.nii, 1])
        for i in range(0, self.nii):
            m = int(self.ii[i, 0])
            z6[i] = z_value[m]

        'z1(|Vi|), z2(Pi), z3(Qi), z4(Pij), z5(Qij), z6(Iij)'
        Z_MEAS = np.concatenate((z1, z2, z3, z4, z5, z6), 0)

        return Z_MEAS

    def h_calculate(self, fbus_m, tbus_m, Vsp, theta, nbus, YBus_Matrix):
        f_Pi, f_Qi = sym_func_Pi_Qi()
        f_Pf, f_Qf = sym_func_Pij_Qij()
        #f5, f5_ang = sym_func_Iij()
        f_I_rect = sym_func_Iij_rec()

        # SCADA measurements
        'h1 the voltage vector |Vi| calculated'
        h1 = np.zeros([self.nvi, 1])
        for i in range(0, self.nvi):
            m = int(fbus_m[int(self.vi[i, 0])]) - 1
            h1[i] = Vsp[m]

        'h2: Active injection power vector (Pi) calculated'
        h2 = np.zeros([self.npi, 1])
        for i in range(0, self.npi):
            m = int(fbus_m[int(self.pi[i, 0])]) - 1
            for k in range(0, nbus):
                G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                Pi = f_Pi(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                h2[i] = h2[i] + Pi

        'h3: Calculated injection reactive power vector (Qi)'
        h3 = np.zeros([self.nqi, 1])
        for i in range(0, self.nqi):
            m = int(fbus_m[int(self.qi[i, 0])]) - 1
            for k in range(0, nbus):
                G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                Qi = f_Qi(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                h3[i] = h3[i] + Qi

        'h4: Flow active power vector (Pij) calculated'
        h4 = np.zeros([self.npf, 1])
        for i in range(0, self.npf):
            m = int(fbus_m[int(self.pf[i, 0])]) - 1
            n = int(tbus_m[int(self.pf[i, 0])]) - 1
            G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
            Pij = f_Pf(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
            h4[i] = Pij

        'h5: Flow reactive power vector (Qij) calculated'
        h5 = np.zeros([self.nqf, 1])
        for i in range(0, self.nqf):
            m = int(fbus_m[int(self.qf[i, 0])]) - 1
            n = int(tbus_m[int(self.qf[i, 0])]) - 1
            G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
            Qij = f_Qf(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
            # Qij = im(Qij)
            h5[i] = Qij

        'h6: current vector |Iij| calculated'
        h6 = np.zeros([self.nii, 1])
        for i in range(0, self.nii):
            m = int(fbus_m[int(self.ii[i, 0])]) - 1
            n = int(tbus_m[int(self.ii[i, 0])]) - 1
            G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
            Iij = f_I_rect(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
            h6[i] = pow(((re(Iij)) ** 2 + (im(Iij)) ** 2), 0.5)

        'h1(|Vi|), h2(Pi), h3(Qi), h4(Pij), h5(Qij), h6(Iij)'
        h_calculate = np.concatenate((h1, h2, h3, h4, h5, h6), 0)

        return h_calculate

    def Jacobian(self, fbus_m, tbus_m, Vsp, theta, nbus, YBus_Matrix):
        f30, f31, f32, f33 = sym_func_H61_H62_rec()
        f5_a, f5_b, f6, f7_a, f7_b, f8 = sym_func_H21_H22()
        f9_a, f9_b, f10, f11_a, f11_b, f12 = sym_func_H31_H32()
        f13, f14, f15, f16 = sym_func_H41_H42()
        f17, f18, f19, f20 = sym_func_H51_H52()
        #f21, f22, f23, f24 = sym_func_H61_H62()

        # Jacobian..
        # H11 - Derivative of V with respect to angles.. All Zeros
        H11 = np.zeros([self.nvi, nbus - 1])

        # H12 - Derivative of V with respect to V..
        H12 = np.zeros([self.nvi, nbus])
        for k in range(0, self.nvi):
            for n in range(0, nbus):
                if n == k:
                    H12[k, n] = 1

        'H21, ∂Pi/∂θ Derivatives of Injection Power (Pi) with respect to the angle (θ)'
        H21 = np.zeros([self.npi, nbus - 1])
        for i in range(0, self.npi):
            m = int(fbus_m[int(self.pi[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, k + 1, YBus_Matrix)
                    H21i = f5_a(G1, B1, Vsp[m][0], theta[m][0], Vsp[k + 1][0], theta[k + 1][0])
                    H21[i, k] = H21[i, k] + H21i
                    for n in range(0, nbus):
                        H21i = f5_b(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                        H21[i, k] = H21[i, k] + H21i
                else:
                    G1, B1 = get_G_B_Pos_seq(m, k + 1, YBus_Matrix)
                    H21j = f6(G1, B1, Vsp[m][0], theta[m][0], Vsp[k + 1][0], theta[k + 1][0])
                    H21[i, k] = H21j

        'H22, ∂Pi/∂V Derivatives of Injection Power (Pi) with respect to the voltage (V)'
        H22 = np.zeros([self.npi, nbus])
        for i in range(0, self.npi):
            m = int(fbus_m[int(self.pi[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                    H22i = f7_a(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                    H22[i, k] = H22[i, k] + H22i
                    for n in range(0, nbus):
                        G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                        H22i = f7_b(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                        H22[i, k] = H22[i, k] + H22i
                else:
                    G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                    H22j = f8(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                    H22[i, k] = H22[i, k] + H22j

        'H31, ∂Qi/∂θ Derivatives of Injection Power (Qi) with respect to the angle (θ)'
        H31 = np.zeros([self.nqi, nbus - 1])
        for i in range(0, self.nqi):
            m = int(fbus_m[int(self.qi[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, k + 1, YBus_Matrix)
                    H31i = f9_a(G1, B1, Vsp[m][0], theta[m][0], Vsp[k + 1][0], theta[k + 1][0])
                    H31[i, k] = H31[i, k] + H31i
                    for n in range(0, nbus):
                        G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                        H31i = f9_b(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                        H31[i, k] = H31[i, k] + H31i
                else:
                    G1, B1 = get_G_B_Pos_seq(m, k + 1, YBus_Matrix)
                    H31j = f10(G1, B1, Vsp[m][0], theta[m][0], Vsp[k + 1][0], theta[k + 1][0])
                    H31[i, k] = H31[i, k] + H31j

        'H32, ∂Qi/∂V Derivatives of Injection Power (Pi) with respect to the voltage (V)'
        H32 = np.zeros([self.nqi, nbus])
        for i in range(0, self.nqi):
            m = int(fbus_m[int(self.qi[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                    H32i = f11_a(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                    H32[i, k] = H32[i, k] + H32i
                    for n in range(0, nbus):
                        G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                        H32i = f11_b(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                        H32[i, k] = H32[i, k] + H32i
                else:
                    G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                    H32j = f12(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                    H32[i, k] = H32[i, k] + H32j

        'H41, ∂Pij/∂θ Derivatives of active power of flow (Pij) with respect to the angle (θ)'
        H41 = np.zeros([self.npf, nbus - 1])
        for i in range(0, self.npf):
            m = int(fbus_m[int(self.pf[i, 0])]) - 1
            n = int(tbus_m[int(self.pf[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, k, YBus_Matrix)
                    H41i = f13(G1, B1, Vsp[m][0], theta[m][0], Vsp[k][0], theta[k][0])
                    H41[i, k] = H41[i, k] + H41i
                elif k + 1 == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H41j = f14(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H41[i, k] = H41[i, k] + H41j
                else:
                    H41[i, k] = 0

        'H42, ∂Pij/∂V Derivatives of active power of flow (Pij) with respect to voltage (V)'
        H42 = np.zeros([self.npf, nbus])
        for i in range(0, self.npf):
            m = int(fbus_m[int(self.pf[i, 0])]) - 1
            n = int(tbus_m[int(self.pf[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H42i = f15(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H42[i, k] = H42[i, k] + H42i
                elif k == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H42j = f16(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H42[i, k] = H42[i, k] + H42j
                else:
                    H42[i, k] = 0

        'H51, ∂Qij/∂θ Derivatives of reactive power of flow (Qij) with respect to the angle (θ)'
        H51 = np.zeros([self.nqf, nbus - 1])
        for i in range(0, self.nqf):
            m = int(fbus_m[int(self.qf[i, 0])]) - 1
            n = int(tbus_m[int(self.qf[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H51i = f17(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H51[i, k] = H51[i, k] + H51i

                elif k + 1 == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H51j = f18(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H51[i, k] = H51[i, k] + H51j
                else:
                    H51[i, k] = 0

        'H52, ∂Qij/∂V Derivatives of reactive power of flow (Qij) with respect to voltage (V)'
        H52 = np.zeros([self.nqf, nbus])
        for i in range(0, self.nqf):
            m = int(fbus_m[int(self.qf[i, 0])]) - 1
            n = int(tbus_m[int(self.qf[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H52i = f19(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H52[i, k] = H52[i, k] + H52i
                elif k == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H52j = f20(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H52[i, k] = H52[i, k] + H52j
                else:
                    H52[i, k] = 0

        'H61, ∂|Iij|/∂θ Derivatives of the current magnitude |Iij| with respect to angle (θ)'
        H61 = np.zeros([self.nii, nbus - 1])
        for i in range(0, self.nii):
            m = int(fbus_m[int(self.ii[i, 0])]) - 1
            n = int(tbus_m[int(self.ii[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H61i = f30(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H61i = pow((np.real(H61i) ** 2 + np.imag(H61i) ** 2), 0.5)
                    H61[i, k] = H61[i, k] + H61i

                elif k + 1 == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H61j = f31(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H61j = pow((np.real(H61j) ** 2 + np.imag(H61j) ** 2), 0.5)
                    H61[i, k] = H61[i, k] + H61j

        'H62, ∂|Iij|/∂V Derivatives of the current magnitude |Iij| with respect to voltage (V)'
        H62 = np.zeros([self.nii, nbus])
        for i in range(0, self.nii):
            m = int(fbus_m[int(self.ii[i, 0])]) - 1
            n = int(tbus_m[int(self.ii[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    'H62i'
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H62i = f32(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H62i = pow((np.real(H62i) ** 2 + np.imag(H62i) ** 2), 0.5)
                    H62[i, k] = H62[i, k] + H62i

                elif k == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H62j = f31(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H62j = pow((np.real(H62j) ** 2 + np.imag(H62j) ** 2), 0.5)
                    H62[i, k] = H62[i, k] + H62j

        # SCADA measurements
        H1 = np.concatenate((H11, H12), 1)  # |Vi|
        H2 = np.concatenate((H21, H22), 1)  # Pi
        H3 = np.concatenate((H31, H32), 1)  # Qi
        H4 = np.concatenate((H41, H42), 1)  # Pij
        H5 = np.concatenate((H51, H52), 1)  # Qij
        H6 = np.concatenate((H61, H62), 1)  # Iij

        Jacobian = np.concatenate((H1, H2, H3, H4, H5, H6), 0)

        return Jacobian

class Zm_hcalc_Jacobian_PMU_SeqPos:
    def __init__(self, vi_pmu, ii_pmu, nvi_pmu, nii_pmu):
        self.vi_pmu = vi_pmu
        self.ii_pmu = ii_pmu
        self.nvi_pmu = nvi_pmu
        self.nii_pmu = nii_pmu

    def h_calc_PMU(self, fbus_pmu, tbus_pmu, Vsp, theta, YBus_Matrix):

        f_Iij_rec = sym_func_Iij_rec()
        'Phasor measurements (PMU)'
        'h7 (Voltage magnitude vector (|Vi|) calculated)'
        h7 = np.zeros([self.nvi_pmu, 1])
        for i in range(0, self.nvi_pmu):
            m = int(fbus_pmu[int(self.vi_pmu[i, 0])]) - 1
            h7[i] = Vsp[m]

        'h8 (Voltage angle vector (θi) calculated)'
        h8 = np.zeros([self.nvi_pmu, 1])
        for i in range(0, self.nvi_pmu):
            m = int(fbus_pmu[int(self.vi_pmu[i, 0])]) - 1
            h8[i] = theta[m]

        'h9 (Current magnitude vector (Iij_real) calculated)'
        h9 = np.zeros([self.nii_pmu, 1])
        for i in range(0, self.nii_pmu):
            m = int(fbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            n = int(tbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
            I_ij = f_Iij_rec(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
            h9[i] = re(I_ij)

        'h10 (Current magnitude vector (Iij_img) calculated)'
        h10 = np.zeros([self.nii_pmu, 1])
        for i in range(0, self.nii_pmu):
            m = int(fbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            n = int(tbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
            angI_ij = f_Iij_rec(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
            h10[i] = im(angI_ij)

        h_calculate = np.concatenate((h7, h8, h9, h10), 0)

        return h_calculate

    def Jacobian_PMU(self, fbus_pmu, tbus_pmu, Vsp, theta, nbus, YBus_Matrix):
        f30, f31, f32, f33 = sym_func_H61_H62_rec()
        # Phasor measurements (PMU)'
        'H71, ∂|Vi|/∂θ Derivatives of voltage magnitude measurements (|Vi|) with respect to angle (θ)'
        H71 = np.zeros([self.nvi_pmu, nbus - 1])

        'H72, ∂|Vi|/∂V Derivatives of voltage magnitude measurements (|Vi|) with respect to voltage (V)'
        H72 = np.zeros([self.nvi_pmu, nbus])
        for k in range(0, self.nvi_pmu):
            m = int(fbus_pmu[int(self.vi_pmu[k, 0])]) - 1
            for n in range(0, nbus):
                if n == k:
                    H72[k, m] = 1

        'H81, ∂θi/∂θ Derivatives of voltage angle measurements (θi) with respect to angle (θ)'
        H81 = np.zeros([self.nvi_pmu, nbus - 1])
        for i in range(0, self.nvi_pmu):
            m = int(fbus_pmu[int(self.vi_pmu[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    H81[i, m - 1] = 1

        'H82, ∂θi/∂V Derivatives of voltage angle measurements (θi) with respect to voltage (V)'
        H82 = np.zeros([self.nvi_pmu, nbus])

        'H91, ∂|Iij_real|/∂θ Derivatives of the current magnitude |Iij_real| with respect to angle (θ)'
        H91 = np.zeros([self.nii_pmu, nbus - 1])
        for i in range(0, self.nii_pmu):
            m = int(fbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            n = int(tbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H91i = f30(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H91i = np.real(H91i)
                    H91[i, k] = H91[i, k] + H91i

                elif k + 1 == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H91j = f31(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H91j = np.real(H91j)
                    H91[i, k] = H91[i, k] + H91j

        'H92, ∂|Iij|/∂V Derivatives of the current magnitude |Iij_real| with respect to voltage (V)'
        H92 = np.zeros([self.nii_pmu, nbus])
        for i in range(0, self.nii_pmu):
            m = int(fbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            n = int(tbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H92i = f32(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H92i = np.real(H92i)
                    H92[i, k] = H92[i, k] + H92i

                elif k == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H92j = f33(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H92j = np.real(H92j)
                    H92[i, k] = H92[i, k] + H92j

        'H01, ∂δij/∂θ Derivatives of the current magnitude |Iij_img| with respect to angle (θ)'
        H01 = np.zeros([self.nii_pmu, nbus - 1])
        for i in range(0, self.nii_pmu):
            m = int(fbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            n = int(tbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            for k in range(0, nbus - 1):
                if k + 1 == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H01i = f30(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H01i = np.imag(H01i)
                    H01[i, k] = H01[i, k] + H01i

                elif k + 1 == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H01j = f31(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H01j = np.imag(H01j)
                    H01[i, k] = H01[i, k] + H01j

        'H02, ∂δij/∂V Derivatives of the current  magnitude |Iij_img| with respect to voltage (V)'
        H02 = np.zeros([self.nii_pmu, nbus])
        for i in range(0, self.nii_pmu):
            m = int(fbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            n = int(tbus_pmu[int(self.ii_pmu[i, 0])]) - 1
            for k in range(0, nbus):
                if k == m:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H02i = f32(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H02i = np.imag(H02i)
                    H02[i, k] = H02[i, k] + H02i

                elif k == n:
                    G1, B1 = get_G_B_Pos_seq(m, n, YBus_Matrix)
                    H02j = f33(G1, B1, Vsp[m][0], theta[m][0], Vsp[n][0], theta[n][0])
                    H02j = np.imag(H02j)
                    H02[i, k] = H02[i, k] + H02j

        # Phasor measurements (PMU)'
        H7 = np.concatenate((H71, H72), 1)  # |Vi|
        H8 = np.concatenate((H81, H82), 1)  # θi
        H9 = np.concatenate((H91, H92), 1)  # |Iij_real|
        H0 = np.concatenate((H01, H02), 1)  # |Iij_imag|

        Jacobean_PMU = np.concatenate((H7, H8, H9, H0), 0)

        return Jacobean_PMU