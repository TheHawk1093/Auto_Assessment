# -*- coding: utf-8 -*-
"""Variant library for ME 5309 midsem synthetic answer sheets.
VAR[(question, part, variant)] = dict(m=marks, ty=error category, e=description, t=[paragraphs])
Placeholders: §t -> theta-dot, §tt -> theta-double-dot, §x -> x-dot
"""
VAR = {}


def V(q, p, k, m, ty, e, *t):
    VAR[(q, p, k)] = dict(m=m, ty=ty, e=e, t=list(t))


MAX = {('Q1', 'a'): 4, ('Q1', 'b'): 3, ('Q1', 'c'): 3,
       ('Q2', 'a'): 2, ('Q2', 'b'): 2, ('Q2', 'c'): 4, ('Q2', 'd'): 2,
       ('Q3', 'a'): 2, ('Q3', 'b'): 2, ('Q3', 'c'): 4, ('Q3', 'd'): 2,
       ('Q4', 'a'): 2, ('Q4', 'b'): 2, ('Q4', 'c'): 4, ('Q4', 'd'): 2}

GIVEN = {
    'Q1': "Given: sensor 1280 px wide, pixel pitch p = 5 µm (square), lens f = 16 mm, standoff Z = 400 mm; force sensor 10 mV/N, 12-bit ADC over 0–5 V; plant §x = −2x + u with zero-order hold, T = 0.1 s.",
    'Q2': "Given: J = 0.02 kg·m², b = 0.05 N·m·s/rad, m = 1 kg, ℓ = 0.25 m, g = 9.81 m/s². So mgℓ = 1 × 9.81 × 0.25 = 2.4525 N·m (used throughout).",
    'Q3': "Given: A = [0, 1; 0, −2], B = [0; 1], C = [1, 0], f<sub>s</sub> = 1 kHz so the sample time is T = 1/f<sub>s</sub> = 1 ms.",
    'Q4': "Given: plant θ̈ + aθ̇ + cθ = b u with a = 2, c = 6, b = 1; controller u = N<sub>ff</sub> r − k<sub>1</sub>θ − k<sub>2</sub>θ̇.",
}
GIVEN = {k: v.replace('§x', 'ẋ') for k, v in GIVEN.items()}

# ------------------------------------------------------------------ Q1 (a)
V('Q1', 'a', 'ok_T', 4, '', '',
  "(i) f<sub>x</sub> = f / p = 16 mm / 5 µm = 16×10<super>-3</super> / 5×10<super>-6</super> = <b>3200 px</b>.",
  "(ii) Sensor width W<sub>s</sub> = 1280 × 5 µm = 6.4 mm. By similar triangles FOV = W<sub>s</sub>·Z / f = 6.4 × 400 / 16 = <b>160 mm</b>.",
  "Distance per pixel = FOV / 1280 = 160/1280 = <b>0.125 mm/px</b> (check: Z/f<sub>x</sub> = 400/3200 = 0.125 mm/px).")
V('Q1', 'a', 'ok_V', 4, '', '',
  "Assumptions: pinhole (thin-lens) camera model, lens focused on the belt plane, belt plane perpendicular to the optical axis, no lens distortion, so every pixel images the same length on the belt.",
  "(i) The focal length in pixel units is the physical focal length divided by the pixel pitch: f<sub>x</sub> = f/p = (16×10<super>-3</super> m)/(5×10<super>-6</super> m) = 3200. The metres cancel so the answer is in pixels. <b>f<sub>x</sub> = 3200 px</b>.",
  "(ii) Width of the sensor = N·p = 1280 × 5 µm = 6400 µm = 6.4 mm. Using similar triangles between the sensor and the belt plane, W<sub>s</sub>/f = FOV/Z, hence FOV = W<sub>s</sub>·Z/f = (6.4 mm)(400 mm)/(16 mm) = 160 mm. <b>FOV = 160 mm</b>.",
  "Ground sampling distance = FOV/N = 160 mm / 1280 px = 0.125 mm/px. Cross-check with the pixel-based formula Z/f<sub>x</sub> = 400 mm / 3200 px = 0.125 mm/px; both agree, so <b>1 pixel = 0.125 mm = 125 µm</b> on the belt.")
V('Q1', 'a', 'ok_2sf', 3.5, 'Unit/Precision', 'Per-pixel distance reported to 2 s.f. (0.13 mm/px), violating the 3-s.f. instruction (-0.5)',
  "(i) f<sub>x</sub> = f / p = 16 mm / 5 µm = <b>3200 px</b>.",
  "(ii) W<sub>s</sub> = 1280 × 5 µm = 6.4 mm. FOV = W<sub>s</sub>·Z/f = 6.4 × 400/16 = <b>160 mm</b>.",
  "Per pixel = 160/1280 ≈ <b>0.13 mm/px</b>.")
V('Q1', 'a', 'e1', 2.0, 'Unit conversion', 'Unit slip: 16 mm / 5 µm evaluated as 16/5 = 3.2 (µm not converted); FOV and per-pixel values absurd but formulas right (error carried forward)',
  "(i) f<sub>x</sub> = f/p = 16/5 = <b>3.2 px</b>.",
  "(ii) Width of sensor = 1280 × 5 = 6400. FOV = N·Z/f<sub>x</sub> = 1280 × 400 / 3.2 = <b>160000 mm</b>.",
  "One pixel = FOV/N = 160000/1280 = <b>125 mm per pixel</b>. (looks large but the formula is right)")
V('Q1', 'a', 'e2', 2.0, 'Conceptual', 'Similar-triangle ratio inverted (f/Z instead of Z/f): FOV = 0.256 mm instead of 160 mm; f_x correct',
  "(i) f<sub>x</sub> = f/p = 16×10<super>-3</super> / 5×10<super>-6</super> = <b>3200 px</b>.",
  "(ii) Sensor width = 1280 × 5 µm = 6.4 mm. Using similar triangles, FOV = W<sub>s</sub>·f / Z = 6.4 × 16/400 = <b>0.256 mm</b>.",
  "Distance per pixel = FOV/1280 = 0.256/1280 = <b>2×10<super>-4</super> mm</b> = 0.2 µm.")
V('Q1', 'a', 'bare', 0, 'Missing working', 'Final answers only; no formula or substitution (instruction 5 gives no credit)',
  "f<sub>x</sub> = 3200 px. FOV = 160 mm. 1 pixel = 0.125 mm.")

# ------------------------------------------------------------------ Q1 (b)
V('Q1', 'b', 'ok_T', 3, '', '',
  "LSB = V<sub>range</sub>/2<super>n</super> = 5 V / 2<super>12</super> = 5/4096 = 1.2207 mV.",
  "Smallest resolvable force ΔF = LSB / S = 1.2207 mV / (10 mV/N) = <b>0.1221 N</b>.")
V('Q1', 'b', 'ok_V', 3, '', '',
  "Assumptions: ideal 12-bit ADC (4096 codes), the full 0–5 V range is used, no offset or gain error, and sensor noise is below one LSB so quantisation sets the limit.",
  "Voltage step: 1 LSB = V<sub>FS</sub>/2<super>N</super> = 5 V/4096 = 1.2207×10<super>-3</super> V = 1.2207 mV.",
  "The sensor maps force to voltage by V = S·F with S = 10 mV/N, so ΔF<sub>min</sub> = ΔV/S = 1.2207 mV / (10 mV/N) = 0.12207 N. <b>ΔF<sub>min</sub> ≈ 0.122 N</b>. (Using 4095 steps instead of 4096 codes gives 0.1221 N, the same at 3 s.f.)")
V('Q1', 'b', 'ok_nu', 2.5, 'Unit/Precision', 'Final answer written without units (-0.5)',
  "LSB = 5/2<super>12</super> = 5/4096 = 1.2207 mV.",
  "ΔF = LSB/S = 1.2207/10 = <b>0.122</b>")
V('Q1', 'b', 'e1', 1.5, 'Incomplete', 'Stopped at ADC LSB voltage; never converted to force via sensor sensitivity',
  "Resolution of the ADC = V<sub>range</sub>/2<super>n</super> = 5 V / 4096 = 1.22×10<super>-3</super> V = <b>1.22 mV</b>.",
  "So the smallest change the system can resolve is 1.22 mV.")
V('Q1', 'b', 'e2', 2.5, 'Calculation', 'Decimal-place slip in final division (0.0122 N instead of 0.122 N); method correct',
  "LSB = 5/4096 = 1.2207 mV.",
  "ΔF = LSB / S = 1.2207 mV / 10 mV/N = <b>0.0122 N</b>.")
V('Q1', 'b', 'bare', 0, 'Missing working', 'Bare numeric answer; no formula or substitution (no credit under instruction 5)',
  "Answer: 0.122 N.")

