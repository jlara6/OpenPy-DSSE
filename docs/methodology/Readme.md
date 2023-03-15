# State Estimation 

## Mathematical formulation

State estimation is a procedure to obtain an estimate of the operating point of the system defined by the state vector by processing a set of measurements and taking advantage of redundancy to refine and obtain an optimal estimate. This is achieved by applying maximum likelihood estimation (MLE), where it is assumed that the set of measurements $z_{1},z_{2},....., z_{m}$ has measurement errors with a known probability density function $N(μ_i,σ^2)$. The MSE problem, is obtained by solving the minimization problem:

$min\sum_{i=1}^{m}(\frac{z_{i}-\mu _{i}}{\sigma _{i}})^{2}$ (Eq. 1)

Which expressed as a function of the residuals $r_{i}$ of the measurements $z_{i}$ corresponds to $r_{i}=z_{i}-\mu _{i}=z_{i}-E(z_{i})$. The mean $$mu _{i}$, or expected value $E(z_{i})$, can be expressed as a nonlinear function $h_{i}(x)$ that relates the state vector $x$ to the measurement $z_{i}$. The square of each residual $r_{i}^2$ is weighted with the weight of the measurement $z_{i}$ is $W_{ii}=\left ( \frac{1}{\sigma ^{2}} \right )$ reciprocal of the error variance. The minimization problem of (Eq. 1) is equivalent to minimizing the sum of the square of the residuals or solving the optimization problem for the state vector $x$ with an objective function:

$min\sum_{i=1}^{m}W_{ii}\cdot r_{i}^{2}$ (Eq. 2)

Subject to:

$z_{i}= h_{i}\left ( x \right )+r_{i}$ (Eq. 3)

Where $i=1,...,m$. The measurements $z$ as a function of the state vector $x$:

$z = 
\begin{bmatrix}
z_{1} \\
z_{2}\\
\vdots\\
z_{m}
\end{bmatrix} =
\begin{bmatrix}
h_{1}\left ( x_{1},x_{2},\cdots ,x_{n} \right )\\
h_{2}\left ( x_{1},x_{2},\cdots ,x_{n} \right )\\
\vdots\\
h_{m}\left ( x_{1},x_{2},\cdots ,x_{n} \right ) \\
\end{bmatrix} +
\begin{bmatrix}
e_{1} \\
e_{2}\\
\vdots\\
e_{m}
\end{bmatrix} =
h\left (x\right )+e $ (Eq. 4)

Where $h^T=[h_{1}(x),h_{2}(x),...,h_{m}(x)]$ is the function matrix, $x^T=[x_{1},x_{2},...,x_{n}]$ is the state vector and $e^T=[e_{1},e_{2},...,e_{m}]$ is the vector of measurement errors. The statistical properties of the measurement errors:

$\mu _{i} \to E \left ( e_{i} \right )= 0$ (Eq. 5)

Where $i=1,2,...,m$, the independent measurement errors, $E[e_{i} e_{j}]=0$ then:
 
$Cov(e)=E[e\cdot e^T]=R=diag \left \{ \sigma _{1}^{2},\sigma _{2}^{2},\cdots ,\sigma _{m}^{2}\right\}$ (Eq. 6)

The standard deviation $$z_{i}$ for each measurement $z_{i}$ is calculated to reflect the expected accuracy of the corresponding meter used.

## Weighted Least Squares Method (WLS)

It is one of the most widely used techniques in power system state estimation, it solves the optimization problem with the objective function of minimizing the sum of the square of the weighted residuals:

$J(x)=\sum_{m}^{n}\frac{\left ( z_{i}-h_{i}(x) \right )}{R_{ii}}=\left [ z-h(x) \right]^T\cdot R^{-1}\cdot\left [ z-h(x) \right ]$ (Eq. 7).

At the minimum, the optimality condition must be satisfied and is expressed as:

$g\left ( x \right )=\frac{\partial J(x)}{\partial x}=-H(x)^T\cdot R^{-1}\cdot [z-h(x)]=0$ (Eq. 8).

Where $H(x)$ is the Jacobian matrix of the matrix of nonlinear functions $h(x)$:

$H(x)=\left [ \frac{\partial h(x)}{\partial x} \right ]$  (Eq. 9).

