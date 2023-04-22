---
title: Estimación de estado 
author: Jorge Lara
date: 10 de marzo de 2023
bibliography: referencias.bib
csl: ieee.csl
---

#  ESTIMACIÓN DE ESTADO 

## Formulación matemática

La estimación de estado es un procedimiento para obtener una estimación del punto de operación del sistema definido por el vector de estado, para ello procesan un conjunto de mediciones y aprovecha la redundancia para depurar y obtener una estimación optima. Esto se logra con aplicación la estimación de máxima verosimilitud (EMV), donde se asume que el conjunto de mediciones $z_{1},z_{2},....., z_{m}$  tiene errores de medición con una función de densidad de probabilidad conocida $N(μ_i,σ^2)$. El problema de EMV, se obtienen resolviendo el problema de minimización:

$min\sum_{i=1}^{m}(\frac{z_{i}-\mu _{i}}{\sigma _{i}})^{2}$ (Ec. 1)

Que expresado en función de los residuos $r_{i}$ de las mediciones $z_{i}$ corresponde a $r_{i}=z_{i}-\mu _{i}=z_{i}-E(z_{i})$. La media $\mu _{i}$ o valor esperado $E(z_{i})$, puede ser expresado como una función no lineal $h_{i}(x)$ que relaciona el vector de estado $x$ con la medición $z_{i}$. El cuadrado de cada residuo $r_{i}^2$ es ponderado con el peso de la medición $z_{i}$ es $W_{ii}=\left ( \frac{1}{\sigma ^{2}} \right )$ reciproca de la varianza de error. El problema de minimización de (Ec. 1) es equivalente a minimizar la suma del cuadrado de los residuos o resolver el problema de optimización para el vector de estado $x$ con función objetivo:
 
$min\sum_{i=1}^{m}W_{ii}\cdot r_{i}^{2}$ (Ec. 2)

Sujeto a:
 
$z_{i}= h_{i}\left ( x \right )+r_{i}$ (Ec. 3)

Donde $i=1,…,m$. Las mediciones $z$ en función del vector de estado $x$:
 
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
h\left (x\right )+e $  (Ec. 4)

Donde $h^T=[h_{1}(x),h_{2}(x),..,h_{m}(x)]$ es la matriz de funciones, $x^T=[x_{1},x_{2},..,x_{n}]$ es el vector de estado y $e^T=[e_{1},e_{2},..,e_{m}]$ es el vector de errores de medición. Las propiedades estadísticas de los errores de mediciones:
 
$\mu _{i}\to E\left ( e_{i} \right )=0$ (Ec. 5)

Donde $i=1,2,…,m$, los errores de medición independientes, $E[e_{i} e_{j}]=0$ entonces:
 
$Cov(e)=E[e\cdot e^T]=R=diag\left\{ \sigma _{1}^{2},\sigma _{2}^{2},\cdots ,\sigma _{m}^{2}\right\}$ (Ec. 6)

La desviación estándar $\sigma _{i}$ para cada medición $z_{i}$ es calculada para reflejar la precisión esperada del correspondiente medidor utilizado.

##	Método de los Mínimos Cuadrados Ponderados (MCP)

Es una de técnica más utilizada en la estimación de estado de los sistemas eléctricos, resuelve el problema de optimización con función objetivo de minimización de la suma del cuadrado de los residuos ponderados:

$J(x)=\sum_{m}^{n}\frac{\left ( z_{i}-h_{i}(x) \right )}{R_{ii}}=\left [ z-h(x) \right]^T\cdot R^{-1}\cdot\left [ z-h(x) \right ]$ (Ec. 7)

En el mínimo, la condición de optimo debe ser satisfecha y se exprese como:
 
$g\left ( x \right )=\frac{\partial J(x)}{\partial x}=-H(x)^T\cdot R^{-1}\cdot [z-h(x)]=0$ (Ec. 8)

Donde $H(x)$ es la matriz jacobiana de la matriz de funciones no lineales $h(x)$:
 
$H(x)=\left [ \frac{\partial h(x)}{\partial x} \right ]$ (Ec. 9)

Expandiendo la función no lineal $g(x)$ en series de Taylor alrededor del vector de estado $x^k$ y al despreciar los términos de mayor orden y utilizando la técnica iterativa conocida como método de Gauss-Newton:
 
$x^{k+1}=x^{k}-\left [ G\left ( x^{k} \right ) \right ]\cdot g\left ( x^{k} \right )$ (Ec. 11)
 
$G\left(x^{k}\right)=\frac{\partial g\left(x_{k}\right )}{\partial x}=H^T\cdot R^{-1}\cdot H\left ( x^{k} \right )$ (Ec. 12)
 
$g\left (x^{k}\right)=-H^{T}\cdot \left(x^{k}\right)\cdot R^{-1}\cdot \left ( z-h\left ( x^{k} \right ) \right )$ (Ec. 13)

Donde $k$ es el índice de la iteración; $x^k$ es el vector solución de la iteración $k$ y $G(x^k)$ es la matriz de ganancia.
 
La solución se determina en cada iteración calculando $\Delta x^{k+1}$ con:
 
$\left [G\left (x^{k}\right )\right]\Delta x^{k+1}=H^{T}\left (x^{k}\right)R^{-1} \left [z-h\left ( x_{i}\right)\right ]$ (Ec. 14)

Donde $\Delta x^{k+1}=x^{k+1}-x^{k}$ y $G=\left [ H^{T}\left (x_{o}\right)R^{-1}H\left ( x_{o} \right )\right ]$ es la matriz de coeficientes o de ganancia. El vector de estado en la primera aproximación resulta $x_{1}=x_{0}+\Delta x$. Si el punto $x_0$ no está lo suficientemente próximo al valor que conduce al mínimo deberá realizarse una iteración considerando $x_1$ como solución nominal o punto de partida, el proceso iterativo para calcular $\hat{x}$ se puede expresar como:
 