# ------------------------------------------------------------------ Q1 (c)
V('Q1', 'c', 'ok_T', 3, '', '',
  "ZOH discretisation: F = e<super>AT</super>, G = ∫<sub>0</sub><super>T</super> e<super>Aτ</super>B dτ = A<super>-1</super>(F − I)B (A ≠ 0).",
  "Here A = −2, B = 1, T = 0.1: F = e<super>−0.2</super> = <b>0.8187</b>. G = (F − 1)/A = (0.8187 − 1)/(−2) = <b>0.0906</b>.",
  "x<sub>k+1</sub> = 0.8187 x<sub>k</sub> + 0.0906 u<sub>k</sub>.")
V('Q1', 'c', 'ok_V', 3, '', '',
  "With u held constant over [kT, (k+1)T] (zero-order hold) the variation-of-constants formula gives x((k+1)T) = e<super>AT</super> x(kT) + ∫<sub>0</sub><super>T</super> e<super>A(T−s)</super> B u(kT) ds. Since u(kT) is constant it leaves the integral, so F = e<super>AT</super> and G = ∫<sub>0</sub><super>T</super> e<super>Aσ</super> B dσ = A<super>-1</super>(e<super>AT</super> − I)B for invertible A.",
  "Substituting A = −2, B = 1, T = 0.1 s: F = e<super>−0.2</super> = 0.81873. G = (0.81873 − 1)/(−2) = 0.090635.",
  "Sanity check: the DC gain of the continuous plant is −A<super>-1</super>B = 0.5, and the discrete DC gain G/(1 − F) = 0.090635/0.18127 = 0.5 ✓.",
  "<b>x<sub>k+1</sub> = 0.8187 x<sub>k</sub> + 0.0906 u<sub>k</sub></b>")
V('Q1', 'c', 'e1', 0, 'Method', 'Used forward-Euler instead of the exact ZOH discretisation (F=0.8, G=0.1); question demands exact model',
  "Using forward Euler: x<sub>k+1</sub> = x<sub>k</sub> + T(A x<sub>k</sub> + B u<sub>k</sub>), so F = 1 + AT and G = BT.",
  "F = 1 + (−2)(0.1) = <b>0.8</b>, G = 1 × 0.1 = <b>0.1</b>.",
  "x<sub>k+1</sub> = 0.8 x<sub>k</sub> + 0.1 u<sub>k</sub>.")
V('Q1', 'c', 'e2', 2.0, 'Calculation', 'Integration slip: ∫e^(−2τ)dτ taken as 1−e^(−0.2) (missing 1/2): G = 0.1813 instead of 0.0906; F and formulas right',
  "F = e<super>AT</super> and G = ∫<sub>0</sub><super>T</super> e<super>Aτ</super> B dτ.",
  "F = e<super>−0.2</super> = <b>0.8187</b>.",
  "G = ∫<sub>0</sub><super>0.1</super> e<super>−2τ</super> dτ = 1 − e<super>−0.2</super> = <b>0.1813</b>.")
V('Q1', 'c', 'e3', 2.0, 'Misread data', 'Sampling period misread as 0.01 s (should be 0.1 s); formulas right, numbers consistently wrong (F=0.9802, G=0.0099)',
  "F = e<super>AT</super>, G = A<super>-1</super>(F − I)B. Taking T = 0.01 s.",
  "F = e<super>−0.02</super> = <b>0.9802</b>.",
  "G = (0.9802 − 1)/(−2) = <b>0.0099</b>.")

# ------------------------------------------------------------------ Q2 (a)
V('Q2', 'a', 'ok_T', 2, '', '',
  "States x<sub>1</sub> = θ, x<sub>2</sub> = §t. §x<sub>1</sub> = x<sub>2</sub>; §x<sub>2</sub> = (1/J)[τ − b x<sub>2</sub> − mgℓ sin x<sub>1</sub>].",
  "Equilibria (τ = τ<sub>0</sub>, §x = 0): x<sub>2</sub> = 0 and mgℓ sin θ<sub>e</sub> = τ<sub>0</sub>. Since |sin θ| ≤ 1, an equilibrium exists iff |τ<sub>0</sub>| ≤ mgℓ = 2.4525 N·m.")
V('Q2', 'a', 'ok_V', 2, '', '',
  "The model is second order, so I choose the position and velocity as states: x = [x<sub>1</sub>, x<sub>2</sub>]<super>T</super> = [θ, §t]<super>T</super>, with input τ.",
  "Rewriting J§tt + b§t + mgℓ sin θ = τ gives the nonlinear state-space model: §x<sub>1</sub> = x<sub>2</sub>, §x<sub>2</sub> = (1/J)(τ − b x<sub>2</sub> − mgℓ sin x<sub>1</sub>), i.e. §x = f(x, τ).",
  "Equilibria for constant τ<sub>0</sub> need §x = 0: the first equation gives x<sub>2</sub> = 0, and the second then gives mgℓ sin θ<sub>e</sub> = τ<sub>0</sub>, i.e. sin θ<sub>e</sub> = τ<sub>0</sub>/(mgℓ).",
  "This has a solution only if |τ<sub>0</sub>/(mgℓ)| ≤ 1, so <b>|τ<sub>0</sub>| ≤ mgℓ = 2.4525 N·m</b>. For |τ<sub>0</sub>| < mgℓ there are two equilibria per revolution (θ<sub>e</sub> and π − θ<sub>e</sub>); at |τ<sub>0</sub>| = mgℓ they merge, and beyond it the joint cannot be held statically.")
V('Q2', 'a', 'e1', 1.5, 'Incomplete', 'Equilibrium range given as 0 <= tau0 <= mgl; misses negative torques (should be |tau0| <= mgl)',
  "x<sub>1</sub> = θ, x<sub>2</sub> = §t. §x<sub>1</sub> = x<sub>2</sub>, §x<sub>2</sub> = (τ − b x<sub>2</sub> − mgℓ sin x<sub>1</sub>)/J.",
  "At equilibrium x<sub>2</sub> = 0 and sin θ<sub>e</sub> = τ<sub>0</sub>/(mgℓ), so 0 ≤ τ<sub>0</sub> ≤ mgℓ = 2.45 N·m.")
V('Q2', 'a', 'e2', 1.5, 'Sign error', 'Sign error on damping term in state equation (+b x2); equilibrium condition and range correct',
  "Let x<sub>1</sub> = θ and x<sub>2</sub> = §t. §x<sub>1</sub> = x<sub>2</sub>; §x<sub>2</sub> = (1/J)[τ + b x<sub>2</sub> − mgℓ sin x<sub>1</sub>].",
  "Equilibrium: x<sub>2</sub> = 0 and mgℓ sin θ<sub>e</sub> = τ<sub>0</sub>. Because −1 ≤ sin θ ≤ 1 we need |τ<sub>0</sub>| ≤ mgℓ = 2.4525 N·m.")
V('Q2', 'a', 'e3', 1.0, 'Conceptual', 'Claims an equilibrium exists for every tau0 (ignores |sin|<=1 so |tau0|<=mgl); model correct',
  "x<sub>1</sub> = θ, x<sub>2</sub> = §t. §x<sub>1</sub> = x<sub>2</sub>, §x<sub>2</sub> = (1/J)(τ − b x<sub>2</sub> − mgℓ sin x<sub>1</sub>).",
  "Equilibrium means §x = 0, so x<sub>2</sub> = 0 and mgℓ sin θ<sub>e</sub> = τ<sub>0</sub>. Since sine is periodic we can always find a θ<sub>e</sub> that satisfies this, so an equilibrium exists for any τ<sub>0</sub>.")

# ------------------------------------------------------------------ Q2 (b)
V('Q2', 'b', 'ok_T', 2, '', '',
  "δ§x = A δx + B δτ, A = ∂f/∂x, B = ∂f/∂τ at θ<sub>e</sub> = 60°, x<sub>2e</sub> = 0.",
  "A = [0, 1; −(mgℓ/J) cos θ<sub>e</sub>, −b/J] = [0, 1; −122.6×0.5, −2.5] = <b>[0, 1; −61.31, −2.5]</b>.",
  "B = [0; 1/J] = <b>[0; 50]</b>.")
V('Q2', 'b', 'ok_V', 2, '', '',
  "The equilibrium at θ<sub>e</sub> = 60° needs the torque τ<sub>e</sub> = mgℓ sin 60° = 2.4525 × 0.8660 = 2.124 N·m. Define deviations δx = x − x<sub>e</sub> with x<sub>e</sub> = [60°, 0]<super>T</super> and δτ = τ − τ<sub>e</sub>; then δ§x ≈ A δx + B δτ with the Jacobians evaluated at the equilibrium.",
  "∂f<sub>1</sub>/∂x = [0, 1]. ∂f<sub>2</sub>/∂x<sub>1</sub> = −(mgℓ/J) cos x<sub>1</sub> = −(2.4525/0.02)(0.5) = −122.625 × 0.5 = −61.31 (s<super>-2</super>). ∂f<sub>2</sub>/∂x<sub>2</sub> = −b/J = −0.05/0.02 = −2.5 s<super>-1</super>.",
  "<b>A = [0, 1; −61.31, −2.5]</b>, and since ∂f<sub>2</sub>/∂τ = 1/J = 50, <b>B = [0; 50]</b>.",
  "Check: the characteristic equation λ² + 2.5λ + 61.31 = 0 gives λ = −1.25 ± 7.73j, a lightly damped stable oscillation, as expected for a pendulum hanging near-vertical (60° below the downward vertical).")
