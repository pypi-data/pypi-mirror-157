import importlib.resources

virgo_common_file = importlib.resources.read_text(
    "finesse_virgo.katscript", "00_virgo_common_file.kat"
)
additional_katscript = importlib.resources.read_text(
    "finesse_virgo.katscript", "01_additional_katscript.kat"
)

virgo_common_file_f2 = importlib.resources.read_text(
    "finesse_virgo.katscript.legacy", "virgo_common_file_f2.kat"
)

# TODO: this can be done better
files = ["00_virgo_common_file.kat", "01_additional_katscript.kat"]

__all__ = ("virgo_common_file", "additional_katscript", "virgo_common_file_f2")
