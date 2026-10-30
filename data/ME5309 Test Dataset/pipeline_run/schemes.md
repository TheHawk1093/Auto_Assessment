# Marking schemes: ME 5309 – Mid-Semester Examination (40 marks)

## Question 1a (4 marks, numeric)

Answer all three parts within this Ques 1. Each part is independent of the others.

(a) A machine-vision camera inspects parts moving on a conveyor. The sensor is 1280 pixels wide with square pixels of 5µm, the lens has a focal length of 16 mm, and the camera looks down on the belt from a standoff of 400 mm.
(i) Determine the focal length f_x in pixels.
(ii) Determine the width of the field of view on the belt, and hence the distance on the belt that corresponds to one pixel.

```
Marking stance: standard. Full marks need fx = 3200 px, FOV = 160 mm and 0.125 mm per pixel; either route (similar triangles or Z/fx) is fine. If fx is wrong but later steps are consistent with the student's own value and method, award the later method steps, but the final value only if it is 0.125 mm. Missing units on the final answer lose a small share.
P1 (2 marks): Focal length in pixels: fx = f / pixel width = 16 mm / 0.005 mm = 3200 pixels. Full marks for the correct value with the method shown (formula or substitution).
    level 0.5 of the marks: Correct formula fx = f/pixel size with substitution, but arithmetic or unit-conversion error in the result (e.g. 3.2 or 32000).
P2 (1 marks): Field of view width on the belt = 160 mm, by sensor width 6.4 mm × 400/16, or by 1280 × Z/fx. Either direction of working is acceptable (standoff and Z are the same).
P3 (1 marks): Distance on the belt per pixel = 0.125 mm (160/1280, or Z/fx = 400/3200). Final answer. Final answer 0.125 mm (checked by code; do not re-judge it).
```

Answer key worked out: (i) fx = f / pixel size = 16 mm / 0.005 mm = 3200 pixels (fy = 3200 too).
(ii) Sensor width = 1280 × 5 µm = 6.4 mm. FOV = 6.4 × 400/16 = 160 mm. Per pixel = 160/1280 = 0.125 mm (equivalently Z/fx = 400/3200 = 0.125 mm). Final: 0.125 mm per pixel on the belt (FOV 160 mm, fx 3200 px).

## Question 1b (3 marks, numeric)

Answer all three parts within this Ques 1. Each part is independent of the others.

(b) A force sensor of sensitivity 10 mV/N is read by a 12-bit ADC whose input range is 0 V to 5 V. Determine the smallest change in force that the system can resolve.

```
Marking stance: standard. Full marks need the LSB from a written V_FS/2^N (2 marks) and division by the sensitivity to give about 0.122 N (1 mark). Using 4095 instead of 4096 is accepted in full. Multiplying by the sensitivity loses the last mark. A bare 1.22 mV with no formula earns no LSB marks. A wrong voltage range earns the LSB marks only if the arithmetic matches that range, and the marker should flag it.
P1 (2 marks): Resolution (LSB) found from a written formula LSB = V_FS / 2^N with substitution 5 V / 2^12 (or 4095), giving about 1.22 mV (1.2207 mV; 1.2210 mV from 4095 also accepted). Must show the formula/substitution; a bare 1.22 mV with no formula earns 0. If a different range (e.g. 10 V or ±5 V) is used, award this mark only if the arithmetic matches the stated range, and flag it.
    level 0.5 of the marks: Formula or substitution written correctly (V_FS / 2^N with N = 12) but arithmetic result for LSB is wrong or missing.
P2 (1 marks): Divides the LSB voltage by the sensitivity (1.22 mV / 10 mV/N) to get the smallest resolvable force change. Multiplying by the sensitivity earns 0 here. The division must be shown. Final answer about 0.122 N (0.1221 N); give the unit in N. Final answer 0.1221 N (checked by code; do not re-judge it).
```

Answer key worked out: LSB = V_FS / 2^N = 5 V / 4096 = 1.2207 mV. Smallest resolvable force change = LSB / sensitivity = 1.2207 mV / (10 mV/N) = 0.1221 N.

## Question 1c (3 marks, maths)

Answer all three parts within this Ques 1. Each part is independent of the others.