V('Q2', 'b', 'e1', 1.0, 'Calculation', 'Calculator left in radian mode: cos(60) = -0.952 gives A21 = +116.8 instead of -61.31; structure, A22 and B right',
  "Jacobian at θ<sub>e</sub> = 60°: A = [0, 1; −(mgℓ/J) cos θ<sub>e</sub>, −b/J].",
  "mgℓ/J = 2.4525/0.02 = 122.625; cos(60) = −0.9524, so A<sub>21</sub> = −122.625 × (−0.9524) = +116.8. A<sub>22</sub> = −b/J = −2.5.",
  "<b>A = [0, 1; 116.8, −2.5]</b>, <b>B = [0; 50]</b>.")
V('Q2', 'b', 'e2', 1.0, 'Conceptual', 'Used sin(theta_e) instead of cos(theta_e) in the Jacobian: A21 = -106.2 (should be -61.31)',
  "Linearising: A = [0, 1; ∂f<sub>2</sub>/∂x<sub>1</sub>, ∂f<sub>2</sub>/∂x<sub>2</sub>].",
  "∂f<sub>2</sub>/∂x<sub>1</sub> = −(mgℓ/J) sin θ<sub>e</sub> = −122.625 × 0.8660 = −106.2. ∂f<sub>2</sub>/∂x<sub>2</sub> = −b/J = −2.5.",
  "<b>A = [0, 1; −106.2, −2.5]</b>, B = [0; 1/J] = <b>[0; 50]</b>.")
V('Q2', 'b', 'e3', 1.5, 'Incomplete', 'B given as [0;1], omitting the 1/J = 50 factor; A fully correct',
  "A = [0, 1; −(mgℓ/J) cos 60°, −b/J] = <b>[0, 1; −61.31, −2.5]</b>.",
  "B = ∂f/∂τ = [0; 1] (the torque enters directly) so <b>B = [0; 1]</b>.")

# ------------------------------------------------------------------ Q2 (c)
V('Q2', 'c', 'ok_T', 4, '', '',
  "At rest §t = §tt = 0, so the PD torque must balance gravity: K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = mgℓ sin θ<sub>ss</sub>.",
  "If θ<sub>ss</sub> = θ<sub>d</sub> = 90° the left side is 0 but the right side is mgℓ sin 90° = 2.4525 ≠ 0: contradiction. So the joint cannot rest at θ<sub>d</sub>; the gravity torque needs a non-zero error to produce the holding torque.",
  "Solve 50(π/2 − θ<sub>ss</sub>) = 2.4525 sin θ<sub>ss</sub> numerically: θ<sub>ss</sub> ≈ 1.5218 rad = 87.19°. Error ≈ 90° − 87.19° = <b>2.81°</b> (joint sags below θ<sub>d</sub>).")
V('Q2', 'c', 'ok_V', 4, '', '',
  "Set all time derivatives to zero in the closed loop. With τ = K<sub>p</sub>(θ<sub>d</sub> − θ) − K<sub>d</sub>§t and §t = §tt = 0 the damper term vanishes (so K<sub>d</sub> has no effect on the final position) and the dynamics reduce to mgℓ sin θ<sub>ss</sub> = K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>).",
  "Why θ<sub>ss</sub> ≠ θ<sub>d</sub>: if the joint were at rest exactly at θ<sub>d</sub> = 90° the PD torque would be K<sub>p</sub>·0 − K<sub>d</sub>·0 = 0, yet gravity pulls with mgℓ sin 90° = 2.4525 N·m. The net torque would be non-zero, so the joint could not be at rest. A purely proportional-derivative law can only hold a load if there is a steady error.",
  "Let e = θ<sub>d</sub> − θ<sub>ss</sub> (in rad). Then sin θ<sub>ss</sub> = sin(π/2 − e) = cos e, and the equation becomes 50 e = 2.4525 cos e. Fixed-point iteration: e<sub>0</sub> = 2.4525/50 = 0.04905 (taking cos e ≈ 1); e<sub>1</sub> = 0.04905 × cos(0.04905) = 0.04899; e<sub>2</sub> = 0.04905 × cos(0.04899) = 0.04899, converged.",
  "e = 0.04899 rad × (180/π) = 2.807°, so θ<sub>ss</sub> = 87.19°. <b>Steady-state error ≈ 2.81° (the arm sags below the target).</b> This is small because K<sub>p</sub> is much larger than mgℓ (K<sub>p</sub>/mgℓ ≈ 20).")
V('Q2', 'c', 'ok_approx', 4, 'Valid alternative', 'Used the small-error estimate sin(theta_ss) ~ 1 giving 2.81 deg; acceptable because the question asks to estimate (full marks expected)',
  "At rest §t = §tt = 0 so K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = mgℓ sin θ<sub>ss</sub>. At θ<sub>d</sub> the right side would be 2.4525 ≠ 0, so the error cannot be zero.",
  "Estimate: θ<sub>ss</sub> ≈ θ<sub>d</sub> so sin θ<sub>ss</sub> ≈ 1; error e ≈ mgℓ/K<sub>p</sub> = 2.4525/50 = 0.0491 rad = <b>2.81°</b>.")
V('Q2', 'c', 'e2', 2.0, 'Unit conversion', 'theta_d entered in degrees while Kp is in N.m/rad (unit inconsistency): error 0.049 deg instead of 2.81 deg; reasoning right',
  "At rest §t = §tt = 0, so K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = mgℓ sin θ<sub>ss</sub>, i.e. 50(90 − θ<sub>ss</sub>) = 2.4525 sin θ<sub>ss</sub>.",
  "Gravity torque is non-zero at 90°, so the left side can't be zero, hence θ<sub>ss</sub> ≠ θ<sub>d</sub>.",
  "Taking sin θ<sub>ss</sub> ≈ 1: 90 − θ<sub>ss</sub> = 2.4525/50 = 0.049, so the steady-state error ≈ <b>0.049°</b>.")
V('Q2', 'c', 'e3', 0.5, 'Conceptual', 'Claims PD drives error to zero and ignores gravity at steady state; only states theta-dot = theta-ddot = 0',
  "At steady state §t = 0 and §tt = 0.",
  "A PD controller is stable and its job is to drive (θ<sub>d</sub> − θ) to zero, so θ<sub>ss</sub> = θ<sub>d</sub> = 90°. The gravity term only affects the transient. Hence the steady-state error is <b>0°</b> and the joint does come to rest at θ<sub>d</sub>.")
V('Q2', 'c', 'e4', 2.5, 'Calculation', 'Decimal slip: 2.4525/50 evaluated as 0.00491 rad giving 0.281 deg instead of 2.81 deg; reasoning and equation correct',
  "At rest §t = §tt = 0: K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = mgℓ sin θ<sub>ss</sub> = 2.4525 sin θ<sub>ss</sub>. At θ<sub>d</sub> = 90° the right side ≠ 0 while the left side = 0, so the joint cannot rest at θ<sub>d</sub>.",
  "With sin θ<sub>ss</sub> ≈ 1: θ<sub>d</sub> − θ<sub>ss</sub> = 2.4525/50 = 0.00491 rad = <b>0.281°</b>.")

# ------------------------------------------------------------------ Q2 (d)
V('Q2', 'd', 'ok_T', 2, '', '',
  "With compensation, at rest: K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) + mgℓ sin θ<sub>ss</sub> = mgℓ sin θ<sub>ss</sub> ⇒ θ<sub>ss</sub> = θ<sub>d</sub>: <b>steady-state error = 0</b>.",
  "Closed loop: J§tt + (b + K<sub>d</sub>)§t + K<sub>p</sub>(θ − θ<sub>d</sub>) = 0; gravity cancels. Without compensation the linearised stiffness is K<sub>p</sub> + mgℓ cos θ<sub>d</sub>, and at θ<sub>d</sub> = 90° cos θ<sub>d</sub> = 0, so the stiffness is K<sub>p</sub> either way. <b>Poles unchanged</b> (specific to 90°; at other angles they would shift).")
