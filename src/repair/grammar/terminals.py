import math
from functools import partial
from typing import Callable, Type
import random

from repair.approach.trace import TraceSuite


class GrammarTerminal:
    def __init__(self, name: str,
                 value_fn: Callable,
                 return_type: Type,
                 display_name: str = None):
        self.name = name
        self.value_fn = value_fn  # Callable producing terminal value
        self.return_type = return_type
        self.display_name = display_name or name

    @staticmethod
    def create_terminals(trace_suite):
        # prev(_var) uses the underscore to avoid clashing with proper var names (of float type)
        return [GrammarTerminal(var_name, lambda: f"_{var_name}", str, display_name=var_name)
                for var_name in trace_suite.variable_names]

    @staticmethod
    def create_ephemerals(trace_suite, numbers_factor):
        # Ephemeral numeric terminals (randomly sampled each individual)
        # dur
        min_time = math.floor(trace_suite.variables[TraceSuite.TIME_VAR]["min"])
        max_time = math.ceil(trace_suite.variables[TraceSuite.TIME_VAR]["max"])
        max_dur = max_time - min_time
        ephemerals = [(GrammarTerminal("rand_dur", partial(random.randint, 0, max_dur), int,
                                       display_name=f"rand_dur(0, {max_dur})"))]
        # vars: collect min and max per unit
        units = {}
        for var_name, var in trace_suite.variables.items():
            unit = var["unit"]
            if var_name == TraceSuite.TIME_VAR or unit not in units:
                units[unit] = {"min": var["min"], "max": var["max"]}
                continue
            if var["min"] < units[unit]["min"]:
                units[unit]["min"] = var["min"]
            if var["max"] > units[unit]["max"]:
                units[unit]["max"] = var["max"]
        # vars: create randoms per unit
        for unit, bounds in units.items():
            window_orig = bounds["max"] - bounds["min"]
            window_scaled = window_orig * numbers_factor
            offset = (window_scaled - window_orig) / 2
            min_unit = bounds["min"] - offset
            if bounds["min"] > 0: # don't make it negative
                min_unit = max(min_unit, 0.0)
            max_unit = bounds["max"] + offset
            ephemerals.append(GrammarTerminal(f"rand_float_{unit}", partial(random.uniform, min_unit, max_unit),
                                              float, display_name=f"rand_float_{unit}({min_unit}, {max_unit})"))

        return ephemerals