(c) The first-order plant ẋ = −2x + u is to be implemented in a digital controller. Using a zero-order hold on the input and a sampling period T = 0.1 s, obtain the exact discrete-time model x_{k+1} = F x_k + G u_k and give F and G numerically. State the formulae you use for F and G before substituting.

```
Marking stance: standard. Full marks: both formulae stated, F ≈ 0.8187 and G ≈ 0.0906. Only F given: 2 marks. Forward Euler (F=0.8, G=0.1) or Tustin, if clearly labelled, earns 1 mark maximum in total. Sign error giving G = −0.0906 keeps formula and F marks (2 total). Correct method with F and G left unevaluated: 1.5 maximum, but if it amounts to Euler, 1 maximum.
P1 (1 marks): States the ZOH discretisation formulae before substituting: F = e^{AT} and G = (∫₀ᵀ e^{Aτ} dτ)·B (or equivalent G = A^{-1}(F − I)B). Both F and G formulae must be given. Stating Euler or Tustin formulae does not earn this mark.
    level 0.5 of the marks: Only one of the two formulae (F or G) is stated correctly.
P2 (1 marks): Correct F = e^{-0.2} = 0.8187 (accept 0.819, 0.81873). Euler value 0.8 is wrong. Final answer 0.8187  (checked by code; do not re-judge it).
    level 0.5 of the marks: Correct exponent e^{-0.2} written but not evaluated numerically.
P3 (1 marks): Correct G = (1 − e^{-0.2})/2 = 0.0906 (accept 0.09063). Sign-inverted (−0.0906) or Euler value 0.1 is wrong. Final answer 0.0906  (checked by code; do not re-judge it).
```

Answer key worked out: Formulae: F = e^{AT}, G = ∫₀ᵀ e^{Aτ}dτ·B = A^{-1}(F − I)B. With A=−2, B=1, T=0.1: F = e^{−0.2} = 0.8187; G = (1 − e^{−0.2})/2 = 0.18127/2 = 0.0906. So x_{k+1} = 0.8187 x_k + 0.0906 u_k.

## Question 2a (2 marks, maths)

A single revolute joint moving in the vertical plane is described by J θ̈ + b θ̇ + mgℓ sinθ = τ, where θ is measured from the downward vertical and J = 0.02 kg·m², b = 0.05 N·m·s/rad, m = 1 kg, ℓ = 0.25 m.

(a) Choose a state vector and write the nonlinear state-space model ẋ = f(x,τ). For a constant applied torque τ0, write the equation that determines the equilibria and state the range of τ0 for which an equilibrium exists.

```
Marking stance: standard. Full marks: correct two-equation state model, and equilibrium equation with the evaluated range |τ0| ≤ 2.4525 N·m. Half of the second mark for the symbolic range, or for the one-sided range with no mention of symmetry. Equilibrium equation without any range earns 0 for the second point. Claiming a unique equilibrium is not penalised in the marks, but note it.
P1 (1 marks): Chooses state x1 = θ, x2 = θ̇ (equivalent choice acceptable) and writes both state equations: ẋ1 = x2 and ẋ2 = (1/J)(τ − b x2 − mgℓ sin x1). Both equations must be correct for full marks.
    level 0.5 of the marks: State vector chosen and one of the two equations correct, or both equations present with a minor algebra/sign slip.
P2 (1 marks): Equilibrium condition: x2 = 0 and mgℓ sin θe = τ0, together with the existence range |τ0| ≤ mgℓ = 2.4525 N·m (g = 9.81), because |sin θe| ≤ 1. A range with no equilibrium equation, or an equilibrium equation with no range, earns no credit for the range.
    level 0.5 of the marks: Correct equilibrium equation and range given symbolically as |τ0| ≤ mgℓ without evaluating the number.
    level 0.5 of the marks: Correct equilibrium equation and numerical range written as τ0 ≤ 2.4525 N·m without the modulus, with symmetry (negative torque) not mentioned anywhere.
```

Answer key worked out: x1 = θ, x2 = θ̇. ẋ1 = x2; ẋ2 = (1/J)(τ − b x2 − mgℓ sin x1). With τ = τ0 and ẋ = 0: x2 = 0 and mgℓ sin θe = τ0, with mgℓ = 1×9.81×0.25 = 2.4525 N·m. Since |sin θe| ≤ 1, an equilibrium exists only when |τ0| ≤ 2.4525 N·m (two equilibria in each period for |τ0| < 2.4525).