V('Q2', 'd', 'ok_V', 2, '', '',
  "Steady state: §t = §tt = 0 and the control law gives τ = K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) + mgℓ sin θ<sub>ss</sub>. Plugging into the plant, mgℓ sin θ<sub>ss</sub> = K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) + mgℓ sin θ<sub>ss</sub>, so K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = 0 and <b>θ<sub>ss</sub> = θ<sub>d</sub>: steady-state error is zero</b>.",
  "Poles: linearise the closed loop about θ<sub>d</sub>. Before compensation, J§tt + (b + K<sub>d</sub>)§t + (K<sub>p</sub> + mgℓ cos θ<sub>d</sub>) δθ = 0, characteristic polynomial Jλ² + (b + K<sub>d</sub>)λ + K<sub>p</sub> + mgℓ cos θ<sub>d</sub>. After compensation the added term mgℓ sin θ cancels the plant's gravity term exactly, leaving Jλ² + (b + K<sub>d</sub>)λ + K<sub>p</sub>.",
  "The two differ only by mgℓ cos θ<sub>d</sub>, and for θ<sub>d</sub> = 90° this is 2.4525 × 0 = 0. So <b>the closed-loop poles are unchanged</b> at this operating angle. I should stress this is because cos 90° = 0; if θ<sub>d</sub> were, say, 60°, the compensation would raise the stiffness by 61.3 × 0.02... i.e. it would move the poles.")
V('Q2', 'd', 'e1', 1.0, 'Conceptual', 'Error = 0 correct, but claims poles change (ignores cos 90 deg = 0)',
  "Error: K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = 0 at rest, so θ<sub>ss</sub> = θ<sub>d</sub>; <b>error = 0</b>.",
  "Poles: yes they change. The gravity term is removed from the dynamics so the effective stiffness changes from K<sub>p</sub> + mgℓ cos θ to K<sub>p</sub>, which moves the poles (the system becomes faster).")
V('Q2', 'd', 'e2', 1.5, 'Weak justification', 'Correct conclusions (error 0; poles unchanged) but justification wrong: term depends on theta; real reason is cos 90 deg = 0',
  "New steady-state error = <b>0</b>, because the added term cancels the gravity torque exactly.",
  "The poles do not change, because the added term is a feed-forward term that does not depend on the error, so it cannot affect the stability of the loop.")
V('Q2', 'd', 'e3', 1.0, 'Conceptual', 'Claims a residual error of ~0.5 deg (should be exactly 0); poles unchanged with correct reason (cos 90 deg = 0)',
  "Gravity compensation reduces the steady-state error to about 0.5°, not exactly zero, since the compensation is evaluated at the measured angle and the sensor and model are not perfect.",
  "Poles: unchanged. The linearisation of the gravity term about θ<sub>d</sub> is mgℓ cos θ<sub>d</sub>, which is zero at 90°, so the stiffness stays K<sub>p</sub>.")

# ------------------------------------------------------------------ Q3 (a)
V('Q3', 'a', 'ok_T', 2, '', '',
  "(1) Differentiation is a high-pass operation (gain ∝ ω), so encoder measurement/quantisation noise is amplified, by about 1/T = 1000 at 1 kHz.",
  "(2) Encoder quantisation: Δθ is a whole number of counts, so ω̂ = Δθ/T moves in steps of (count size)/T; at low speed the estimate is a coarse staircase of zeros and spikes.")
V('Q3', 'a', 'ok_V', 2, '', '',
  "Reason 1 – noise amplification: the backward difference ω̂<sub>k</sub> = (θ<sub>k</sub> − θ<sub>k−1</sub>)/T has frequency response (1 − e<super>−jωT</super>)/T, whose magnitude grows with frequency (≈ ω for small ωT), i.e. it is a high-pass operation. Any noise on the encoder signal therefore appears in the velocity multiplied by roughly 1/T = 1000 s<super>-1</super>, and can swamp the true velocity.",
  "Reason 2 – quantisation: the encoder only reports integer counts, so Δθ is an integer multiple of the count size q. Dividing by T = 1 ms gives velocity steps of q/T; for a 4096-count encoder q = 2π/4096 = 1.53×10<super>-3</super> rad, so one step is 1.53 rad/s. At low speed the estimate flips between 0 and one step (a noisy staircase), exactly where the damping term of the PD law is needed.",
  "(A further, smaller issue is the half-sample delay of a backward difference, but the two reasons above are the main ones.)")
V('Q3', 'a', 'e1', 1.0, 'Conceptual', 'One valid reason (noise amplification); second reason (memory/processing cost) is wrong',
  "(1) Differentiation amplifies noise in the encoder signal.",
  "(2) Finite differencing needs a lot of memory and processing, which is slow on a micro-controller at 1 kHz.")
V('Q3', 'a', 'e2', 1.0, 'Incomplete', 'Only one distinct reason (noise amplification) stated twice in different words',
  "(1) Taking the difference of two readings amplifies noise.",
  "(2) The high frequency noise in the encoder signal gets magnified when we subtract successive readings and divide by a small T.")
V('Q3', 'a', 'e3', 0, 'Conceptual', 'Both reasons wrong (adds a pole / derivative of a sampled signal not defined)',
  "(1) Finite differencing introduces an extra pole which makes the plant unstable.",
  "(2) It cannot be implemented digitally because the derivative of a sampled signal is not defined.")

# ------------------------------------------------------------------ Q3 (b)
V('Q3', 'b', 'ok_T', 2, '', '',
  "H(s) = ω<sub>c</sub>/(s + ω<sub>c</sub>), ω<sub>c</sub> = 2π(20) = 125.66 rad/s. Tustin: s = (2/T)(z − 1)/(z + 1), T = 1 ms. With a = ω<sub>c</sub>T/2 = 0.06283: H(z) = a(1 + z<super>-1</super>) / [(1 + a) − (1 − a)z<super>-1</super>].",
  "y<sub>k</sub> = [a/(1+a)](u<sub>k</sub> + u<sub>k−1</sub>) + [(1−a)/(1+a)] y<sub>k−1</sub> = <b>0.05912 (u<sub>k</sub> + u<sub>k−1</sub>) + 0.88177 y<sub>k−1</sub></b>.",
  "DC gain: z = 1 gives H(1) = 2(0.05912)/(1 − 0.88177) = 0.11824/0.11823 = 1.000 ✓.")
V('Q3', 'b', 'ok_V', 2, '', '',
  "The analogue prototype is the first-order low-pass H(s) = ω<sub>c</sub>/(s + ω<sub>c</sub>) with ω<sub>c</sub> = 2πf<sub>c</sub> = 2π × 20 = 125.66 rad/s. The bilinear (Tustin) transform replaces s by (2/T)(z − 1)/(z + 1) with T = 1/f<sub>s</sub> = 0.001 s.",
  "Define a = ω<sub>c</sub>T/2 = 125.66 × 0.001/2 = 0.062832. Then H(z) = ω<sub>c</sub> / [(2/T)(z−1)/(z+1) + ω<sub>c</sub>] = a(z + 1) / [(1 + a) z − (1 − a)] = a(1 + z<super>-1</super>) / [(1 + a) − (1 − a) z<super>-1</super>].",
  "Dividing through by (1 + a): a/(1 + a) = 0.062832/1.062832 = 0.059117 and (1 − a)/(1 + a) = 0.937168/1.062832 = 0.881767. Hence with u = differenced signal and y = filtered velocity: <b>y<sub>k</sub> = 0.05912 (u<sub>k</sub> + u<sub>k−1</sub>) + 0.88177 y<sub>k−1</sub></b>. (Frequency pre-warping is neglected since f<sub>c</sub> ≪ f<sub>s</sub>/2.)",
  "Verification of the DC gain: set u and y constant (z = 1): y = 2(0.05912)u + 0.88177 y ⇒ y(1 − 0.88177) = 0.11824 u ⇒ y/u = 0.11824/0.11823 = 1.000. In general H(1) = 2a/[(1 + a) − (1 − a)] = 2a/2a = 1 exactly, so the steady-state output equals the commanded input ✓.")
V('Q3', 'b', 'e1', 1.0, 'Method', 'Used forward Euler instead of Tustin: coefficients 0.8743/0.1257 wrong for the bilinear transform; DC check done and valid-filter structure partly credited',
  "I discretise with forward Euler (s ≈ (z − 1)/T) to keep it simple. ω<sub>c</sub> = 2π × 20 = 125.66 rad/s.",
  "y<sub>k</sub> = (1 − ω<sub>c</sub>T) y<sub>k−1</sub> + ω<sub>c</sub>T u<sub>k−1</sub> = <b>0.8743 y<sub>k−1</sub> + 0.1257 u<sub>k−1</sub></b>.",
  "DC gain: 0.1257/(1 − 0.8743) = 0.1257/0.1257 = 1 ✓.")
V('Q3', 'b', 'e2', 1.5, 'Calculation', 'Forgot 2*pi: used w_c = 20 rad/s instead of 125.66 rad/s; Tustin method and DC check correct',
  "ω<sub>c</sub> = 20 rad/s. Tustin with T = 0.001: a = ω<sub>c</sub>T/2 = 0.01.",
  "y<sub>k</sub> = [a/(1 + a)](u<sub>k</sub> + u<sub>k−1</sub>) + [(1 − a)/(1 + a)] y<sub>k−1</sub> = <b>0.00990 (u<sub>k</sub> + u<sub>k−1</sub>) + 0.98020 y<sub>k−1</sub></b>.",
  "DC gain: 2(0.0099)/(1 − 0.9802) = 0.0198/0.0198 = 1 ✓.")
