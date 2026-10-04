(* ::Package:: *)
(* Mathematica code for the nonlinear SIR model (Math 3440 project) *)

(* ---------- 1. Eigenvalue crossing at R0 = 1 ---------- *)
Clear[gamma, R, lambda2, bifPlot];
gamma = 0.8;
lambda2[R_] := gamma (R - 1);
bifPlot =
  Plot[lambda2[R], {R, 0, 3},
    AxesLabel -> {"R0", "lambda2"},
    PlotLabel -> "Eigenvalue crossing at R0 = 1",
    PlotRange -> All,
    Epilog -> {
      Red, PointSize[0.02], Point[{1, 0}],
      Dashed, Gray, Line[{{1, -gamma}, {1, gamma}}],
      Dashed, Gray, Line[{{0, 0}, {3, 0}}],
      Text["stable", {0.4, -0.4}],
      Text["unstable", {2.2, 0.4}]
    },
    ImageSize -> Large
  ];
Export["nonlinear_diagram_gr1.eps", bifPlot, "EPS"];

(* ---------- 2. Phase plane, nullclines and fixed points ---------- *)
Clear[beta, gamma, s, i, R0, fS, fI,
  streamPlot, nullclineS, nullclineI, fixedPts, phasePlanePlot];
beta = 1.5;
gamma = 0.8;
R0 = beta/gamma;
fS[s_, i_] := -beta s i;
fI[s_, i_] := beta s i - gamma i;

streamPlot =
  StreamPlot[{fS[s, i], fI[s, i]}, {s, 0, 1}, {i, 0, 0.6},
    StreamStyle -> Arrowheads[0.02],
    AxesLabel -> {"s (susceptible fraction)", "i (infected fraction)"},
    PlotRangePadding -> Scaled[0.02],
    ImageSize -> Large
  ];
nullclineS =
  ContourPlot[fS[s, i] == 0, {s, 0, 1}, {i, 0, 0.6},
    ContourStyle -> {Red, Thick}];
nullclineI =
  ContourPlot[fI[s, i] == 0, {s, 0, 1}, {i, 0, 0.6},
    ContourStyle -> {Blue, Thick}];
fixedPts =
  Graphics[{
    Black, PointSize[0.018],
    Table[Point[{sStar, 0}], {sStar, 0, 1, 0.2}],
    Red, PointSize[0.025], Point[{1, 0}]
  }];
phasePlanePlot =
  Show[streamPlot, nullclineS, nullclineI, fixedPts,
    PlotLabel -> Row[{"Phase plane, nullclines and fixed points (R0 = ",
      NumberForm[R0, {3, 2}], ")"}]
  ];
Export["nonlinear_diagram_gr2.eps", phasePlanePlot, "EPS"];

(* ---------- 3. Phase plane for the Costco post (fitted beta, gamma) ---------- *)
Clear[beta, gamma, s, i, R0, fS, fI,
  threshold, stream, nullclines, sol, trajectory, phasePlaneCostco];
beta = 0.38;
gamma = 0.18;
R0 = beta/gamma;
fS[s_, i_] := -beta s i;
fI[s_, i_] := beta s i - gamma i;
threshold = gamma/beta;

stream =
  StreamPlot[{fS[s, i], fI[s, i]}, {s, 0, 1.05}, {i, 0, 0.6},
    Axes -> True,
    AxesLabel -> {"s (Susceptible)", "i (Infected)"},
    PlotLabel -> Style["Phase Plane: Costco Post (R0 = " <>
      ToString[NumberForm[R0, {3, 2}]] <> ")", 14, Bold],
    StreamStyle -> {Gray, Arrowheads[0.02]},
    StreamPoints -> Fine,
    GridLines -> Automatic
  ];
nullclines =
  Graphics[{
    {Gray, Dashed, Thickness[0.005], Line[{{0, 0}, {1.05, 0}}]},
    {Darker[Green], Dashed, Thickness[0.005], Line[{{threshold, 0}, {threshold, 0.6}}]},
    Text[Style["Epidemic Threshold\ns = " <> ToString[NumberForm[threshold, {3, 2}]],
      10, Darker[Green]], {threshold + 0.15, 0.5}]
  }];
sol =
  NDSolve[{
    s'[t] == -beta s[t] i[t],
    i'[t] == beta s[t] i[t] - gamma i[t],
    s[0] == 0.99,
    i[0] == 0.01
  }, {s, i}, {t, 0, 100}];
trajectory =
  ParametricPlot[Evaluate[{s[t], i[t]} /. sol], {t, 0, 100},
    PlotStyle -> {Red, Thickness[0.007]}];
phasePlaneCostco =
  Show[stream, nullclines, trajectory,
    PlotRange -> {{0, 1.05}, {0, 0.6}},
    ImageSize -> Large,
    Frame -> True,
    FrameLabel -> {"Susceptible Fraction (s)", "Infected Fraction (i)"}
  ];
Export["nonlinear_diagram_gr3.eps", phasePlaneCostco, "EPS"];