## Question 2b (2 marks, maths)

A single revolute joint moving in the vertical plane is described by J θ̈ + b θ̇ + mgℓ sinθ = τ, where θ is measured from the downward vertical and J = 0.02 kg·m², b = 0.05 N·m·s/rad, m = 1 kg, ℓ = 0.25 m.

(b) Linearise the model about the equilibrium at θe = 60° and give the matrices A and B numerically.

```
Marking stance: standard. P1 is for the correct symbolic A and B (cos θe, correct signs). P2 is for the numerical entries −61.3, −2.5, 50. Using sin θe or measuring from the horizontal (A21 = −106.2) loses P1; the numerical mark may be given only if the numbers follow from the student's own expression and B is correct. Maximum 1 for any single common error.
P1 (1 marks): Correct symbolic linearised state-space form with states x=[δθ, δθ̇]: A = [[0,1],[−mgℓ cosθe/J, −b/J]] and B = [[0],[1/J]]. Must use cos θe (derivative of sin θ) with the correct negative sign on A21 and −b/J in A22. Using sin θe, a sign error on A21, or other wrong symbolic form earns no marks.
P2 (1 marks): Correct numerical entries: A = [[0,1],[−61.3,−2.5]] (A21 ≈ −61.3 from 1×9.81×0.25×0.5/0.02), and B = [[0],[50]]. Accept g=9.81 (−61.3) or small rounding differences. Award if numbers are consistent with the student's own symbolic expression only where the error is not in B (e.g. an own-expression A21 with correct −2.5 and 50); B=[0,1]^T (forgot 1/J) loses this mark.
```

Answer key worked out: Let x1 = δθ, x2 = δθ̇, u = δτ. θ̈ = (τ − bθ̇ − mgℓ sinθ)/J. Linearising: sinθ ≈ sinθe + cosθe δθ, so δθ̈ = −(mgℓ cosθe/J) δθ − (b/J) δθ̇ + δτ/J.
mgℓ = 1×9.81×0.25 = 2.4525; ×cos60° = 1.22625; /0.02 = 61.31. b/J = 2.5. 1/J = 50.
A = [[0, 1], [−61.3, −2.5]], B = [[0], [50]].

## Question 2c (4 marks, maths)

A single revolute joint moving in the vertical plane is described by J θ̈ + b θ̇ + mgℓ sinθ = τ, where θ is measured from the downward vertical and J = 0.02 kg·m², b = 0.05 N·m·s/rad, m = 1 kg, ℓ = 0.25 m.

(c) The joint is now controlled by pure PD feedback, τ = Kp(θd − θ) − Kd θ̇, Kp = 50 N·m/rad, with a constant commanded (desired) angle θd = 90°. Show that the joint does not come to rest at θd. Write the equation satisfied by the steady-state angle θss, and hence estimate the steady-state error in degrees.

```
Marking stance: standard. Full marks: impossibility argument, correct steady-state equation, and error ≈ 2.81° (2.7°–2.9°). Qualitative 'no integral action' alone gets 1 mark. Small-angle sinθ≈θ loses the final 2 marks; radians without conversion or only θss stated gives half of the final 2 marks.
P1 (1 marks): Shows that θss = θd is impossible: by substitution (at θd = 90° the PD torque Kp(θd−θss) would be zero while gravity torque mgℓ sin90° = 2.4525 N·m ≠ 0) or by a torque-balance argument (proportional term must supply the holding torque, so a non-zero error is needed). A bare statement 'no integral action' with no argument earns this mark only.
P2 (1 marks): Correct steady-state equation obtained by setting θ̈ = θ̇ = 0: Kp(θd − θss) = mgℓ sin θss (Kd term vanishes). Equivalent forms accepted.
P3 (2 marks): Correct steady-state error value: 0.049 rad or 2.81°. Accept any value in 2.7°–2.9° or 0.047–0.050 rad by any route (linearisation with cos90°=0 giving e ≈ mgℓ/Kp = 2.4525/50, numerical iteration, or graphical solution). Accept θss ≈ 87.2° if the error is evident. Answer in radians only with no conversion to degrees loses the unit share (1 of these 2 marks). Using sin θss ≈ θss (small angle about zero) loses these marks.
    level 0.5 of the marks: Correct method/approximation leading to the right expression or value but the answer is left in radians with no degree conversion, or only θss = 87.2° is given without stating the error, or a value outside the band arising from a mixed operating point (e.g. cos 60° used, 2.70°).
```