V('Q3', 'b', 'e3', 1.0, 'Calculation', 'Feedback coefficient mis-evaluated (0.8187 instead of 0.8818); DC gain only asserted and would not equal 1 with these coefficients',
  "ω<sub>c</sub> = 2π × 20 = 125.66 rad/s, a = ω<sub>c</sub>T/2 = 0.0628, Tustin transform.",
  "y<sub>k</sub> = <b>0.0591 (u<sub>k</sub> + u<sub>k−1</sub>) + 0.8187 y<sub>k−1</sub></b>.",
  "The DC gain is 1 since low-pass filters always have unity gain at DC.")
V('Q3', 'b', 'e4', 1.5, 'Incomplete', 'Coefficients correct but DC gain only asserted, not verified from the difference equation',
  "ω<sub>c</sub> = 2π × 20 = 125.66 rad/s; Tustin: s = (2/T)(z − 1)/(z + 1); a = ω<sub>c</sub>T/2 = 0.0628.",
  "y<sub>k</sub> = <b>0.0591 (u<sub>k</sub> + u<sub>k−1</sub>) + 0.8818 y<sub>k−1</sub></b>.",
  "DC gain is unity because it is a low-pass filter.")
V('Q3', 'b', 'bare', 0, 'Missing working', 'Final difference equation and DC gain stated without derivation (no credit under instruction 5)',
  "y[k] = 0.0591 (u[k] + u[k−1]) + 0.8818 y[k−1]. DC gain = 1.")

# ------------------------------------------------------------------ Q3 (c)
V('Q3', 'c', 'ok_T', 4, '', '',
  "A − LC = [−ℓ<sub>1</sub>, 1; −ℓ<sub>2</sub>, −2]. det(sI − A + LC) = (s + ℓ<sub>1</sub>)(s + 2) + ℓ<sub>2</sub> = s² + (2 + ℓ<sub>1</sub>)s + (2ℓ<sub>1</sub> + ℓ<sub>2</sub>).",
  "Desired: (s + 10)² = s² + 20s + 100. Match: 2 + ℓ<sub>1</sub> = 20 ⇒ ℓ<sub>1</sub> = 18; 2ℓ<sub>1</sub> + ℓ<sub>2</sub> = 100 ⇒ ℓ<sub>2</sub> = 64. <b>L = [18, 64]<super>T</super></b>.")
V('Q3', 'c', 'ok_V', 4, '', '',
  "First check observability: O = [C; CA] = [1, 0; 0, 1], full rank, so the observer poles can be placed arbitrarily.",
  "With L = [ℓ<sub>1</sub>, ℓ<sub>2</sub>]<super>T</super> and C = [1, 0], LC = [ℓ<sub>1</sub>, 0; ℓ<sub>2</sub>, 0], so A − LC = [−ℓ<sub>1</sub>, 1; −ℓ<sub>2</sub>, −2].",
  "Characteristic polynomial: det(sI − (A − LC)) = det[s + ℓ<sub>1</sub>, −1; ℓ<sub>2</sub>, s + 2] = (s + ℓ<sub>1</sub>)(s + 2) − (−1)(ℓ<sub>2</sub>) = s² + (2 + ℓ<sub>1</sub>) s + (2ℓ<sub>1</sub> + ℓ<sub>2</sub>).",
  "Both estimator poles at s = −10 means the desired polynomial is (s + 10)² = s² + 20 s + 100. Comparing coefficients: s¹: 2 + ℓ<sub>1</sub> = 20 ⇒ ℓ<sub>1</sub> = 18. s⁰: 2ℓ<sub>1</sub> + ℓ<sub>2</sub> = 100 ⇒ ℓ<sub>2</sub> = 100 − 36 = 64.",
  "<b>L = [18, 64]<super>T</super></b>. Verification: A − LC = [−18, 1; −64, −2] has trace −20 and determinant (−18)(−2) − (1)(−64) = 36 + 64 = 100, so the polynomial is s² + 20s + 100 = (s + 10)² ✓.")
V('Q3', 'c', 'e1', 2.0, 'Sign error', 'Sign error in determinant (-l2 instead of +l2): polynomial s^2+(2+l1)s+(2l1-l2) gives L=[18,-64]',
  "A − LC = [−ℓ<sub>1</sub>, 1; −ℓ<sub>2</sub>, −2]. det(sI − A + LC) = (s + ℓ<sub>1</sub>)(s + 2) − ℓ<sub>2</sub> = s² + (2 + ℓ<sub>1</sub>)s + (2ℓ<sub>1</sub> − ℓ<sub>2</sub>).",
  "Desired (s + 10)² = s² + 20s + 100. So 2 + ℓ<sub>1</sub> = 20 ⇒ ℓ<sub>1</sub> = 18 and 2ℓ<sub>1</sub> − ℓ<sub>2</sub> = 100 ⇒ ℓ<sub>2</sub> = 36 − 100 = −64.",
  "<b>L = [18, −64]<super>T</super></b>.")
V('Q3', 'c', 'e2', 2.5, 'Calculation', 'Expanded (s+10)^2 as s^2+10s+100 (should be 20s) giving L=[8,84]; characteristic polynomial derived correctly',
  "A − LC = [−ℓ<sub>1</sub>, 1; −ℓ<sub>2</sub>, −2], so det(sI − A + LC) = (s + ℓ<sub>1</sub>)(s + 2) + ℓ<sub>2</sub> = s² + (2 + ℓ<sub>1</sub>)s + (2ℓ<sub>1</sub> + ℓ<sub>2</sub>).",
  "Desired: (s + 10)(s + 10) = s² + 10s + 100. Matching: 2 + ℓ<sub>1</sub> = 10 ⇒ ℓ<sub>1</sub> = 8; 2(8) + ℓ<sub>2</sub> = 100 ⇒ ℓ<sub>2</sub> = 84.",
  "<b>L = [8, 84]<super>T</super></b>.")
V('Q3', 'c', 'e3', 1.0, 'Conceptual', 'Confused observer design with state feedback: used A-BK structure, L=[100,18] wrong; only the pole-matching idea is credited',
  "To place the poles I look at the characteristic polynomial of the closed loop. Treating the gain as in A − BK: A − BK = [0, 1; −k<sub>1</sub>, −2 − k<sub>2</sub>], so det = s² + (2 + k<sub>2</sub>)s + k<sub>1</sub>.",
  "Desired s² + 20s + 100: k<sub>2</sub> = 18 and k<sub>1</sub> = 100, so <b>L = [100, 18]<super>T</super></b>.")
V('Q3', 'c', 'e4', 3.0, 'Calculation', 'Arithmetic slip: l2 = 100 - 18 = 82 (forgot 2*l1 = 36) instead of 64; derivation and l1 correct',
  "A − LC = [−ℓ<sub>1</sub>, 1; −ℓ<sub>2</sub>, −2]; characteristic polynomial det(sI − A + LC) = (s + ℓ<sub>1</sub>)(s + 2) + ℓ<sub>2</sub> = s² + (2 + ℓ<sub>1</sub>)s + (2ℓ<sub>1</sub> + ℓ<sub>2</sub>).",
  "Desired (s + 10)² = s² + 20s + 100. Then 2 + ℓ<sub>1</sub> = 20 ⇒ ℓ<sub>1</sub> = 18, and 2ℓ<sub>1</sub> + ℓ<sub>2</sub> = 100 ⇒ ℓ<sub>2</sub> = 100 − 18 = 82.",
  "<b>L = [18, 82]<super>T</super></b>.")
V('Q3', 'c', 'bare', 0, 'Missing working', 'Final L stated without derivation of the characteristic polynomial (no credit under instruction 5)',
  "L = [18, 64]<super>T</super>.")

# ------------------------------------------------------------------ Q3 (d)
V('Q3', 'd', 'ok_T', 2, '', '',
  "Advantage of the observer: it uses the plant model and the applied input u, so its velocity estimate has (almost) no phase lag; the 20 Hz filter on differenced data always delays by about 1/(2π f<sub>c</sub>) ≈ 8 ms. It can also reconstruct states that cannot be obtained by differencing (e.g. disturbance, when augmented).",
  "Filter is safer when the model is uncertain or changes (unknown payload, friction, contact, actuator saturation): the observer then gives a biased or poorly-behaved estimate while the model-free filter still follows the measured data.")
