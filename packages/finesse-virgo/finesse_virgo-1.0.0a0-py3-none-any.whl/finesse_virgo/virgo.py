import finesse

from finesse.knm import Map
from finesse.utilities.maps import circular_aperture
from finesse.utilities.tables import Table, NumberTable
from finesse.symbols import CONSTANTS

from finesse.analysis.actions import (
    Series,
    RunLocks,
    Change,
    SensingMatrixDC,
    Minimize,
    Maximize,
    TemporaryParameters,
    OptimiseRFReadoutPhaseDC,
    Xaxis,
    Noxaxis,
    Temporary,
)

import os
import glob
import importlib.resources
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

from .actions import DARM_RF_to_DC

from finesse.exceptions import ModelAttributeError
from finesse.components import DegreeOfFreedom

# definition of thermal states
THERMAL_STATES = {
    "design-matched": {
        "PR.Rc": -1430,
        "SR.Rc": 1430,
        "f_CPN_TL.value": -338008.0,
        "f_CPW_TL.value": -353134.0,
    },
    "cold": {
        "PR.Rc": -1477,
        "SR.Rc": 1443,
        "f_CPN_TL.value": float("inf"),
        "f_CPW_TL.value": float("inf"),
    },
}

# definition of aperture size for each mirror.
#   as (coating diameter, substrate diameter)
APERTURE_SIZES = {
    "NI": (0.340, 0.350),
    "NE": (0.340, 0.350),
    "WI": (0.340, 0.350),
    "WE": (0.340, 0.350),
    "PR": (0.340, 0.350),
    "SR": (0.340, 0.350),
    "BS": (0.530, 0.550),
}


def make_virgo(**kwargs):
    """Returns a fully tuned Virgo ifo as a Finesse model.

    Accepts same configurations as the Virgo class.
    """
    virgo = Virgo(**kwargs)
    virgo.make()
    return virgo.model