Answer key worked out: Steady state (θ̈=θ̇=0): Kp(θd−θss) = mgℓ sinθss. mgℓ = 1×9.81×0.25 = 2.4525 N·m. If θss=θd=90°, LHS=0 but RHS=2.4525, contradiction, so an error exists. With e=θd−θss, linearise about 90° (cos90°=0): Kp e ≈ mgℓ → e ≈ 2.4525/50 = 0.04905 rad ≈ 2.81°. Numerical solution gives θss ≈ 87.19°, e ≈ 2.81°. Final answer: steady-state error ≈ 2.8° (0.049 rad), θss ≈ 87.2°.

## Question 2d (2 marks, short)

A single revolute joint moving in the vertical plane is described by J θ̈ + b θ̇ + mgℓ sinθ = τ, where θ is measured from the downward vertical and J = 0.02 kg·m², b = 0.05 N·m·s/rad, m = 1 kg, ℓ = 0.25 m.

(d) A gravity-compensation term is now added, so that τ = Kp(θd − θ) − Kd θ̇ + mgℓ sinθ. State the new steady-state error, and state with justification whether this additional term changes the closed-loop poles of the linearisation about θd.

```
Marking stance: standard. Full marks: zero steady-state error with cancellation, plus a pole statement that names the mgℓ cosθ stiffness term (general answer, 90° answer, or both). Part marks only for zero error without justification. No marks for bare yes/no on poles. Note on the script candidates giving both answers.
P1 (1 marks): States the new steady-state error is zero (θss = θd), with the gravity cancellation shown or clearly asserted (the +mgℓ sinθ term cancels the gravity term, leaving Jθ̈ + (b+Kd)θ̇ + Kp(θ−θd) = 0).
    level 0.5 of the marks: States zero error but gives no cancellation or reason.
P2 (1 marks): Correct, justified statement about the poles. Accept any of: (a) the poles change in general because the gravity stiffness term mgℓ cosθ is removed from the characteristic equation (s² + ((b+Kd)/J)s + Kp/J instead of (Kp + mgℓ cosθss)/J); (b) at θd = 90° the gravity stiffness mgℓ cosθ is ~zero/negligible, so the poles are essentially unchanged at this operating point, though they would change elsewhere; (c) both together (best answer, no extra marks; note on script). Do not award an unjustified yes/no, or 'poles change because the plant is now linear' without identifying which coefficient (the mgℓ cosθ stiffness term) changes.
```

## Question 3a (2 marks, short)

A joint is instrumented with a position encoder only, and its model is A = [0 1; 0 −2], B = [0; 1], C = [1 0], with the state x = [θ θ̇]^T. The control loop runs at fs = 1 kHz. A velocity signal is required for a PD control law.

(a) State the two distinct reasons why forming velocity by raw finite differencing of successive encoder readings gives a poor estimate.

```
Marking stance: standard. Full marks need two distinct mechanisms, each explained: quantisation divided by small T, and high-frequency noise amplification by differentiation. A mechanism only named without explanation earns half. Vague 'noise' stated twice in different words counts as one mechanism; ignore any discussion of changing fs.
P1 (1 marks): First valid mechanism, correctly explained: quantisation amplification. The encoder position is quantised to discrete counts; differencing (θk − θk−1)/T divides a one-count error (Δθ) by the small sample period T, so a one-count jitter gives a large spurious velocity (e.g. 0.01° count at 1 kHz → 10°/s). Must explain why differencing causes it, not just name it.
    level 0.5 of the marks: Names quantisation / finite encoder resolution as a cause but gives no explanation of why differencing amplifies it (no division by small T, no one-count jitter effect).
P2 (1 marks): Second, genuinely distinct mechanism, correctly explained: noise amplification by differentiation. Differentiation has gain rising with frequency, so broadband sensor/electrical noise on the position signal is amplified at high frequencies where there is no useful signal. Must explain why differencing causes it. Generic 'it is noisy' or 'noise is amplified' that merely restates quantisation noise does not count as distinct.
    level 0.5 of the marks: Names sensor/measurement noise (or high-frequency noise) as a problem but gives no explanation of why differencing amplifies it (no mention of rising gain with frequency or high-pass behaviour).
```