V('Q3', 'd', 'ok_V', 2, '', '',
  "Advantage of the observer that no filter of this kind can give: the observer is driven by both the measurement y and the model with the actual input u, so it predicts the motion between samples. The velocity estimate therefore has little or no phase lag. The low-pass filter on differenced data, by contrast, always pays a lag of about 1/(2π f<sub>c</sub>) = 8 ms for its noise rejection, a trade-off it cannot escape. In addition the observer gives all states, and can be augmented with a disturbance state (e.g. unknown load torque) which no filter on θ can estimate.",
  "Circumstance where the filter is safer: when the plant model is poorly known or changes during operation, for example an unknown payload, varying friction, contact with the environment, or actuator saturation making u differ from the commanded value. The observer propagates the wrong model so its estimate can be biased (and in the worst case unstable with the feedback loop), whereas the model-free filter just smooths what the encoder actually measures.")
V('Q3', 'd', 'e1', 1.0, 'Conceptual', 'Observer advantage correct (uses model/input, no lag); circumstance wrong (claims filter safer at high sampling rate)',
  "Advantage of the observer: it uses the model and the input u, so there is no lag in the estimate, which a filter always introduces.",
  "The filter is safer when the sampling rate is very high, because the observer would not be able to run fast enough.")
V('Q3', 'd', 'e2', 1.0, 'Vague', 'Both answers vague (observer is more accurate; filter safer because cheap): half credit each at best',
  "The observer is more accurate than the filter.",
  "The filter is safer when you need something simple and cheap to implement.")
V('Q3', 'd', 'e3', 0, 'Conceptual', 'Both answers wrong (claims no observer advantage; filter safer when model perfectly known)',
  "An observer works only when there is no noise, so it has no advantage; a filter is always better because it is simpler.",
  "The filter is safer when the model is perfectly known.")

# ------------------------------------------------------------------ Q4 (a)
V('Q4', 'a', 'ok_T', 2, '', '',
  "θ̈ + aθ̇ + cθ = b(N<sub>ff</sub> r − k<sub>1</sub>θ − k<sub>2</sub>θ̇) ⇒ θ̈ + (a + bk<sub>2</sub>)θ̇ + (c + bk<sub>1</sub>)θ = bN<sub>ff</sub> r.",
  "With a = 2, b = 1, c = 6, k<sub>1</sub> = k<sub>2</sub> = 2: s² + 4s + 8 = 0 ⇒ s = −2 ± 2j (stable).",
  "DC gain = bN<sub>ff</sub>/(c + bk<sub>1</sub>) = N<sub>ff</sub>/8 = 1 ⇒ <b>N<sub>ff</sub> = 8</b>.")
V('Q4', 'a', 'ok_V', 2, '', '',
  "Substitute the control law into the plant: θ̈ + aθ̇ + cθ = b N<sub>ff</sub> r − b k<sub>1</sub> θ − b k<sub>2</sub> θ̇. Moving the feedback terms to the left: θ̈ + (a + b k<sub>2</sub>) θ̇ + (c + b k<sub>1</sub>) θ = b N<sub>ff</sub> r.",
  "Numerically, a + b k<sub>2</sub> = 2 + 2 = 4 and c + b k<sub>1</sub> = 6 + 2 = 8, so the characteristic equation is s² + 4s + 8 = 0. Roots: s = [−4 ± √(16 − 32)]/2 = −2 ± 2j. They have negative real parts, so the loop is stable; ω<sub>n</sub> = √8 = 2.83 rad/s and ζ = 4/(2 × 2.83) = 0.707.",
  "Transfer function from r to θ: T(s) = b N<sub>ff</sub> / (s² + 4s + 8). DC gain (s = 0): T(0) = N<sub>ff</sub>/8. For unity DC gain, <b>N<sub>ff</sub> = 8</b>. (Note that this is larger than 1 because the gravity-related stiffness c and the feedback k<sub>1</sub> both resist the displacement.)")
V('Q4', 'a', 'e1', 1.0, 'Calculation', 'Poles correct; N_ff inverted (0.125 instead of 8)',
  "Closed loop: θ̈ + (a + bk<sub>2</sub>)θ̇ + (c + bk<sub>1</sub>)θ = bN<sub>ff</sub> r, i.e. s² + 4s + 8 = 0 so the poles are s = −2 ± 2j.",
  "DC gain = bN<sub>ff</sub>/(c + bk<sub>1</sub>) = N<sub>ff</sub>/8. For unity gain N<sub>ff</sub> = 1/8 = <b>0.125</b>.")
V('Q4', 'a', 'e2', 0.5, 'Conceptual', 'Gravity stiffness c dropped from the characteristic equation (s^2+4s+2): poles -0.59,-3.41 and N_ff=2 wrong; structure of derivation right',
  "Substituting u: θ̈ + (a + bk<sub>2</sub>)θ̇ + bk<sub>1</sub>θ = bN<sub>ff</sub> r (the c term is the gravity load, handled separately).",
  "So s² + 4s + 2 = 0, giving s = −0.586 and s = −3.414. DC gain = bN<sub>ff</sub>/(bk<sub>1</sub>) = N<sub>ff</sub>/2 = 1 ⇒ <b>N<sub>ff</sub> = 2</b>.")
V('Q4', 'a', 'bare', 0, 'Missing working', 'Poles and N_ff stated without derivation (no credit under instruction 5)',
  "Poles: −2 ± 2j. N<sub>ff</sub> = 8.")

# ------------------------------------------------------------------ Q4 (b)
V('Q4', 'b', 'ok_T', 2, '', '',
  "With b = 0.75 (N<sub>ff</sub> = 8, k<sub>1</sub> = 2): G<sub>DC</sub> = bN<sub>ff</sub>/(c + bk<sub>1</sub>) = 0.75 × 8/(6 + 0.75 × 2) = 6/7.5 = 0.8.",
  "θ<sub>ss</sub> = <b>0.8</b>. Tracking error = (1 − 0.8)/1 × 100 = <b>20%</b>. (Less than the 25% actuator loss, because the stiffness also dropped.)")
V('Q4', 'b', 'ok_V', 2, '', '',
  "With the actual b = 0.75 and unchanged N<sub>ff</sub> = 8, k<sub>1</sub> = k<sub>2</sub> = 2, the closed loop becomes θ̈ + (a + bk<sub>2</sub>)θ̇ + (c + bk<sub>1</sub>)θ = bN<sub>ff</sub> r, i.e. θ̈ + 3.5θ̇ + 7.5θ = 6 r.",
  "For a unit step the steady state is found by setting derivatives to zero: 7.5 θ<sub>ss</sub> = 6 × 1, so θ<sub>ss</sub> = 6/7.5 = <b>0.8</b>.",
  "Tracking error = (r − θ<sub>ss</sub>)/r × 100% = (1 − 0.8) × 100 = <b>20%</b>. A common mistake would be to say the output falls by the same 25% as the actuator gain; that is wrong here, because b also appears in the feedback stiffness c + bk<sub>1</sub>, which decreases from 8 to 7.5 and partially compensates. The poles also change: s² + 3.5s + 7.5 → s = −1.75 ± 2.11j, still stable.")
V('Q4', 'b', 'e1', 0, 'Conceptual', 'Assumed error scales with b (0.75 / 25%) without recomputing DC gain; correct answer is 0.8 / 20%',
  "The actuator is 25% weaker, so the output is also 25% lower: θ<sub>ss</sub> = 0.75, and the tracking error = <b>25%</b>.")
V('Q4', 'b', 'e2', 1.0, 'Calculation', 'Correct DC-gain formula but denominator not updated for b=0.75 (used 8 not 7.5): result 0.75 / 25% instead of 0.8 / 20%',
  "G<sub>DC</sub> = bN<sub>ff</sub>/(c + bk<sub>1</sub>). Numerator: 0.75 × 8 = 6. Denominator: c + k<sub>1</sub> = 8 as before.",
  "θ<sub>ss</sub> = 6/8 = <b>0.75</b>, so error = <b>25%</b>.")
V('Q4', 'b', 'e3', 1.0, 'Calculation', 'theta_ss = 0.8 correct but % error computed as 80% (should be 20%)',
  "G<sub>DC</sub> = bN<sub>ff</sub>/(c + bk<sub>1</sub>) = 6/7.5 = 0.8, so θ<sub>ss</sub> = <b>0.8</b>.",
  "Percentage error = 0.8 × 100 = <b>80%</b>.")
V('Q4', 'b', 'bare', 0, 'Missing working', 'Answer stated without formula or substitution (no credit under instruction 5)',
  "θ<sub>ss</sub> = 0.8, error = 20%.")

# ------------------------------------------------------------------ Q4 (c)
V('Q4', 'c', 'ok_T', 4, '', '',
  "θ̈ + aθ̇ + cθ = b(−k<sub>1</sub>θ − k<sub>2</sub>θ̇ + K<sub>I</sub>ξ), ξ̇ = r − θ. Take r = 0 and differentiate once, using ξ̇ = −θ: d³θ/dt³ + (a + bk<sub>2</sub>)θ̈ + (c + bk<sub>1</sub>)θ̇ + bK<sub>I</sub>θ = 0.",
  "Char. poly: <b>s³ + (a + bk<sub>2</sub>)s² + (c + bk<sub>1</sub>)s + bK<sub>I</sub></b>.",
  "Desired: (s + 4)(s² + 4s + 8) = s³ + 8s² + 24s + 32.",
  "Match: 2 + k<sub>2</sub> = 8 ⇒ <b>k<sub>2</sub> = 6</b>; 6 + k<sub>1</sub> = 24 ⇒ <b>k<sub>1</sub> = 18</b>; K<sub>I</sub> = 32 (b = 1).")
