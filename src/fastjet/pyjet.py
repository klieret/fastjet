import awkward as ak

import fastjet._ext  # noqa: F401, E402
from fastjet.version import __version__  # noqa: E402

__all__ = ("__version__",)


class AwkwardClusterSequence:
    def __init__(self, data, jetdef):
        self.jetdef = jetdef
        inps, inpf = self.swig_to_params(self.jetdef)
        container, length, data = ak.to_buffers(data)
        # offsets = data["part0-node0-offsets"]
        px = data["part0-node1-data"]
        py = data["part0-node2-data"]
        pz = data["part0-node3-data"]
        E = data["part0-node4-data"]
        results = fastjet._ext.interface(px, py, pz, E, inps, inpf)
        self.inclusive_jets = self.construct_awkward_array(results)

    def swig_to_params(self, jetdef):
        params = jetdef.description().split()
        if params[0] == "e+e-":
            algor = params[0]
            Rv = float(params[7])  # e+e- generalised
        if params[0] == "e+e-" and params[2] == "(Durham)":
            algor = "Durham"  # e+e- durham
            Rv = 0
        if params[2] == "generalised":
            Rv = params[8]
            algor = "genkt"  # genralised kt
        else:
            algor = params[2]
            Rv = float(params[7])
        inps = {"algor": algor}  # kt or antikt
        inpf = {"R": Rv}
        return inps, inpf

    def construct_awkward_array(self, results):
        self.form = """ {
    "class": "RecordArray",
    "contents": {
        "phi": {
            "class": "NumpyArray",
            "itemsize": 8,
            "format": "d",
            "primitive": "float64",
            "form_key": "node1"
        },
        "rap": {
            "class": "NumpyArray",
            "itemsize": 8,
            "format": "d",
            "primitive": "float64",
            "form_key": "node2"
        },
        "pt": {
            "class": "NumpyArray",
            "itemsize": 8,
            "format": "d",
            "primitive": "float64",
            "form_key": "node3"
        }
    },
    "parameters": {
        "__record__": "Momentum4D"
    },
    "form_key": "node0"
}
"""
        size = len(results["part0-node1-data"])
        out = ak.from_buffers(self.form, size, results)
        return out