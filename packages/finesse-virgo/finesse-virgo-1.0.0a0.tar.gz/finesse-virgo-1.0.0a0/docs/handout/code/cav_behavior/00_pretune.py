# %%
import finesse
from finesse.analysis.actions import (
    Series,
    RunLocks,
    Change,
    Maximize,
    TemporaryParameters,
    OptimiseRFReadoutPhaseDC,
)
from finesse.symbols import CONSTANTS

finesse.configure(plotting=True)

# %% [markdown]
# 1) Power recycled (single) arm cavity model
#
# The model down below consists of an arm cavity of adV+, whose power is recycled by the PRM.
# All the values in this model are inherited by adV+ common kat file.
#
# The model is then tuned to the operating point by:
# * Maximimising the power in the arm cavity
# * Maximising the power in the PR cavity
# * Running the locks to further improve the tuning

# %%
model = finesse.Model()
model.parse(
    """
laser i1 P=20.0  #just one arm cavity
mod eom6 f=6270777 midx=0.22
mod eom8 f=4/3*eom6.f midx=0.15
link(i1, eom6, eom8, PR)

# prc
var lPRC 11.95196615985547

# Rc updated to -1436.38 to match arm cavity (instead of PRC)
m PR R=0.95162 T=0.04835 L=30u Rc=[-1436.38, -1436.38]
s s_prc PR.p2 ITM.p1 L=lPRC

# arm cav
m ITM R=0.986203 L=27u Rc=[-1425, -1425]
s scav ITM.p2 ETM.p1 L=3000
m ETM R=0.9999686 L=27u Rc=[1695, 1695]

# dofs
dof PR_z  PR.dofs.z +1
dof ETM_z ETM.dofs.z +1

# readouts and detectors
readout_rf prc_err PR.p1.o  f=eom8.f phase=0 output_detectors=True
readout_rf arm_err ITM.p1.o f=eom6.f phase=0 output_detectors=True
pd prc_dc PR.p2.o
pd arm_dc ITM.p2.o

# locks
lock prc_lock prc_err.outputs.I PR_z.DC -1.833 1e-6
lock arm_lock arm_err.outputs.I ETM_z.DC -0.0001071 1e-6

modes(maxtem=0)
cav cav ITM.p2.o priority=3
# cav cav PR.p2.o via=ETM.p1.i priority=1
"""
)

# %%
# adjust PRC length to be resonant on 6 MHz
delta_l = 0.5 * CONSTANTS["c0"] / (2 * model.eom6.f) - model.lPRC.value
print("adjusting PRC by ", delta_l.eval())
model.s_prc.L += delta_l.eval()

# pre-tuning the model
model.run(
    TemporaryParameters(
        Series(
            Change({"eom6.midx": 0, "eom8.midx": 0, "PR.misaligned": True}),
            # Maximise arm power
            Maximize("arm_dc", "ETM_z.DC", bounds=[-180, 180], tol=1e-14),
            # Bring in PR
            Change({"PR.misaligned": False}),
            # Maximise PRC power
            Maximize("prc_dc", "PR_z.DC", bounds=[-180, 180], tol=1e-14),
        ),
        exclude=("PR.phi", "ETM.phi", "PR_z.DC", "ETM_z.DC"),
    )
)

# optimising demod phases
model.run(OptimiseRFReadoutPhaseDC("PR_z", "prc_err", "ETM_z", "arm_err", d_dof=1e-7))

# running the looks to further improve the tuning
model.run(RunLocks(method="newton"))

# %%
# save the pre-tuned kat file
targetFile = open("modelTuned.kat", "w")
targetFile.writelines(model.unparse())
targetFile.close()

# %% [markdown]
# # Stability tunings
#
# Produces tuned katfiles under marginally stable conditions.

# %%
for stability, Rc in [
    ("mstable1", -1436.38),
    ("mstable0", -12),
    ("unstable1", -1446.38),
    ("unstable0", -2),
]:
    # set new RoC
    model.PR.Rcx = Rc
    model.PR.Rcy = Rc

    # pre-tuning the model
    model.run(
        TemporaryParameters(
            Series(
                Change({"eom6.midx": 0, "eom8.midx": 0, "PR.misaligned": True}),
                # Maximise arm power
                Maximize("arm_dc", "ETM_z.DC", bounds=[-180, 180], tol=1e-14),
                # Bring in PR
                Change({"PR.misaligned": False}),
                # Maximise PRC power
                Maximize("prc_dc", "PR_z.DC", bounds=[-180, 180], tol=1e-14),
            ),
            exclude=("PR.phi", "ETM.phi", "PR_z.DC", "ETM_z.DC"),
        )
    )

    # optimising demod phases
    model.run(
        OptimiseRFReadoutPhaseDC("PR_z", "prc_err", "ETM_z", "arm_err", d_dof=1e-7)
    )

    # running the looks to further improve the tuning
    model.run(RunLocks(method="newton"))

    # save the pre-tuned kat file
    targetFile = open(f"modelTuned_{stability}.kat", "w")
    targetFile.writelines(model.unparse())
    targetFile.close()

# %%