V('Q4', 'c', 'ok_V', 4, '', '',
  "Take the state z = [θ, θ̇, ξ]<super>T</super>. The plant gives θ̈ = −aθ̇ − cθ + b u with u = −k<sub>1</sub>θ − k<sub>2</sub>θ̇ + K<sub>I</sub>ξ, and ξ̇ = r − θ. With r = 0 (r only shifts the equilibrium) the closed-loop matrix is A<sub>cl</sub> = [0, 1, 0; −(c + bk<sub>1</sub>), −(a + bk<sub>2</sub>), bK<sub>I</sub>; −1, 0, 0].",
  "Characteristic polynomial det(sI − A<sub>cl</sub>), expanding along the first row: s·[(s + a + bk<sub>2</sub>)s − 0] + 1·[(c + bk<sub>1</sub>)s + bK<sub>I</sub>] = s³ + (a + bk<sub>2</sub>)s² + (c + bk<sub>1</sub>)s + bK<sub>I</sub>. <b>(Result)</b>",
  "Desired poles −4 and −2 ± 2j: (s + 2 − 2j)(s + 2 + 2j) = (s + 2)² + 4 = s² + 4s + 8. Multiply by (s + 4): s³ + 4s² + 8s + 4s² + 16s + 32 = s³ + 8s² + 24s + 32.",
  "Compare coefficients with a = 2, b = 1, c = 6: s²: 2 + k<sub>2</sub> = 8 ⇒ <b>k<sub>2</sub> = 6</b>. s¹: 6 + k<sub>1</sub> = 24 ⇒ <b>k<sub>1</sub> = 18</b>. s⁰: b K<sub>I</sub> = 32 ⇒ <b>K<sub>I</sub> = 32</b>.",
  "Check: all coefficients of the desired polynomial are positive and (8)(24) = 192 > 32, so Routh–Hurwitz confirms the three poles are in the left half plane ✓.")
V('Q4', 'c', 'e1', 3.0, 'Sign error', 'Sign error in constant term (-b*K_I): gives K_I = -32 instead of +32; other coefficients right',
  "Substituting u and differentiating: the integral term enters with a minus sign, so the characteristic polynomial is s³ + (a + bk<sub>2</sub>)s² + (c + bk<sub>1</sub>)s − bK<sub>I</sub>.",
  "Desired: (s + 4)(s² + 4s + 8) = s³ + 8s² + 24s + 32.",
  "So 2 + k<sub>2</sub> = 8 ⇒ k<sub>2</sub> = 6; 6 + k<sub>1</sub> = 24 ⇒ k<sub>1</sub> = 18; −K<sub>I</sub> = 32 ⇒ <b>K<sub>I</sub> = −32</b>.")
V('Q4', 'c', 'e2', 1.0, 'Conceptual', 'Ignored the integrator state: used a 2nd-order polynomial, k1=k2=2, K_I=4; no third-order characteristic polynomial',
  "Closed-loop: θ̈ + (a + bk<sub>2</sub>)θ̇ + (c + bk<sub>1</sub>)θ = 0, so s² + (a + bk<sub>2</sub>)s + (c + bk<sub>1</sub>) = 0.",
  "Poles at −2 ± 2j give s² + 4s + 8, so k<sub>2</sub> = 2 and k<sub>1</sub> = 2. The extra pole at s = −4 comes from the integrator, so choose K<sub>I</sub> = 4.")
V('Q4', 'c', 'e3', 3.0, 'Calculation', 'Expansion slip: (s+4)(s^2+4s+8) taken as s^3+8s^2+16s+32 (should be 24s) giving k1=10 instead of 18',
  "Char. poly: s³ + (a + bk<sub>2</sub>)s² + (c + bk<sub>1</sub>)s + bK<sub>I</sub>.",
  "Desired: (s + 4)(s² + 4s + 8) = s³ + 4s² + 8s + 4s² + 16s + 32 = s³ + 8s² + 16s + 32 (combining terms).",
  "2 + k<sub>2</sub> = 8 ⇒ <b>k<sub>2</sub> = 6</b>; 6 + k<sub>1</sub> = 16 ⇒ <b>k<sub>1</sub> = 10</b>; K<sub>I</sub> = <b>32</b>.")
V('Q4', 'c', 'e4', 2.5, 'Conceptual', 'Swapped a and c in characteristic polynomial: k1=22, k2=2 wrong; K_I = 32 right',
  "Substituting the control law and differentiating once: s³ + (c + bk<sub>2</sub>)s² + (a + bk<sub>1</sub>)s + bK<sub>I</sub>.",
  "Desired: (s + 4)(s² + 4s + 8) = s³ + 8s² + 24s + 32.",
  "6 + k<sub>2</sub> = 8 ⇒ <b>k<sub>2</sub> = 2</b>; 2 + k<sub>1</sub> = 24 ⇒ <b>k<sub>1</sub> = 22</b>; K<sub>I</sub> = <b>32</b>.")
V('Q4', 'c', 'bare', 0, 'Missing working', 'Final gains stated without derivation (no credit under instruction 5)',
  "k<sub>1</sub> = 18, k<sub>2</sub> = 6, K<sub>I</sub> = 32.")

# ------------------------------------------------------------------ Q4 (d)
V('Q4', 'd', 'ok_T', 2, '', '',
  "For a constant r, in steady state all derivatives vanish: ξ̇ = r − θ<sub>ss</sub> = 0 ⇒ θ<sub>ss</sub> = r, independent of b and c; the closed loop only needs to be stable so that a steady state exists.",
  "Failure mode: integrator windup. When the actuator saturates the error persists, ξ keeps growing and causes a large overshoot afterwards. Remedy: anti-windup (clamp the integrator, conditional integration or back-calculation).")
V('Q4', 'd', 'ok_V', 2, '', '',
  "Suppose the closed loop is stable and r is constant. Then the state converges to a constant, so θ̇ = θ̈ = 0 and, crucially, ξ̇ = 0 as well (ξ itself is constant at its final value ξ<sub>ss</sub>). From the integrator equation ξ̇ = r − θ, we get r − θ<sub>ss</sub> = 0, i.e. <b>θ<sub>ss</sub> = r</b>.",
  "Neither b nor c appears in this argument. They only influence the value of ξ<sub>ss</sub> needed to hold the equilibrium (from the plant equation cθ<sub>ss</sub> = bu<sub>ss</sub> = b(−k<sub>1</sub>θ<sub>ss</sub> + K<sub>I</sub>ξ<sub>ss</sub>)), and the pole locations, so the zero error survives any error in the model parameters provided the loop stays stable (unlike the feed-forward N<sub>ff</sub> scheme of part (b)).",
  "Practical failure mode: integrator windup. If the actuator saturates (torque limit), the loop is effectively open, the error stays non-zero and ξ keeps integrating to a huge value. When the reference becomes reachable the stored integral forces a large overshoot and a long recovery. Standard remedy: anti-windup, such as clamping the integrator when the actuator is saturated, conditional integration, or back-calculation that feeds the difference between commanded and saturated torque back to the integrator.")
V('Q4', 'd', 'e1', 1.0, 'Conceptual', 'Zero-error argument correct; failure mode given (noise amplification) is not the standard one (windup)',
  "In steady state ξ̇ = 0, so r − θ<sub>ss</sub> = 0 ⇒ θ<sub>ss</sub> = r for any b and c as long as the system is stable.",
  "Failure mode: integral action amplifies noise and makes the system oscillate. Remedy: put a low-pass filter on the measurement.")
V('Q4', 'd', 'e2', 1.5, 'Weak justification', 'Hand-wavy zero-error argument (no equation: integrator accumulates until error is zero); windup + anti-windup clamp correct',
  "The integrator keeps accumulating the error until the error becomes zero, so the steady-state error is zero whatever b and c are, if the loop is stable.",
  "Failure mode: integrator windup when the actuator saturates. Remedy: anti-windup, e.g. clamp the integrator.")
V('Q4', 'd', 'e3', 1.5, 'Weak remedy', 'Zero-error derivation correct; windup named but remedy ("reduce K_I to zero") is not a standard anti-windup scheme',
  "Steady state: ξ̇ = 0, so r = θ<sub>ss</sub>; the parameters b and c do not enter, hence zero error for any b and c as long as it is stable.",
  "Failure mode: windup when the actuator saturates. Remedy: reduce K<sub>I</sub> to zero (or use a smaller gain) while saturated.")