## Question 3b (2 marks, maths)

A joint is instrumented with a position encoder only, and its model is A = [0 1; 0 −2], B = [0; 1], C = [1 0], with the state x = [θ θ̇]^T. The control loop runs at fs = 1 kHz. A velocity signal is required for a PD control law.

(b) A first-order low-pass filter with cut-off frequency fc = 20 Hz is to be applied to the differenced signal. Discretise the filter using the bilinear (Tustin) transform at fs = 1 kHz and write the resulting difference equation with numerical coefficients. Verify that its DC gain (steady state ratio between desired command and actual output) is unity.

```
Marking stance: standard. Full marks for the correct difference equation with coefficients 0.0591 (both input terms) and 0.882 (feedback term), and for showing the z=1 evaluation giving a gain of exactly 1. Give half of P1 for a correct method with a numerical slip. A bare statement that the DC gain is 1 without evaluation earns nothing for P2.
P1 (1 marks): Correct Tustin-discretised difference equation with numerical coefficients to 3 s.f.: y_k = 0.0591(u_k + u_{k-1}) + 0.882 y_{k-1} (b0 = b1 = κ/(1+κ) ≈ 0.0591, with κ = ωcT/2 = 0.0628, and a1 = (κ−1)/(1+κ) ≈ −0.882, i.e. +0.882 y_{k-1} on the right-hand side). Equivalent forms accepted (e.g. y_k − 0.882 y_{k-1} = 0.0591 u_k + 0.0591 u_{k-1}). Sign error on the y_{k-1} term or wrong coefficients earns no credit.
    level 0.5 of the marks: Correct method (Tustin substitution with ωc = 125.66 rad/s, T = 1 ms) and correct general form of H(z), but numerical coefficients wrong or not given to 3 s.f.
P2 (1 marks): DC gain verified by evaluating H(z) at z = 1 (or by setting y_k = y_{k-1}, u_k = u_{k-1} in the difference equation): (b0+b1)/(1+a1) = 0.1182/0.1182 = 1, so the gain is unity. Must show the evaluation, not just assert it. Follow-through is allowed using the student's own coefficients if they are consistent.
```

Answer key worked out: H(s)=1/(1+s/ωc), ωc=2π·20=125.66 rad/s, T=1 ms. Tustin: s=(2/T)(1−z⁻¹)/(1+z⁻¹). κ=ωcT/2=0.062832. H(z)=κ(1+z⁻¹)/((1+κ)+(κ−1)z⁻¹). b0=b1=κ/(1+κ)=0.0591; a1=(κ−1)/(1+κ)=−0.8818. Difference equation: y_k = 0.0591(u_k+u_{k-1}) + 0.882 y_{k-1}. DC gain at z=1: (0.1182)/(1−0.8818)=0.1182/0.1182=1. Gain is unity.

## Question 3c (4 marks, maths)

A joint is instrumented with a position encoder only, and its model is A = [0 1; 0 −2], B = [0; 1], C = [1 0], with the state x = [θ θ̇]^T. The control loop runs at fs = 1 kHz. A velocity signal is required for a PD control law.

(c) Instead of filtering, a Luenberger (full state observer covered in class) observer ˙x̂ = A x̂ + Bu + L(y − C x̂) is to be used. Derive the characteristic polynomial of A − LC in terms of L = [ℓ1 ℓ2]^T, and hence determine L so that both estimator poles lie at s = −10.

