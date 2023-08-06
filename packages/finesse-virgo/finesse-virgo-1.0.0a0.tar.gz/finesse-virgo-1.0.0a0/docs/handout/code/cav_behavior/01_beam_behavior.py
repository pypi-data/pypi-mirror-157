# %%
import numpy as np
import matplotlib.pyplot as plt

import finesse
from finesse.analysis.actions import Noxaxis

finesse.configure(plotting=True)

# %%
# load the tuned kat file (output from Riccardo's `00_pretune.ipynb``)
base = finesse.Model()
base.parse_file("modelTuned.kat")

# add some scanning parameters
base.parse("var cPR -1435.88")
base.parse("var cETM 1696")

base.PR.Rcx = base.cPR.ref
base.PR.Rcy = base.cPR.ref
base.ETM.Rcx = base.cETM.ref
base.ETM.Rcy = base.cETM.ref

base.parse(
    """
# add power detector
pd pPR PR.p2.i

# add mismatch detector
mmd mm ITM.p2.i ITM.p1.o

# add beam parameter detector
bp pw0 i1.p1.i w0
bp pz i1.p1.i z

# set homs
modes(even, maxtem=4)

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
# model.unparse_file('tuned_model_w_short_cavity.kat')
out = model.run()
# print(model.mismatches_table())

# short cavity, fixed q
model1 = base.deepcopy()
model1.parse(code1)
model1.PR.p1.i.q = q1
out1 = model1.run()
# print(model1.mismatches_table())

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
# print(model4.mismatches_table())

# long cavity, fixed q
model5 = base.deepcopy()
model5.parse(code2)
model5.PR.p1.i.q = q1
out5 = model5.run()

x = np.abs(out.x1 - out.x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Power in PRC vs PR RoC")
ax1.plot(x, out["pPR"], "--", label="with cavities")
ax1.plot(x, out4["pPR"], ":", label="with long cavities", lw=4)
ax1.plot(x, out5["pPR"], "o", label="with long cavities, q fixed", lw=4)
ax1.plot(x, out1["pPR"], "-.", label="with cavities, q fixed")
ax1.plot(x, out2["pPR"], "-", label="cavities removed, q fixed")
ax1.plot(x, out3["pPR"], ".", label="cavities disabled")
ax1.set_ylim(880, 900)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Power [W]")
ax1.legend()
fig.savefig("plots/0-prc-beam-parameters-overview.pdf")

x = np.abs(out.x1 - out.x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Mismatch vs RoC")
ax1.plot(x, out["mm"], "--", label="with cavities")
ax1.plot(x, out4["mm"], ":", label="with long cavities", lw=4)
# ax1.plot(x,out5['mm'], 'o', label='with long cavities, q fixed', lw=4)
# ax1.plot(x,out1['mm'], '-.', label='with cavities, q fixed')
# ax1.plot(x,out2['mm'], '-', label='cavities removed, q fixed')
# ax1.plot(x,out3['mm'], '.', label='cavities disabled')
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Mismatch")
ax1.legend()
fig.savefig("plots/1-prc-beam-parameters-mismatch.pdf")

x = np.abs(out.x1 - out.x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Waist size at laser vs PR RoC")
ax1.plot(x, out["pw0"], "--", label="with cavities")
ax1.plot(x, out4["pw0"], ":", label="with long cavities", lw=4)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Waist size")
ax1.legend()
fig.savefig("plots/2-prc-beam-parameters-w0.pdf")

x = np.abs(out.x1 - out.x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Waist position at laser vs PR RoC")
ax1.plot(x, out["pz"], "--", label="with cavities")
ax1.plot(x, out4["pz"], ":", label="with long cavities", lw=4)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Waist position")
ax1.legend()
fig.savefig("plots/3-prc-beam-parameters-z.pdf")

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

out = []
out1 = []
out2 = []
out3 = []
out4 = []
out5 = []

homs = [4, 8, 12, 16, 20]

for hom in homs:
    base.modes("even", maxtem=hom)

    # short cavity
    model = base.deepcopy()
    model.parse(code1)
    out.append(model.run())

    # short cavity, fixed q
    model1 = base.deepcopy()
    model1.parse(code1)
    model1.PR.p1.i.q = q1
    out1.append(model1.run())

    # no PR cavity, fixed q
    model2 = base.deepcopy()
    model2.PR.p1.i.q = q1
    out2.append(model2.run())

    # cavities disabled
    model3 = base.deepcopy()
    model3.parse(code1)
    model3.sim_trace_config["disable"] = ["cavPR"]
    out3.append(model3.run())

    # long cavity
    model4 = base.deepcopy()
    model4.parse(code2)
    out4.append(model4.run())

    # long cavity, fixed q
    model5 = base.deepcopy()
    model5.parse(code2)
    model5.PR.p1.i.q = q1
    out5.append(model5.run())

# %% [markdown]
# # Maxtem convergence of short cavity with fixed q

# %%
x = np.abs(out[0].x1 - out[0].x1[0])
fig, ax1 = plt.subplots()
ax1.set_title("Convergence of short cavity with higher maxtem")
ax1.plot(x, out5[0]["pPR"], "ok", label="with long cavities, q fixed", lw=4)

for i in range(len(homs)):
    ax1.plot(x, out1[i]["pPR"], "-.", label=f"maxtem={homs[i]}")

ax1.set_ylim(880, 900)
ax1.set_xlabel("Relative ROC tuning [m]")
ax1.set_ylabel("Power [W]")
ax1.legend()

fig.savefig("plots/4-prc-beam-parameters-convergence.pdf")