V('Q4', 'd', 'e4', 1.0, 'Weak justification', 'Circular argument for zero error (stable so zero error); windup with clamping remedy correct',
  "Because the closed loop is stable, the steady-state error is zero for any b and c.",
  "Failure mode: integrator windup. Remedy: clamp the integrator output (anti-windup).")

# =================== EXTRA VARIANTS (batches 2-5) ===================
V('Q1', 'a', 'e3', 3.0, 'Incomplete', 'f_x and FOV correct but distance per pixel never given (-1.0)',
  "(i) f<sub>x</sub> = f/p = 16 mm / 5 µm = <b>3200 px</b>.",
  "(ii) Sensor width = 1280 × 5 µm = 6.4 mm; FOV = W<sub>s</sub>·Z/f = 6.4 × 400/16 = <b>160 mm</b>.")
V('Q1', 'b', 'e4', 2.0, 'Unit conversion', 'Read 10 mV/N as 10 V/N: LSB correct, method right, result 1.22e-4 N (off by 1000)',
  "LSB = 5 V/2<super>12</super> = 5/4096 = 1.2207 mV = 1.2207×10<super>-3</super> V.",
  "ΔF = LSB/S with S = 10 mV/N = 10 V/N (taking the mV as V in the denominator): ΔF = 1.2207×10<super>-3</super>/10 = <b>1.22×10<super>-4</super> N</b>.")
V('Q1', 'c', 'ok_2sf', 2.5, 'Unit/Precision', 'F and G reported to 2 s.f. (0.82, 0.09), violating the 3 s.f. instruction (-0.5)',
  "F = e<super>AT</super>, G = A<super>-1</super>(F − I)B for a ZOH input.",
  "F = e<super>−0.2</super> = <b>0.82</b>; G = (0.82 − 1)/(−2) = <b>0.09</b>. So x<sub>k+1</sub> = 0.82 x<sub>k</sub> + 0.09 u<sub>k</sub>.")
V('Q1', 'c', 'e4', 2.5, 'Notation', 'F and G computed correctly but swapped in the final model x[k+1] = G x[k] + F u[k]',
  "F = e<super>AT</super> = e<super>−0.2</super> = 0.8187. G = A<super>-1</super>(F − I)B = (0.8187 − 1)/(−2) = 0.0906.",
  "Hence the exact model is x<sub>k+1</sub> = <b>0.0906 x<sub>k</sub> + 0.8187 u<sub>k</sub></b>.")
V('Q2', 'a', 'e4', 1.5, 'Sign error', 'Sign error on the gravity term in the state equation (+mgl sin x1); equilibrium range |tau0|<=mgl still stated',
  "x<sub>1</sub> = θ, x<sub>2</sub> = §t. §x<sub>1</sub> = x<sub>2</sub>; §x<sub>2</sub> = (1/J)[τ − b x<sub>2</sub> + mgℓ sin x<sub>1</sub>].",
  "At equilibrium x<sub>2</sub> = 0 and mgℓ sin θ<sub>e</sub> = −τ<sub>0</sub>, so |τ<sub>0</sub>| ≤ mgℓ = 2.4525 N·m.")
V('Q2', 'b', 'ok_2sf', 1.5, 'Unit/Precision', 'A21 given as -61 (2 s.f.), violating the 3 s.f. instruction (-0.5)',
  "A = [0, 1; −(mgℓ/J) cos θ<sub>e</sub>, −b/J] = [0, 1; −122.6 × 0.5, −2.5] = <b>[0, 1; −61, −2.5]</b>.",
  "B = [0; 1/J] = <b>[0; 50]</b>.")
V('Q2', 'c', 'ok_2sf', 3.5, 'Unit/Precision', 'Final error quoted as 2.8 deg (2 s.f.), violating the 3 s.f. instruction (-0.5)',
  "At rest §t = §tt = 0, so K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) = mgℓ sin θ<sub>ss</sub>.",
  "At θ<sub>d</sub> the left side is 0 but the right side is 2.4525, a contradiction, so θ<sub>ss</sub> ≠ θ<sub>d</sub> (gravity needs a holding torque).",
  "Solving 50(π/2 − θ<sub>ss</sub>) = 2.4525 sin θ<sub>ss</sub> numerically: θ<sub>ss</sub> ≈ 87.2°, error ≈ <b>2.8°</b>.")
V('Q2', 'd', 'e4', 1.0, 'Incomplete', 'Error = 0 correct; nothing said about the closed-loop poles',
  "With the compensation term, at rest K<sub>p</sub>(θ<sub>d</sub> − θ<sub>ss</sub>) + mgℓ sin θ<sub>ss</sub> = mgℓ sin θ<sub>ss</sub>, so θ<sub>ss</sub> = θ<sub>d</sub> and the steady-state error is <b>0</b>.")
V('Q3', 'a', 'ok_alt', 2, 'Valid alternative', 'Gives noise amplification plus time delay/lag of the backward difference (a valid second reason); full marks expected',
  "(1) A finite difference acts like a high-pass filter, so measurement and quantisation noise in the encoder is greatly amplified (by 1/T).",
  "(2) A backward difference actually estimates the velocity at the mid-point of the interval, i.e. it lags the true velocity by T/2, and any jitter in the sample time shows up directly as velocity error.")
V('Q3', 'b', 'ok_3sf', 1.5, 'Unit/Precision', 'Coefficients rounded to 2 s.f. (0.059, 0.88), violating the 3 s.f. instruction; DC check only approximately 1 (-0.5)',
  "ω<sub>c</sub> = 2π(20) = 125.7 rad/s; Tustin with T = 1 ms, a = ω<sub>c</sub>T/2 = 0.063.",
  "y<sub>k</sub> = <b>0.059 (u<sub>k</sub> + u<sub>k−1</sub>) + 0.88 y<sub>k−1</sub></b>.",
  "DC gain: 2(0.059)/(1 − 0.88) = 0.118/0.12 ≈ 0.98 ≈ 1 ✓ (rounding).")
V('Q3', 'd', 'ok_alt', 2, 'Valid alternative', 'Different wording of correct points: no lag + unmeasured states/disturbances; filter safer under model mismatch or saturation; full marks expected',
  "Observer advantage: because it is a copy of the plant corrected by the encoder error, it gives a velocity estimate without the delay that a filter needs for noise rejection, and it can also estimate quantities no filter on θ can, such as an unknown load torque.",
  "A filter is the safer choice when the model is wrong or the true input is not known, e.g. unmodelled friction or backlash, a changing payload, or actuator saturation: the observer would then be driven by a wrong u and drift, while the filter only uses measured data.")
V('Q4', 'a', 'e3', 1.0, 'Calculation', 'Closed-loop polynomial correct but roots solved wrongly (-2 +/- 4j, forgot to divide by 2); N_ff = 8 right',
  "Closed loop: θ̈ + (a + bk<sub>2</sub>)θ̇ + (c + bk<sub>1</sub>)θ = bN<sub>ff</sub> r, i.e. s² + 4s + 8 = 0.",
  "s = [−4 ± √(16 − 32)]/2 = −4/2 ± √(−16) = <b>−2 ± 4j</b>.",
  "DC gain = N<sub>ff</sub>/8 = 1, so <b>N<sub>ff</sub> = 8</b>.")
V('Q4', 'b', 'e4', 1.5, 'Definition', 'theta_ss = 0.8 correct; error taken relative to the output ((1-0.8)/0.8 = 25%) instead of the reference (20%)',
  "With b = 0.75: G<sub>DC</sub> = 0.75 × 8/(6 + 0.75 × 2) = 6/7.5, so θ<sub>ss</sub> = <b>0.8</b>.",
  "Error = (1 − 0.8)/0.8 × 100 = <b>25%</b>.")
V('Q4', 'c', 'e5', 3.5, 'Symbolic slip', 'Symbolic characteristic polynomial written without the factor b (s^3+(a+k2)s^2+(c+k1)s+K_I); numbers unaffected since b = 1',
  "Substituting u into the plant and using ξ̇ = −θ (r = 0): characteristic polynomial s³ + (a + k<sub>2</sub>)s² + (c + k<sub>1</sub>)s + K<sub>I</sub>.",
  "Desired: (s + 4)(s² + 4s + 8) = s³ + 8s² + 24s + 32.",
  "2 + k<sub>2</sub> = 8 ⇒ <b>k<sub>2</sub> = 6</b>; 6 + k<sub>1</sub> = 24 ⇒ <b>k<sub>1</sub> = 18</b>; <b>K<sub>I</sub> = 32</b>.")
V('Q4', 'd', 'e5', 1.5, 'Incomplete', 'Zero-error argument correct; windup named with explanation but no remedy given',
  "In steady state ξ̇ = r − θ<sub>ss</sub> = 0, so θ<sub>ss</sub> = r whatever b and c are, provided the loop is stable.",
  "Failure mode: integrator windup — when the actuator saturates the integral keeps growing and causes a big overshoot later.")