```
Marking stance: standard. Full marks need the correct A − LC, the characteristic polynomial, the desired polynomial s²+20s+100 and L = [18; 64]. Give part marks for correct steps before any error. Do not penalise the same error twice, and accept an equivalent correct method.
P1 (1 marks): Forms A − LC correctly, with LC as the outer product of L = [ℓ1; ℓ2] and C = [1 0], so ℓ1, ℓ2 sit in the first column only: A − LC = [[−ℓ1, 1], [−ℓ2, −2]].
P2 (1 marks): Correct characteristic polynomial det(sI − (A − LC)) = s² + (ℓ1 + 2)s + (2ℓ1 + ℓ2). Equivalent expanded forms accepted.
P3 (1 marks): Correct desired polynomial for a double pole at −10: (s+10)² = s² + 20s + 100.
P4 (1 marks): Matches coefficients to get ℓ1 = 18 and ℓ2 = 64, i.e. L = [18; 64]. Both values must be correct. Follow-through on the student's own polynomial from P2 may earn this mark only if the matching is done correctly.
    level 0.5 of the marks: Only one of ℓ1 = 18 or ℓ2 = 64 is correct, or the matching method is right but there is an arithmetic slip.
```

Answer key worked out: A − LC = [[−ℓ1, 1], [−ℓ2, −2]]. det(sI − (A − LC)) = (s+ℓ1)(s+2) + ℓ2 = s² + (ℓ1+2)s + (2ℓ1+ℓ2). Desired: (s+10)² = s² + 20s + 100. So ℓ1 + 2 = 20 gives ℓ1 = 18, and 2ℓ1 + ℓ2 = 100 gives ℓ2 = 64. L = [18; 64].

## Question 3d (2 marks, short)

A joint is instrumented with a position encoder only, and its model is A = [0 1; 0 −2], B = [0; 1], C = [1 0], with the state x = [θ θ̇]^T. The control loop runs at fs = 1 kHz. A velocity signal is required for a PD control law.

(d) Both the filter of part (b) and the observer of part (c) produce a velocity estimate. State one advantage the observer has that no filter of this kind can provide, and state one circumstance in which the filter would be the safer choice.

```
Marking stance: standard. Full marks need one valid observer advantage with reasoning (1) and one filter-favouring circumstance tied to model error or parameter uncertainty (1). Part marks are given where the idea is named but the reasoning or the link to model error is missing. Generic statements such as 'observer is more accurate' or 'filter is easier' earn nothing.
P1 (1 marks): States one valid advantage of the observer that a filter cannot provide, with correct reasoning. Acceptable: it uses the known input u and plant model so it predicts rather than differentiates, tracking changing velocity without the lag/smoothing trade-off of a low-pass filter; OR it estimates an unmeasured state rather than just smoothing a differentiated measurement; OR quantisation enters through a bounded, filtered path rather than being divided by T. A bare claim (e.g. 'observer is better/more accurate') with no reasoning does not earn full marks.
    level 0.5 of the marks: Names a valid advantage (e.g. uses the model/input u) but gives no or incorrect reasoning for why a filter cannot do it.
P2 (1 marks): States one circumstance where the filter is safer, specifically invoking model error or parameter uncertainty: the filter is model-free, so when A, B or actuator gain are wrong/drifting (temperature, load, wear), or the plant is strongly nonlinear away from the linearisation point, the observer's estimate becomes biased or misleading/divergent while the filter only depends on its own bandwidth choice. A circumstance not tied to model error or uncertainty (e.g. 'filter is simpler', 'cheaper to compute') does not earn the mark.
    level 0.5 of the marks: Says the filter is safer because it is model-free or simpler, but does not link this to an inaccurate or uncertain model/parameters as the circumstance.
```

## Question 4a (2 marks, maths)

A linearised, gravity-loaded joint, with the input gains lumped into a single constant b, is described by θ̈ + aθ̇ + cθ = bu, a = 2, c = 6, b = 1, where c arises from the gravity load. The nominal controller is state feedback with reference feedforward, u = N_ff r − k1θ − k2θ̇.

(a) With k1 = k2 = 2, find the closed-loop poles and determine the value of N_ff for which the DC gain from r to θ is exactly unity.

```
Marking stance: standard. Full marks for poles −2 ± 2j and N_ff = 8 justified by a DC-gain condition. Part marks as per levels for correct intermediate equation or DC-gain expression with a later error. No marks for the wrong closed-loop equation, e.g. ignoring the gravity term c.
P1 (1 marks): Closed-loop poles: substitutes the control law to get s² + 4s + 8 = 0 (i.e. θ̈ + (a+bk2)θ̇ + (c+bk1)θ = bN_ff r) and finds poles s = −2 ± 2j. Equivalent forms (−2 ± j2) accepted.
    level 0.5 of the marks: Correct closed-loop characteristic equation s²+4s+8=0 but poles wrong or not found.
P2 (1 marks): N_ff = 8, obtained from a stated DC-gain condition (e.g. set derivatives to zero or final value: θss/r = bN_ff/(c+bk1) = N_ff/8 = 1). A bare value 8 with no DC-gain condition shown does not earn full marks. Final answer 8  (checked by code; do not re-judge it).
    level 0.5 of the marks: Correct DC-gain expression N_ff/8 (or b N_ff/(c+bk1)) stated but final N_ff wrong, or N_ff = 8 given without showing the DC-gain condition.
```