class Virgo:
    """Container for the Virgo tuning script which houses and configures the model
    through individual steps producing a tuned interferometer."""

    def __init__(
        self,
        file_to_parse=None,
        display_plots=False,
        thermal_state=None,
        use_3f_error_signals=False,
        with_apertures=False,
        maxtem=None,
        verbose=False,
        x_scale=1,
        zero_k00=False,
        parse_locks=True,
        parse_additional_katscript=False,
    ):
        self.display_plots = display_plots
        self.thermal_state = thermal_state
        self.use_3f_error_signals = use_3f_error_signals
        self.with_apertures = with_apertures
        self.verbose = verbose

        # create the model
        self.model = finesse.Model()

        # parse the katscript file, if provided
        if file_to_parse:
            # if directory is provided, parse every kat file
            if os.path.isdir(file_to_parse):
                if self.verbose:
                    print(f"Input directory found: {file_to_parse}")
                    print("Parsing input files...")

                # TODO: need to fix, will only work with local directory
                for input_file in sorted(glob.glob(f"{file_to_parse}/*.kat")):
                    self.model.parse_file(input_file)

                    if self.verbose:
                        print(f"Parsed input file {input_file}.")
            else:
                # otherwise, parse the provided file
                # this will typically be one of two situations
                #   1) output from the unparser, in which everything needed is provided
                #   2) a modified common file, in which case additional katscript will need to be parsed
                self.model.parse_file(file_to_parse)
        else:
            if self.verbose:
                print("Parsing common katfile...")

            self.model.parse(
                importlib.resources.read_text(
                    "finesse_virgo.katscript", "00_virgo_common_file.kat"
                )
            )

        # parse additional katscript if needed
        # case 1) the flag is set
        # case 2) default (no input file/directory provided)
        if parse_additional_katscript or not file_to_parse:
            if self.verbose:
                print("Parsing additional katscript...")

            self.model.parse(
                importlib.resources.read_text(
                    "finesse_virgo.katscript", "01_additional_katscript.kat"
                )
            )

        # setting phase config to not zero K00 phase, see 'phase' command in F2.
        self.model._settings.phase_config.zero_k00 = zero_k00

        # set x_scale to (maybe) reduce numerical noise from radiation pressure.
        self.model._settings.x_scale = x_scale

        # By default, surfaces are infinite. Using apertures limit their size.
        if with_apertures:
            self.use_apertures()

        # Set maxtem if provided
        # ex: 'off', 2, ('even', 10)
        if maxtem == "off":
            self.model.modes("off")
        elif isinstance(maxtem, int):
            self.model.modes(maxtem=maxtem)
        elif isinstance(maxtem, tuple) and len(maxtem) == 2:
            self.model.modes(maxtem[0], maxtem=maxtem[1])

        # Setting to adjust the RoCs and focal points as defined in the thermal state.
        if thermal_state:
            self.set_thermal_state(thermal_state)

        # Define a control scheme to link DoFs to readouts
        # Should be a list of tuples as (dof, readout, port)
        self.control_scheme = [
            ("PRCL", "B2_8", "I"),
            ("MICH", "B2_56", "Q"),
            ("CARM", "B2_6", "I"),
            ("DARM", "B1p_56", "I"),
            ("SRCL", "B2_56", "I"),
        ]

        # If using 3f error signals, we need to increase the order of modulation in addition to the control scheme for the central interferometer.
        if use_3f_error_signals:
            self.model.eom6.order = 3
            self.model.eom8.order = 3
            self.model.eom56.order = 3

            self.control_scheme = [
                ("PRCL", "B2_6_3f", "I"),
                ("MICH", "B2_56_3f", "Q"),
                ("CARM", "B2_6", "I"),
                ("DARM", "B1p_56", "I"),
                ("SRCL", "B2_56_3f", "I"),
            ]

        # extract individual dof/readout arrays for later use
        self.dofs = [x[0] for x in self.control_scheme]
        self.readouts = [x[1] for x in self.control_scheme]
        self.unique_readouts = list(dict.fromkeys(self.readouts))
        self.dof_readouts = [f"{x[1]}_{x[2]}" for x in self.control_scheme]

        # parse the locks using the control scheme
        #   but provide ability to skip incase they already exist
        if parse_locks:
            self.parse_locks()

    def deepcopy(self):
        return deepcopy(self)

    def make(self, verbose=False):
        """Performs full make process."""

        # step 1: adjust the cavity lengths
        print("Adjusting recycling cavity lengths...")
        self.adjust_recycling_cavity_length("PRC", "lPRC", "lPOP_BS", verbose=verbose)
        self.adjust_recycling_cavity_length("SRC", "lSRC", "lsr", verbose=verbose)

        # step 2: pretune
        print("Pretuning...")
        self.pretune()

        # step 3: optimize demodulation phases
        print("Optimizing demodulation phases...")
        self.optimize_demodulation_phase()

        # step 4: optimize lock gains
        print("Optimizing lock gains...")
        self.optimize_lock_gains()

        # step 5: run RF locks
        print("Running RF locks...")
        if self.verbose:
            self.print_dofs("before locking")

        self.model.run(RunLocks(method="newton"))

        if self.verbose:
            self.print_dofs("after locking")

        # step 6: switch to DC locks
        print("Switching to DARM DC lock...")
        if self.verbose or verbose:
            self.print_dofs("before locking")

        self.model.run(DARM_RF_to_DC())

        if self.verbose or verbose:
            self.print_dofs("after locking")

        print("Done.")

    # TODO: add to __str__ in Lock
    def print_locks(self):
        for lock in self.model.locks:
            print(
                lock.name,
                lock.error_signal.name,
                lock.feedback.name,
                "gain=" + str(lock.gain),
                "disabled=" + str(lock.disabled),
            )

    def print_info(self):
        self.print_lengths()
        self.print_thermal_values()
        self.print_tunings()
        self.print_powers()

    def print_settings(self):
        return Table(
            [
                ["Setting", "Value"],
                ["Modes", self.model.modes_setting["modes"]],
                ["Maxtem", self.model.modes_setting["maxtem"]],
                ["zero_k00", self.model._settings.phase_config.zero_k00],
                ["x_scale", self.model._settings.x_scale],
            ],
            headerrow=True,
            headercolumn=True,
            alignment=["left", "right"],
        )

    def get_dofs_dc(self):
        return [self.model.get(f"{dof}.DC") for dof in self.dofs]

    # can be repeated
    def set_thermal_state(self, state: str) -> None:
        """Sets thermal parameter values for the provided state.

        Parameters
        ----------
        state : str
            Key for desired thermal state as defined in THERMAL_STATES.

        Raises
        ------
        Exception
            Raised when the key does not exist in THERMAL_STATES.
        """

        # make sure the state exists
        if state not in THERMAL_STATES.keys():
            raise Exception(
                f"Invalid thermal state `{state}`. Accepted thermal states: [{', '.join([f'`{key}`' for key in THERMAL_STATES.keys()])}]"
            )

        # set the state
        for key, value in THERMAL_STATES[state].items():
            self.model.set(key, value)

    def use_apertures(self, substrate: bool = False) -> None:
        """Convenience function to use apertures. Creates surface maps for each major
        surface in Virgo. See TDR table 5.2.

        Parameters
        ----------
        model : Model
            Finesse Virgo model containing all surfaces.
        substrate : bool
            Option to use the coating diameter (False) or the substrate diameter (True).
        """

        # (surface name, coating diameter, substrate diameter) values in meters
        for m, s in APERTURE_SIZES.items():
            # select coating or substrate
            diameter = s[int(substrate)]

            # create the aperture map
            radius = diameter / 2
            x = y = np.linspace(-radius, radius, 100)
            smap = Map(
                x,
                y,
                amplitude=circular_aperture(x, y, radius, x_offset=0.0, y_offset=0.0),
            )

            # apply to relevant surface
            self.model.get(m).surface_map = smap

    def adjust_PRC_length(self):
        self.adjust_recycling_cavity_length("PRC", "lPRC", "lPOP_BS")

    def adjust_SRC_length(self):
        self.adjust_recycling_cavity_length("SRC", "lSRC", "lsr")

    # can be repeated
    # TODO: should the length in the common file use the variable?
    #   Could otherwise be done with just the cavity space: self.adjust_cavity_length("lsr")
    def adjust_recycling_cavity_length(
        self, cavity: str, L_in: str, S_out: str, verbose=False
    ):
        """Adjust cavity length so that it fulfils the requirement:

            L = 0.5 * c / (2 * f6), see TDR 2.3 (VIR–0128A–12).

        Parameters
        ----------
        cavity : str
            Name of the cavity being adjusted.
        L_in : str
            Variable used to define the length of the cavity. Needed because the common file does not use a variable.
        S_out : str
            Name of the space component used to adjust the cavity.
        """

        # works also for legacy
        f6 = self.model.get("eom6.f").value

        if self.verbose or verbose:
            print(f"--  adjusting {cavity} length")

        # calculate the required adjustment
        tmp = 0.5 * CONSTANTS["c0"] / (2 * f6)
        delta_l = tmp.eval() - self.model.get(L_in).value.eval()

        if self.verbose or verbose:
            print(f"    adjusting {S_out}.L by {delta_l:.4g} m")

        # apply the adjustment
        self.model.get(S_out).L += delta_l

    # can be repeated
    def pretune(self, verbose=False):
        # store the modulation index for use later
        midx = self.model.eom56.midx.value

        # do the pretuning
        self.model.run(
            TemporaryParameters(
                Series(
                    # Switch off the modulators and remove SR and PR by misaligning them. This ensures only the carrier is present and the arms are isolated.
                    Change(
                        {
                            "eom6.midx": 0,
                            "eom8.midx": 0,
                            "eom56.midx": 0,
                            "SR.misaligned": True,
                            "PR.misaligned": True,
                            "SRAR.misaligned": True,
                            "PRAR.misaligned": True,
                        }
                    ),
                    # Maximise arm power
                    Maximize("B7_DC", "NE_z.DC", bounds=[-180, 180], tol=1e-14),
                    Maximize("B8_DC", "WE_z.DC", bounds=[-180, 180], tol=1e-14),
                    # Minimise dark fringe power
                    Minimize("B1_DC", "MICH.DC", bounds=[-180, 180], tol=1e-14),
                    # Bring back PR
                    Change({"PR.misaligned": False}),
                    # Maximise PRC power
                    Maximize("CAR_AMP_BS", "PRCL.DC", bounds=[-180, 180], tol=1e-14),
                    # Bring in SR
                    Change({"SR.misaligned": False}),
                    # Maximise SRC power
                    # B4_112 requires 56MHz
                    Change({"SRCL.DC": 0, "eom56.midx": midx}),
                    Maximize("B4_112_mag", "SRCL.DC", bounds=[-180, 180], tol=1e-14),
                ),
                exclude=(
                    "PR.phi",
                    "NI.phi",
                    "NE.phi",
                    "WI.phi",
                    "WE.phi",
                    "SR.phi",
                    "NE_z.DC",
                    "WE_z.DC",
                    "MICH.DC",
                    "PRCL.DC",
                    "SRCL.DC",
                ),
            )
        )

        # round off dofs to a reasonable level of precision
        self.model.NE_z.DC = round(self.model.NE_z.DC.value, 4)
        self.model.WE_z.DC = round(self.model.WE_z.DC.value, 4)
        self.model.MICH.DC = round(self.model.MICH.DC.value, 4)
        self.model.PRCL.DC = round(self.model.PRCL.DC.value, 4)
        self.model.SRCL.DC = round(self.model.SRCL.DC.value, 3)

        if self.verbose or verbose:
            print("--  dof tunings")
            for dof in ["NE_z", "WE_z", "MICH", "PRCL", "SRCL"]:
                print(f'    {dof}: {self.model.get(dof+".DC").value}')
            # self.print_tunings()
            # TODO: copy from original notebook
            # self.print_powers()

    def print_dofs(self, msg=None):
        print(f"--  DOFs {msg if msg else ''}:")
        for dof in self.dofs:
            print(f'    {dof}: {self.model.get(dof+".DC").value}')

    # can be repeated
    def apply_dc_offset(self, verbose=False):
        """_summary_"""
        self.model.run(
            Series(
                # Switch off the modulators for pretuning
                TemporaryParameters(
                    Series(
                        Change({"eom6.midx": 0, "eom8.midx": 0, "eom56.midx": 0}),
                        # Find the exact dark fringe, then search only for the negative solution
                        Minimize("B1_DC", "DARM.DC", tol=1e-10),
                        Minimize(
                            "B1_DC",
                            "DARM.DC",
                            method=None,
                            bounds=[self.model.DARM.DC - 90, self.model.DARM.DC],
                            offset=4e-3,
                            tol=1e-14,
                        ),
                    ),
                    exclude=("NE_z.DC", "WE_z.DC", "DARM.DC"),
                )
            )
        )

        if self.display_plots:
            self.plot_QNLS(axis=[5, 500, 100])

        # if self.verbose or verbose:
        # TODO: copy from original notebook
        # self.print_powers()

        if self.display_plots:
            self.dof_plot("PRCL", "CAR_AMP_BS", xscale=50)
            self.dof_plot("DARM", "CAR_AMP_AS", xscale=0.001)
            self.dof_plot("NE_z", "CAR_AMP_N")
            self.dof_plot("WE_z", "CAR_AMP_W")
            self.dof_plot("MICH", "CAR_AMP_AS", xscale=6)
            self.dof_plot("SRCL", "CAR_AMP_AS", xscale=50)

    def dof_plot(self, dof, detector, axis=[-1, 1, 300], xscale=1, logy=True):
        """Sweep across a DoF, reading out at the provided detector."""
        axis = np.array(axis, dtype=np.float64)
        axis[:2] *= xscale
        out = self.model.run(
            Xaxis(f"{dof}.DC", "lin", axis[0], axis[1], axis[2], relative=True)
        )

        try:
            out.plot([detector], logy=logy, degrees=False)
        except AttributeError:
            # Workaround for `out.plot()` not currently working for readouts
            plt.figure()
            if logy:
                plt.semilogy(out.x[0], np.abs(out[detector]), label=detector)
            else:
                plt.plot(out.x[0], np.abs(out[detector]), label=detector)
            plt.xlabel(dof.name + " DC")
            plt.ylabel("A.U.")
            plt.show()

        return out

    def print_powers(self):
        out = self.model.run(
            Series(
                Temporary(
                    Change({"eom8.midx": 0, "eom6.midx": 0, "eom56.midx": 0}), Noxaxis()
                )
            )
        )

        data = []
        rows = []
        for detector in self.model.detectors:
            power = np.abs(out[detector]) ** 2
            if "CAR_AMP" in detector.name:
                rows.append(f"{detector.name:12s}")
                data.append([power, power / self.model.i1.P])
        return NumberTable(
            data,
            colnames=["Detector", "Power [W]", "Pow. ratio"],
            rownames=rows,
            numfmt=["{:9.4g}", "{:9.4g}"],
        )

    def optimize_demodulation_phase(self, verbose=False):
        """Optimize the demodulation phases."""
        # Ignore MICH since its demodulation phase can be inferred from SRCL.
        self.model.run(
            OptimiseRFReadoutPhaseDC(
                *[
                    i
                    for s in zip(self.dofs, self.readouts)
                    for i in s
                    if s[0] != "MICH"
                ],
                d_dof=1e-7,
            )
        )

        self.sensing_matrix = self.get_sensing_matrix()

        if self.verbose or verbose:
            print("--  Optimized demodulation phases:")
            for dof, readout, port in self.control_scheme:
                phase = self.model.get(f"{readout}.phase").value + (
                    0 if port == "I" else 90
                )
                print(f"    {dof:8} {'_'.join([readout, port]):10}: phase={phase:8.4f}")

            print("--  Suggested lock gains:")
            for dof, readout, port in self.control_scheme:
                optical_gain = self.sensing_matrix.out[
                    self.dofs.index(dof), self.readouts.index(readout)
                ]
                lock_gain = -1 / (
                    optical_gain.real if port == "I" else optical_gain.imag
                )

                print(
                    f"    {dof:8s} {'_'.join([readout, port]):10s}: {-1/lock_gain:10.5g}"
                )

    def get_sensing_matrix(self):
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        return self.model.run(SensingMatrixDC(self.dofs, self.readouts, d_dof=1e-6))

    def parse_locks(self):
        """Parses the locks contained within the control scheme. Assumes the locks have
        not already been parsed. If any lock already exists, then this will do nothing.

        Returns True when parsing occurs, False when it is skipped.
        """

        # check if any of the locks already exist
        exists = False
        for dof in self.dofs:
            try:
                self.model.get(f"{dof}_lock")
            except ModelAttributeError:
                # no lock, so it needs to be parsed
                pass
            else:
                # lock found, do not parse
                exists = True

        # if any of the locks already exist, do nothing
        if exists:
            if self.verbose:
                print("Locks already exist.")
            return False

        # We can generate the locks from the control strategy using the sensing matrix.
        for dof, readout, port in self.control_scheme:
            # Handle DARM separately for now since we'll lock on both RF and DC.
            if dof != "DARM":
                self.model.parse(
                    f"lock {dof}_lock {readout}.outputs.{port} {dof}.DC 1 1e-6"
                )
            else:
                self.model.parse(
                    f"lock {dof}_rf_lock {readout}.outputs.{port} {dof}.DC 1 1e-6"
                )

                # lock DARM to 4mW
                # TODO: incorporate this into the control scheme somehow
                self.model.parse(
                    f"lock {dof}_dc_lock B1.outputs.DC {dof}.DC 1 1e-6 offset=4m disabled=true"
                )

    def optimize_lock_gains(self, verbose=False):
        # recalculate the sensing matrix
        self.sensing_matrix = self.get_sensing_matrix()

        # for each dof
        for dof, readout, port in self.control_scheme:
            # get the optical gain from the sensing matrix and calculate the lock gain
            optical_gain = self.sensing_matrix.out[
                self.dofs.index(dof), self.readouts.index(readout)
            ]
            lock_gain = -1 / (optical_gain.real if port == "I" else optical_gain.imag)

            # set the lock gain
            if dof != "DARM":
                self.model.get(f"{dof}_lock").gain = lock_gain
            else:
                self.model.get(f"{dof}_rf_lock").gain = lock_gain
                self.model.get(f"{dof}_dc_lock").gain = lock_gain

        if self.verbose or verbose:
            print("--  Optimized lock gains:")
            for dof, readout, port in self.control_scheme:
                if dof != "DARM":
                    print(
                        f"    {dof:8s} {'_'.join([readout, port]):10s}: {self.model.get(f'{dof}_lock').gain:10.5g}"
                    )
                else:
                    # lock gain for DARM RF and DC will be the same
                    print(
                        f"    {dof:8s} {'_'.join([readout, port]):10s}: {self.model.get(f'{dof}_rf_lock').gain:10.5g}"
                    )

    def optimize_TL(self, accuracy=1, verbose=False):
        """Optimizes the focal point of the thermal lenses by minimizing a figure of
        merit as defined by the `opt_tl` detector.

        Parameters
        ----------
        accuracy : float, optional
            Accuracy to which to tune the focal length, in meters.
        """

        cp_old = accuracy + 1
        cp_old_w = accuracy + 1
        cp_new = np.abs(self.model.CPN_TL.f.eval())
        cp_new_w = np.abs(self.model.CPW_TL.f.eval())

        while np.abs(cp_new - cp_old) > accuracy:
            if verbose or self.verbose:
                print("ΔCPN_TL.f = ", np.abs(cp_new - cp_old))
                print("ΔCPW_TL.f = ", np.abs(cp_new_w - cp_old_w))

            # keep the old value
            cp_old = np.abs(self.model.CPN_TL.f.eval())
            cp_old_w = np.abs(self.model.CPW_TL.f.eval())

            # optimize and run the locks
            self.model.run(Minimize("opt_tl", ["f_CPN_TL", "f_CPW_TL"]))
            self.optimize_demodulation_phase()
            self.optimize_lock_gains()
            self.model.run(RunLocks(method="newton"))

            # keep the new value
            cp_new = np.abs(self.model.CPN_TL.f.eval())
            cp_new_w = np.abs(self.model.CPW_TL.f.eval())

    def get_DARM(self, axis=[0.5, 1000, 200]):
        kat = self.model.deepcopy()

        kat.parse(
            """
        fsig(1)

        # apply a signal to the end mirrors
        sgen sigQ NE.mech.F_z phase=180
        sgen sigI WE.mech.F_z

        # read the output after the SRC
        pd2 darm SRAR.p2.o f1=eom56.f phase1=B1p_56.phase f2=fsig.f phase2=none
        """
        )

        return kat.run(Xaxis(kat.fsig.f, "log", *axis))

    def plot_DARM(self, axis=[0.5, 1000, 200]):
        self.get_DARM(axis).plot(["darm"], log=True)

    # can be repeated
    # TODO: convert to utility?
    def get_QNLS(self, axis=[5, 5000, 100]):
        # allows for repetition
        kat = self.model.deepcopy()

        kat.parse(
            """#kat
            # Differentially modulate the arm lengths
            fsig(1)
            sgen darmx LN.h
            sgen darmy LW.h phase=180

            # Output the full quantum noise limited sensitivity
            qnoised NSR_with_RP B1.p1.i nsr=True

            # Output just the shot noise limited sensitivity
            qshot NSR_without_RP B1.p1.i nsr=True
        """
        )

        return kat.run(f'xaxis(darmx.f, "log", {axis[0]}, {axis[1]}, {axis[2]})')

    def plot_QNLS(self, axis=[5, 5000, 400]):
        out = self.get_QNLS(axis)
        out.plot(["NSR_with_RP", "NSR_without_RP"], log=True, separate=False)

    def print_thermal_values(self):
        # TODO: generate from THERMAL_STATES
        return NumberTable(
            [
                [self.model.PR.Rc[0]],
                [self.model.PR.Rc[1]],
                [self.model.SR.Rc[0]],
                [self.model.SR.Rc[1]],
                [self.model.f_CPN_TL.value.value],
                [self.model.f_CPW_TL.value.value],
            ],
            colnames=["Thermal Parameter", "Value"],
            rownames=["PR.Rcx", "PR.Rcy", "SR.Rcx", "SR.Rcy", "f_CPN_TL", "f_CPW_TL"],
            numfmt="{:11.2f}",
        )

    def plot_error_signals(self):
        for lock in self.model.locks:
            self.dof_plot(
                lock.feedback.name.split(".")[0], lock.error_signal.name, logy=False
            )

    def print_lengths(self):
        f6 = float(self.model.eom6.f.value)
        f8 = float(self.model.eom8.f.value)
        f56 = float(self.model.eom56.f.value)

        # TODO: use table generator
        print(
            f"""┌─────────────────────────────────────────────────┐
│- Arm lengths [m]:                               │
│  LN   = {self.model.elements["LN"].L.value:<11.4f} LW = {self.model.elements["LW"].L.value:<11.4f}            │
├─────────────────────────────────────────────────┤
│- Michelson and recycling lengths [m]:           │
│  ln   = {float(self.model.ln.value):<11.4f} lw       = {float(self.model.lw.value):<11.4f}      │
│  lpr  = {float(self.model.lpr.value):<11.4f} lsr      = {float(self.model.lsrbs.value):<11.4f}      │
│  lMI  = {float(self.model.lMI.value):<11.4f} lSchnupp = {float(self.model.lSchnupp.value):<11.4f}      │
│  lPRC = {float(self.model.lPRC.value):<11.4f} lSRC     = {float(self.model.lSRC.value):<11.4f}      │
├─────────────────────────────────────────────────┤
│- Associated cavity frequencies [Hz]:            │
│  fsrN   = {float(self.model.fsrN.value):<11.2f} fsrW   = {float(self.model.fsrW.value):<11.2f}      │
│  fsrPRC = {float(self.model.fsrPRC.value):<11.2f} fsrSRC = {float(self.model.fsrSRC.value):<11.2f}      │
│                                                 │
│- Modulation sideband frequencies [MHz]:         │
│  f6     = {f6/1e6:<12.6f} f8     = {f8/1e6:<12.6f}    │
│  f56     = {f56/1e6:<12.6f}                         │
├─────────────────────────────────────────────────┤
│- Check frequency match [MHz]:                   │
│  125.5*fsrN-300 = {(125.5*float(self.model.fsrN.value)-300)/1e6:<8.6f}                      │
│  0.5*fsrPRC     = {0.5*float(self.model.fsrPRC.value)/1e6:<8.6f}                      │
│  0.5*fsrSRC     = {0.5*float(self.model.fsrSRC.value)/1e6:<8.6f}                      │
│  9*f6           = {9*f6/1e6:<8.6f}                     │
└─────────────────────────────────────────────────┘"""
        )

    # zero dofs into phi
    def zero_dofs(self, dofs=None):
        """This function will move the current DoF DC values into the phi parameter of
        the driven component before resetting the DoF DC value to zero.

        Parameters
        ----------
        dofs : list or str, optional
            List of dofs to zero. By default, will zero all dofs found in the model.
        """

        # allow a list of dofs to be passed
        if dofs is None:
            dofs = self.get_dofs()

        # make sure it is
        if type(dofs) is not list:
            dofs = [dofs]

        for dof in dofs:
            # if it isn't a component, get it from the model
            if type(dof) is str:
                dof = self.model.get(dof)

            # move each dof value into phi with the appropriate sign
            for drive, amp in zip(dof.drives, dof.amplitudes):
                component = drive.name.split(".")[0]
                self.model.get(component).phi += dof.DC * amp

            # zero the dof value
            dof.DC = 0

    # TODO: move to Finesse 3 model?
    def get_dofs(self):
        return list(filter(lambda c: type(c) is DegreeOfFreedom, self.model.components))

    # TODO: could be moved the Finesse 3?
    # TODO: rename to get_dofs_by_optic()?
    def get_dofs_by_component(self):
        """Returns a dictionary, keyed by component name, with a list of dof/amp pairs
        driving each component."""
        dofs_by_component = {}

        dofs = self.get_dofs()
        for dof in dofs:
            for drive, amp in zip(dof.drives, dof.amplitudes):
                component = drive.name.split(".")[0]
                if component not in dofs_by_component.keys():
                    dofs_by_component[component] = []

                dofs_by_component[component].append((dof.name, amp))

        return dofs_by_component

    # TODO: move to Finesse 3?
    def get_tunings(self):
        """Sums together current phi position and all dof contributions.

        Returns dict of float, keyed by component name.
        """
        tunings = {}

        for component, pairs in self.get_dofs_by_component().items():
            phi = self.model.get(f"{component}.phi")
            tunings[component] = phi + sum(
                [self.model.get(dof).DC.value * amp for dof, amp in pairs]
            )

        return tunings

    # TODO: should be able to extract from model
    def print_tunings(self):
        data = [["Optic", "Tuning (deg)"]]
        for mirror, tuning in self.get_tunings().items():
            data.append([mirror, f"{tuning:15.6g}"])
        return Table(data, alignment=["left", "right"])