Expanding the nonlinear function $g(x)$ in Taylor series around the state vector $x^k$ and by neglecting the higher order terms and using the iterative technique known as the Gauss-Newton method:

$x^{k+1}=x^{k}-\left [ G\left ( x^{k} \right )\right ]\cdot g\left ( x^{k} \right )$ (Eq. 11).

$G\left(x^{k}\right)=\frac{\partial g\left(x_{k}\right )}{\partial x}=H^T\cdot R^{-1}\cdot H\left ( x^{k} \right )$ (Eq. 12).

$g\left (x^{k}\right)=-H^{T}\cdot \left(x^{k}\right)\cdot R^{-1}\cdot \left ( z-h\left ( x^{k} \right ) \right )$ (Eq. 13)

Where $k$ is the index of the iteration; $x^k$ is the solution vector of iteration $k$ and $G(x^k)$ is the gain matrix.

The solution is determined at each iteration by computing $\Delta x^{k+1}$ with:

$\left [G\left (x^{k}\right )\right]\Delta x^{k+1}=H^{T}\left (x^{k}\right)R^{-1} \left [z-h\left ( x_{i}\right)\right ]$ (Eq. 14)

Where $\Delta x^{k+1}=x^{k+1}-x^{k}$ and $G=\left [ H^{T}\left (x_{o}\right)R^{-1}H\left ( x_{o} \right )\right ]$ is the coefficient or gain matrix. The state vector in the first approximation turns out to be $x_{1}=x_{0}+\Delta x$. If the point $x_0$ is not close enough to the value leading to the minimum an iteration should be performed considering $x_1$ as the nominal solution or starting point, the iterative process to compute $x_{x}$ can be expressed as:

$x_{i+1}=x_{i}+\left [ H^{T}\left (x_{i}\right )R^{-1}H\left (x_{i}\right )\right ]^{-1}H^{T}\left (x_{i}\right)R^{-1}\left (z-h\left (x_{i}\right)\right)$ (Eq. 15).