Answer key worked out: Closed loop: θ̈ + (a+bk2)θ̇ + (c+bk1)θ = bN_ff r → θ̈ + 4θ̇ + 8θ = N_ff r. Characteristic: s²+4s+8=0 → s = −2 ± 2j. DC gain (derivatives zero): θss = N_ff r/8, so unity gain requires N_ff = 8.

## Question 4b (2 marks, numeric)

A linearised, gravity-loaded joint, with the input gains lumped into a single constant b, is described by θ̈ + aθ̇ + cθ = bu, a = 2, c = 6, b = 1, where c arises from the gravity load. The nominal controller is state feedback with reference feedforward, u = N_ff r − k1θ − k2θ̇.

(b) The actual actuator gain turns out to be 25% lower than assumed, that is b = 0.75, while N_ff, k1 and k2 are left at the values found in part (a). Compute the steady-state value of θ for a unit step reference r = 1 and the resulting percentage tracking error.

```
Marking stance: standard. Full marks: θss = 0.800 with error 20% below reference, plus an explanation that Nff lies outside the feedback path so the gain error is uncorrected. Part marks on P1 if only one of the number or percentage is correct. An explanation that does not mention feedforward being outside the loop earns nothing on P2.
P1 (1 marks): Final answer: steady-state θss = 0.800 (rad, i.e. b·Nff/(c+b·k1) = 0.75×8/(6+0.75×2) = 6/7.5) AND the tracking error stated as 20% (θ is 20% below the reference, i.e. −20%). Uses Nff = 8, k1 = 2 from part (a). Sign convention may be either as long as it is clear that the output falls short by 20%. Final answer 0.8  (checked by code; do not re-judge it).
    level 0.5 of the marks: Correct θss = 0.8 but percentage error missing or wrong, or correct 20% error stated without θss value.
P2 (1 marks): Explanation: Nff is a feedforward gain on the reference path, outside the feedback loop, so feedback (k1θ, k2θ̇) cannot correct the DC calibration error. No integrator or error-driven correction exists, so the steady-state gain inherits the actuator gain error. Merely saying 'gain changed' without reference to feedforward being outside the feedback path earns no credit.
```

Answer key worked out: At steady state θ̇=θ̈=0: cθ = b(Nff r − k1θ) ⇒ θss = b Nff r/(c + b k1). From part (a) with b=1 and θss=r: Nff = c + k1 = 8, k1 = 2. With b=0.75: θss = 0.75×8/(6+1.5) = 6/7.5 = 0.800. Error = (0.8−1)/1 = −20%. Cause: Nff is feedforward outside the feedback loop, so feedback cannot correct it; no integrator. Final answer: θss = 0.800 (error −20%).

## Question 4c (4 marks, maths)

A linearised, gravity-loaded joint, with the input gains lumped into a single constant b, is described by θ̈ + aθ̇ + cθ = bu, a = 2, c = 6, b = 1, where c arises from the gravity load. The nominal controller is state feedback with reference feedforward, u = N_ff r − k1θ − k2θ̇.

(c) The plant is now augmented with the integral of the tracking error, ξ̇ = r − θ, u = −k1θ − k2θ̇ + K_I ξ. Derive the closed-loop characteristic polynomial symbolically in terms of a, b, c, k1, k2 and K_I. Hence place the closed-loop poles at s = −4 and s = −2 ± 2j, and determine k1, k2 and K_I.