$x_{i+1}=x_{i}+\left [ H^{T}\left (x_{i}\right )R^{-1}H\left (x_{i}\right )\right ]^{-1}H^{T}\left (x_{i}\right)R^{-1}\left (z-h\left (x_{i}\right)\right)$ (Ec. 15)

Este proceso iterativo continua hasta que el termino independiente $\Delta x $ es menor a una tolerancia prefijada. Si la sucesión de $x_i$ es convergente, se alcanza la solución $\hat{x}$, mayor detalle del algoritmo puede ver en [@Abur2004](http://www.crcpress.com/product/isbn/9780824755706).

## Estimador de Estado Hibrido No Lineal

El modelo de la Estimación de Estado No Lineal con D-PMU, procede de la misma forma que en el caso de mediciones convencionales.  El vector de estado de voltaje $(V_k)$ y Angulo $(θ_k)$ donde n es el número de nodos de circuito, se expresa en coordenadas polares $(x=[V_1,V_2,…,V_k,θ_1,θ_2,…,θ_k])$. A partir de una ubicación y tipo de medidores que pueden ser:  $V_k, P_k, Q_k, P_{k,m}, Q_{k,m}, I_{k,m}$ en módulo y para $V_k^{pmu}$ y $I_{k,m}^{pmu}$   en coordenadas polares, las funciones que relacionan las mediciones fasoriales de corriente con el vector de estado que se obtiene para el modelo $π$ generalizado, tomando las admitancias en coordenadas rectangulares [@Rincón2013](https://repositorio.unal.edu.co/handle/unal/51326), quedando $h(x)$ como:
 
$h(x)^T=\left [ V_k,P_k,Q_k, P_{k,m},Q_{k,m},I_{k,m}, V_k^{pmu},\theta_k^{pmu},(I_{k,m}^{pmu})_r,(I_{k,m}^{pmu})_i\right ]$ (Ec. 16)

Los datos de admitancias se extraen del circuito monofásico (unifilar, que parte de una red trifásica equilibrada) o multifásico modelado en OpenDSS. Para un sistema de elementos multifásicos mutuamente acoplados se modelan como impedancias de secuencia positiva desacopladas electromagnéticamente en redes con poco desequilibrio de fases [@Whei-MinLin1996](http://ieeexplore.ieee.org/document/486142/). Las funciones del vector $h(x)$ tanto para el circuito monofásico y de secuencia positiva (multifásico) son modelos no lineales y formados por los modelos de potencia inyectada; flujo de potencia, corriente de rama y fasoriales de tensión y corriente tanto para el caso monofásico y secuencia positiva que se presentan en la Tabla I:

TABLA I. FUNCIONES NO LINEALES SEGÚN EL TIPO DE MEDICIÓN

| **Tipo**| **Monófasico**| **Secuencia Positiva**|
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

En las ecuaciones de la tabla I, $G_{k,m}$ es la conductancia nodal, $B_{k,m}$ es la susceptancia nodal y $Y_{k,m}=G_{k,m}+jB_{k,m}$ . Las mediciones de inyección $PQ_k$ pueden ser $PQ_{k}^{SM}$, $PQ_{k}^{0}$ y $PQ_{k}^{PSD}$ según sea el caso de estudio. Además, se calculan las varianzas para las corrientes en coordenadas rectangulares:
 
$\left(\sigma_{\left(I_{k,m}^{pmu}\right)}^{2}\right)_{real}=(cos^2\theta _{I_{k,m}})\sigma_{\left|I_{k,m}\right|}^{2}+(\left|I_{k,m}\right|^2sin^2\theta_{I_{k,m}})\sigma_{\theta_{I_{k,m}}}^2$ (Ec. 7)
 
$\left(\sigma_{\left(I_{k,m}^{pmu}\right)}^{2}\right)_{imag}=(sin^2\theta _{I_{k,m}})\sigma_{\left|I_{k,m}\right|}^{2}+(\left|I_{k,m}\right|^2cos^2\theta_{I_{k,m}})\sigma_{\theta_{I_{k,m}}}^2$ (Ec. 18)

Se debe tener en cuenta que el vector de variables de estado $x$ tiene una dimensión dos veces el número de barras menos uno $(2×nb-1)$, debido a la barra de referencia del sistema, la cual debe ser única tanto para las mediciones convencionales como fasoriales. Continuando con el proceso de estimación, se obtiene la matriz jacobiana $H(x)$. 

En resumen, para obtener el estado estimado, sigue la siguiente metodología:
1. Inicia las variables de estado con perfil plano $1.0∠0°$
2. Transforma las mediciones fasoriales de corriente en componentes rectangulares.
3. Calcula la matriz jacobiana empleando.
4. Calcula la matriz de covarianzas para las corrientes en componentes rectangulares (17), (18).
5. Añade a la matriz de covarianza de mediciones convencionales ($R_{conv}$), la matriz de covarianzas de voltajes fasoriales ($R_V$) y corrientes rectangulares ($R_I$).
6. Calcula la matriz de ganancia $G(x^k)$.
7. Calcula $∆x^k$ (14) 
8. Evalúa el criterio de convergencia, $max|∆x^k|≤∈, ∈=1×10^{-4}$
9. Si no se cumple el criterio de convergencia, actualiza las variables estimadas $x^{k+1}=x^k+∆x^k,k=k+1$, e ir al paso 2, caso contrario finalizar el algoritmo.


