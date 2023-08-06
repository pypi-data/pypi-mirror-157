# %%
import numpy as np
import matplotlib.pyplot as plt

import finesse
from finesse.analysis.actions import Noxaxis

from finesse.knm import Map
from finesse.utilities.maps import circular_aperture

finesse.configure(plotting=True)

# %%
# load the tuned kat file (output from Riccardo's `00_pretune.ipynb``)
base = finesse.Model()
base.parse_file("modelTuned.kat")

# apply aperture to ITM
diameter = 0.350

# create the aperture map
radius = diameter / 2
x = y = np.linspace(-radius, radius, 200)
smap = Map(
    x,
    y,
    amplitude=circular_aperture(x, y, radius, x_offset=0.0, y_offset=0.0),
)

# apply to relevant surface
base.ITM.surface_map = smap

# add some scanning parameters
base.parse("var cPR -1436.38")
base.parse("var cETM 1696")

base.PR.Rcx = base.cPR.ref
base.PR.Rcy = base.cPR.ref
base.ETM.Rcx = base.cETM.ref
base.ETM.Rcy = base.cETM.ref

base.parse(
    """
# 6 MHz detectors
pd1 pPR_6 PR.p2.i f=2*eom6.f
ad upper PR.p2.i f=eom6.f
ad lower PR.p2.i f=-eom6.f

# determine power from detectors
# mathd pPR abs(pPR_6)
mathd pPR abs(upper)**2+abs(lower)**2

# add mismatch detector
mmd mm ITM.p2.i ITM.p1.o

# add beam parameter detector
bp pw0 i1.p1.i w0
bp pz i1.p1.i z

# set homs
modes(even, maxtem=8)

# scan RoCs
xaxis(cPR, lin, -1436.38, -1433.38, 20, pre_step=run_locks(method="newton"))
# xaxis(cPR, lin, -1436.38, -1433.38, 20)
"""
)

# keep initial q parameter
base.run(Noxaxis())
q1 = base.PR.p1.i.q
print(q1)

# %%
code1 = """
# PRC
cav cavPR PR.p2.o via=ITM.p1.i priority=1
"""

code2 = """
# PRC
cav cavPR PR.p2.o via=ETM.p1.i priority=1
"""

# %%
# short cavity
model = base.deepcopy()
model.parse(code1)
out = model.run()

# short cavity, fixed q
model1 = base.deepcopy()
model1.parse(code1)
model1.PR.p1.i.q = q1
out1 = model1.run()

# no PR cavity, fixed q
model2 = base.deepcopy()
model2.PR.p1.i.q = q1
out2 = model2.run()

# cavities disabled
model3 = base.deepcopy()
model3.parse(code1)
model3.sim_trace_config["disable"] = ["cavPR"]
out3 = model3.run()

# long cavity
model4 = base.deepcopy()
model4.parse(code2)
out4 = model4.run()

# long cavity, fixed q
model5 = base.deepcopy()
model5.parse(code2)
model5.PR.p1.i.q = q1
out5 = model5.run()

x = np.abs(out.x1 - out.x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Power of 6 MHz sideband in PRC vs PR RoC (aperture)")
ax1.plot(x, out["pPR"], "--", label="with cavities")
ax1.plot(x, out4["pPR"], ":", label="with long cavities", lw=4)
ax1.plot(x, out5["pPR"], "o", label="with long cavities, q fixed", lw=4)
ax1.plot(x, out1["pPR"], "-.", label="with cavities, q fixed")
ax1.plot(x, out2["pPR"], "-", label="cavities removed, q fixed")
ax1.plot(x, out3["pPR"], ".", label="cavities disabled")
# ax1.set_ylim(880, 900)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Power [W]")
ax1.legend()
fig.savefig("plots/sb-0b-prc-beam-parameters-overview.pdf")

# %%
base.modes("even", maxtem=20)

# long cavity, fixed q
model5 = base.deepcopy()
model5.parse(code2)
model5.PR.p1.i.q = q1
out5 = model5.run()

ref_trace = out5

# %%
# run all traces at different homs

outs = []
outs1 = []
outs2 = []
outs3 = []
outs4 = []
outs5 = []

homs = [4, 8, 12, 16, 20]

for hom in homs:
    base.modes("even", maxtem=hom)

    # short cavity
    model = base.deepcopy()
    model.parse(code1)
    outs.append(model.run())

    # short cavity, fixed q
    model1 = base.deepcopy()
    model1.parse(code1)
    model1.PR.p1.i.q = q1
    outs1.append(model1.run())

    # no PR cavity, fixed q
    model2 = base.deepcopy()
    model2.PR.p1.i.q = q1
    outs2.append(model2.run())

    # cavities disabled
    model3 = base.deepcopy()
    model3.parse(code1)
    model3.sim_trace_config["disable"] = ["cavPR"]
    outs3.append(model3.run())

    # long cavity
    model4 = base.deepcopy()
    model4.parse(code2)
    outs4.append(model4.run())

    # long cavity, fixed q
    model5 = base.deepcopy()
    model5.parse(code2)
    model5.PR.p1.i.q = q1
    outs5.append(model5.run())

# %%
x = np.abs(outs[-1].x1 - outs[-1].x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Power of 6 MHz sideband in PRC vs PR RoC (aperture)")
ax1.plot(x, outs[-1]["pPR"], "--", label="with cavities")
ax1.plot(x, outs4[-1]["pPR"], ":", label="with long cavities", lw=4)
ax1.plot(x, outs5[-1]["pPR"], "o", label="with long cavities, q fixed", lw=4)
ax1.plot(x, outs1[-1]["pPR"], "-.", label="with cavities, q fixed")
ax1.plot(x, outs2[-1]["pPR"], "-", label="cavities removed, q fixed")
ax1.plot(x, outs3[-1]["pPR"], ".", label="cavities disabled")
# ax1.set_ylim(880, 900)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Power [W]")
ax1.legend()
fig.savefig("plots/sb-1b-prc-beam-parameters-overview-maxtem20.pdf")

# %%
x = np.abs(outs[0].x1 - outs[0].x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Convergence of short cavity with higher maxtem (aperture)")
ax1.plot(x, outs5[0]["pPR"], "ok", label="with long cavities, q fixed", lw=4)

for i in range(len(homs)):
    ax1.plot(x, outs1[i]["pPR"], "-.", label=f"maxtem={homs[i]}")

# ax1.set_ylim(880, 900)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Power [W]")
ax1.legend()
fig.savefig("plots/sb-2b-prc-beam-parameters-short-convergence.pdf")


# %%
x = np.abs(outs[0].x1 - outs[0].x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Convergence of long cavity with higher maxtem (aperture)")
ax1.plot(x, outs5[0]["pPR"], "ok", label="with long cavities, q fixed", lw=4)

for i in range(len(homs)):
    ax1.plot(x, outs5[i]["pPR"], "-.", label=f"maxtem={homs[i]}")

# ax1.set_ylim(880, 900)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Power [W]")
ax1.legend()
fig.savefig("plots/sb-3b-prc-beam-parameters-long-convergence.pdf")