```
Marking stance: standard. Full marks need the correct augmented model, the symbolic polynomial, the desired polynomial, and all three gains (k1=18, k2=6, K_I=32). A different but consistent sign convention for ξ and K_I is accepted in full. Earlier errors lose only the later dependent steps; a wrong gain from a correct method still keeps the method points.
P1 (1 marks): Forms the augmented third-order model with the integral state ξ included (state [θ, θ̇, ξ]), substituting the control law into the plant to get θ̈ = −(c+bk1)θ − (a+bk2)θ̇ + bK_I ξ and ξ̇ = r − θ (equivalently the A_cl matrix [[0,1,0],[−(c+bk1),−(a+bk2),bK_I],[−1,0,0]]). Either sign convention (ξ̇ = θ − r with −K_Iξ) is acceptable if used consistently.
P2 (1 marks): Correct symbolic closed-loop characteristic polynomial s³ + (a+bk2)s² + (c+bk1)s + bK_I.
P3 (1 marks): Correct desired polynomial from poles −4 and −2±2j: (s+4)(s²+4s+8) = s³ + 8s² + 24s + 32.
P4 (1 marks): Matches coefficients with a=2, b=1, c=6 to get all three gains: k1 = 18, k2 = 6, K_I = 32. (If the student uses ξ̇ = r − θ with −K_Iξ and gets K_I = −32, full credit provided the convention is stated and the algebra is consistent.)
    level 0.5 of the marks: Two of the three gains correct, or all three correct from matching coefficients but with one arithmetic slip carried from an earlier error.
```

Answer key worked out: Augmented state x=[θ θ̇ ξ]ᵀ, ξ̇=r−θ. With u=−k1θ−k2θ̇+K_Iξ: θ̈ = −(c+bk1)θ − (a+bk2)θ̇ + bK_Iξ. A_cl=[[0,1,0],[−(c+bk1),−(a+bk2),bK_I],[−1,0,0]]. det(sI−A_cl)= s³+(a+bk2)s²+(c+bk1)s+bK_I. Desired: (s+4)(s²+4s+8)=s³+8s²+24s+32. Match with a=2,b=1,c=6: 2+k2=8 → k2=6; 6+k1=24 → k1=18; K_I=32.

## Question 4d (2 marks, maths)

A linearised, gravity-loaded joint, with the input gains lumped into a single constant b, is described by θ̈ + aθ̇ + cθ = bu, a = 2, c = 6, b = 1, where c arises from the gravity load. The nominal controller is state feedback with reference feedforward, u = N_ff r − k1θ − k2θ̇.

(d) Show that the controller designed in part (c) gives zero steady-state error for any values of b and c, provided the closed loop remains stable. Name one practical failure mode of integral action and the standard remedy for it.

```
Marking stance: standard. Full marks: the ξ̇ = r − θ = 0 ⇒ θ = r argument independent of b, c (with stability caveat), plus one valid failure mode with its remedy. Half marks for each point if only partly given as described. No marks for vague statements without the steady-state argument or a failure mode.
P1 (1 marks): Shows zero steady-state error: at steady state all derivatives vanish, including the integrator state, so ξ̇ = r − θ = 0, hence θ = r exactly, independent of a, b and c (ξ just settles at the value giving the needed constant control). Should note the requirement that the closed loop is stable so a steady state is reached. Merely asserting 'integral action removes error' without the ξ̇ = 0 ⇒ θ = r argument earns no marks.
    level 0.5 of the marks: States that integral action gives zero error or that ξ̇ = 0 at steady state, but does not clearly conclude θ = r independent of b and c (or gives only a calculation for the specific values).
P2 (1 marks): Names one valid practical failure mode of integral action AND gives its matching standard remedy. Acceptable pairs: integrator windup with anti-windup (clamping/conditional integration/back-calculation); reduced stability margin/phase lag with lowering KI, placing the integral pole slower than dominant poles, or adding derivative/feedforward; integration of sensor bias with calibration or leaky integrator. A failure mode with no remedy or a mismatched remedy earns at most half.
    level 0.5 of the marks: Names a valid failure mode but gives no remedy or an incorrect/mismatched remedy.
```

Answer key worked out: At steady state all derivatives are zero, including the integrator state ξ̇ = r − θ = 0, so θ = r regardless of a, b, c (ξss = (c + b k1) r/(b KI) adjusts to supply the needed constant control; requires stability and b ≠ 0). Failure mode: integrator windup when the actuator saturates; remedy: anti-windup (conditional integration/clamping or back-calculation).
