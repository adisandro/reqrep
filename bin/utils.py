REQUIREMENTS = {
    "data/dummy": ("True", "lt(y, 1.0)"),
    "data/traces": ("and(eq(reset, 1.0), and(le(BL, ic), le(ic, TL)))", "eq(yout, ic)"),
    # "data/traces": ("True", "and(le(yout, TL), ge(yout, BL))"),
    "data/case_studies/AFC": (
        "and("
            "and(ge(Throttle, 0.0), lt(Throttle, 61.2)),"
            "and(ge(Engine, 900.0), le(Engine, 1100.0)))",
        "dur(11, 50, and(gt(Error, -0.007), lt(Error, 0.007)))"
    ),
    "data/case_studies/AT-AT1": (
        "and("
            "and(ge(Throttle, 50.0), le(Throttle, 100.0)),"
            "and(ge(Brake, 0.0),     le(Brake, 160.0)))",
        "dur(0, 20, lt(Speed, 120.0))"
    ),
    "data/case_studies/AT-AT2": (
        "and("
            "and(ge(Throttle, 5.0), le(Throttle, 100.0)),"
            "and(ge(Brake, 0.0),    le(Brake, 325.0)))",
        "dur(0, 10, lt(Engine, 4750.0))"
    ),
    "data/case_studies/CC": (
        "and("
            "and(ge(Throttle, 0.0), le(Throttle, 1.0)),"
            "and(ge(Brake, 0.0),    le(Brake, 1.0)))",
        "dur(0, 100, lt(sub(Position5, Position4), 40.0))"
        # "dur(0, 50, and("
        #   "gt(sub(Position5, Position4), 7.5), and("
        #   "gt(sub(Position4, Position3), 7.5), and("
        #   "gt(sub(Position3, Position2), 7.5),"
        #   "gt(sub(Position2, Position1), 7.5)))))"
    ),
    "data/case_studies/EU": (
        "and("
            "and(ge(Phi, 0.0),    lt(Phi, 6.28318)), and("
            "and(ge(Theta, 0.0),  lt(Theta, 3.14159)), and("
            "and(ge(Psi, 0.0),    lt(Psi, 6.28318)), and("
            "and(ge(Vin_x, -0.5), le(Vin_x, 0.5)), and("
            "and(ge(Vin_y, -0.5), le(Vin_y, 0.5)),"
            "and(ge(Vin_z, -0.5), le(Vin_z, 0.5)))))))",
        "and("
            "ge(sub(norm_Vin, norm_Vout), -0.01),"
            "le(sub(norm_Vin, norm_Vout),  0.01))"
        # "and("
        #   "ge(sub(det_R, 1.0), -0.01),"
        #   "le(sub(det_R, 1.0),  0.01))"
    ),
    "data/case_studies/NNP": (
        "and("
            "and(ge(xIn, -0.5), le(xIn, 0.5)),"
            "and(ge(yIn, -0.5), le(yIn, 0.5)))",
        "le(zOut, 1.1)"
        # "ge(zOut, -0.2)"
    ),
    "data/case_studies/TUI": (
        "and("
            "and(ge(xin, 0.0), lt(xin, 1.0)), and("
            "eq(reset, 0.0), and("
            "eq(TL, 10.0), and("
            "eq(BL, -10.0),"
            "eq(ic, 0.0)))))",
        "and(le(yout, TL), ge(yout, BL))"
    ),
}

INPUT_VARIABLES = {"data/dummy": {"x"},
                    "data/traces": {"xin", "reset", "TL", "BL", "dT", "ic"},
                    "data/case_studies/AFC": {"Throttle", "Engine"},
                    "data/case_studies/AT-AT1": {"Throttle", "Brake"},
                    "data/case_studies/AT-AT2": {"Throttle", "Brake"},
                    "data/case_studies/CC": {"Throttle", "Brake"},
                    "data/case_studies/EU": {"Phi", "Theta", "Psi", "Vin_x", "Vin_y", "Vin_z"},
                    "data/case_studies/NNP": {"xIn", "yIn"},
                    "data/case_studies/TUI": {"xin", "reset", "TL", "BL", "dT", "ic"},
                    }