This iterative process continues until the independent term $\Delta x $ is less than a preset tolerance. If the succession of $x_i$ is convergent, then the solution $\hat{x}$ is reached, more details of the algorithm can be found in [1](http://www.crcpress.com/product/isbn/9780824755706).

## Nonlinear Hybrid State Estimator

The model of the Nonlinear State Estimation with D-PMU proceeds in the same way as in the case of conventional measurements. The state vector of voltage $(V_k)$ and Angle $(θ_k)$ where n is the number of circuit nodes, is expressed in polar coordinates $(x=[V_1,V_2,...,V_k,θ_1,θ_2,...,θ_k])$. Starting from a location and type of meters that can be: $V_k, P_k, Q_k, P_{k,m}, Q_{k,m}, I_{k,m}$ in modulus and for $V_k^{pmu}$ and $I_{k,m}^{pmu}$ in polar coordinates, the functions relating the phasor current measurements to the state vector obtained for the generalized $π$ model, taking the admittances in rectangular coordinates [2](https://repositorio.unal.edu.co/handle/unal/51326), leaving $h(x)$ as:

$h(x)^T= \left [ V_k,P_k,Q_k, P_{k,m},Q_{k,m},I_{k,m}, V_k^{pmu},\theta_k^{pmu},(I_{k,m}^{pmu})_r,(I_{k,m}^{pmu})_i \right ]$  (Eq. 16).

The admittance data are extracted from the single-phase (single-phase, starting from a balanced three-phase network) or multiphase circuit modeled in OpenDSS. For a system of mutually coupled multiphase elements they are modeled as electromagnetically decoupled positive sequence impedances in networks with little phase unbalance [3](http://ieeexplore.ieee.org/document/486142/). The vector functions $h(x)$ for both the single-phase and positive-sequence (multiphase) circuit are nonlinear models and formed by the injected power; power flow, branch current, and voltage and current phasor models for both the single-phase and positive-sequence case presented in Table I:

TABLE I. NON-LINEAR FUNCTIONS ACCORDING TO THE TYPE OF MEASUREMENT

|**Type**| **Monophasic**|**Positive Sequence**|
|:---:|:---:|:---:|
|$V_k$|$V_k$|$V_k$|
|$P_k$|$V_k\sum_{m=1}^{n}V_m(G_{k,m}\cdot cos(\theta_k-\theta_m)+B_{k,m}\cdot sin(\theta_k-\theta_m))$|$3P_k$|
|$Q_k$|$V_k\sum_{m=1}^{n}V_m(G_{k,m}\cdot sin(\theta_k-\theta_m)+B_{k,m}\cdot cos(\theta_k-\theta_m))$|$3Q_k$|
|$P_{k,m}$|$V_k(V_m(G_{k,m}\cdot cos(\theta_k-\theta_m)+B_{k,m}\cdot sin(\theta_k-\theta_m)))- V_k(V_k(G_{k,m}\cdot cos(\theta_k-\theta_k)+B_{k,m}\cdot sin(\theta_k-\theta_k)))$|$3P_{k,m}$|
|$Q_{k,m}$|$V_k(V_m(G_{k,m}\cdot sin(\theta_k-\theta_m)+B_{k,m}\cdot cos(\theta_k-\theta_m)))- V_k(V_k(G_{k,m}\cdot sin(\theta_k-\theta_k)+B_{k,m}\cdot cos(\theta_k-\theta_k)))$|$3Q_{k,m}$|
|$I_{k,m}$|$\frac{\sqrt[]{(P_{k,m})^2+(Q_{k,m})^2}}{V_k}$|$\frac{\sqrt[]{(P_{k,m})^2+(Q_{k,m})^2}}{V_k}$|
|$V_k^{pmu}$|$V_k^{pmu}$|$V_k^{pmu}$|
|$\theta_k^{pmu}$|$\theta_k^{pmu}$|$\theta_k^{pmu}$|
|$(I_{k,m}^{pmu})_r$|$(Y_{k,m}\cdot (V_k-V_m))_{real}$|$(Y_{k,m}\cdot (V_k-V_m))_{real}$|
|$(I_{k,m}^{pmu})_i$|$(Y_{k,m}\cdot (V_k-V_m))_{imag}$|$(Y_{k,m}\cdot (V_k-V_m))_{imag}$|

In the equations in Table I, $G_{k,m}$ is the nodal conductance, $B_{k,m}$ is the nodal susceptance and $Y_{k,m}=G_{k,m}+jB_{k,m}$ . The injection measurements $PQ_k$ can be $PQ_{k}^{SM}$, $PQ_{k}^{0}$ and $PQ_{k}^{PSD}$ depending on the case of study. In addition, the variances for the currents in rectangular coordinates are calculated:
 
$\left(\sigma_{ \left(I_{k,m}^{pmu} \right)}^{2} \right)_{real}=(cos^2 \theta _{I_{k,m}})\sigma_{ \left|I_{k,m} \right|}^{2}+( \left|I_{k,m} \right|^2sin^2\theta_{I_{k,m}})\sigma_{\theta_{I_{k,m}}}^2$ (Ec. 7)
 
$ \left(\sigma_{ \left(I_{k,m}^{pmu} \right)}^{2} \right)_{imag}=(sin^2\theta _{I_{k,m}})\sigma_{ \left|I_{k,m} \right|}^{2}+( \left|I_{k,m} \right|^2cos^2\theta_{I_{k,m}})\sigma_{\theta_{I_{k,m}}}^2$ (Ec. 18)

It should be noted that the vector of state variables $x$ has a dimension twice the number of bars minus one $(2×nb-1)$, due to the reference bar of the system, which must be unique for both conventional and phasor measurements. Continuing with the estimation process, the Jacobian matrix $H(x)$ is obtained. 

In summary, to obtain the estimated state, follow the following methodology:
1. initializes the state variables with flat profile $1.0∠0°$.
2. Transforms the phasor current measurements into rectangular components.
3. Calculates the Jacobian matrix employing.
4. Calculate the covariance matrix for the currents in rectangular components (17), and (18).
5. Add to the covariance matrix of conventional measurements ($R_{conv}$), the covariance matrix of phasor voltages ($R_V$) and rectangular currents ($R_I$).
6. Calculate the gain matrix $G(x^k)$.
7. Calculate $∆x^k$ (14).
8. Evaluate the convergence criterion, $max|∆x^k|≤∈, ∈=1×10^{-4}$.
9. If the convergence criterion is not satisfied, update the estimated variables $x^{k+1}=x^k+∆x^k,k=k+1$, and go to step 2, otherwise terminate the algorithm.