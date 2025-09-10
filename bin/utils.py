REQUIREMENTS = {
    "dummy": {"REQ": ("True", "lt(y, 1.0)")},
    "traces": {"REQ": ("and(eq(reset, 1.0), and(le(BL, ic), le(ic, TL)))", "eq(yout, ic)")},
    # "data/traces": ("True", "and(le(yout, TL), ge(yout, BL))"),
    "AFC": {
        "AFC29": (
            "and("
                "and(ge(Throttle, 0.0), lt(Throttle, 61.2)), and("
                "and(ge(Engine, 900.0), le(Engine, 1100.0)),"
                "and(ge(Time, 11.0),    le(Time, 50.0))))",
            "and(gt(Error, -0.007), lt(Error, 0.007))"
        ),
        "AFC33": (
            "and("
                "and(ge(Throttle, 61.2), lt(Throttle, 81.2)), and("
                "and(ge(Engine, 900.0), le(Engine, 1100.0)),"
                "and(ge(Time, 11.0),    le(Time, 50.0))))",
            "and(gt(Error, -0.007), lt(Error, 0.007))"
        )
    },
    "AT": {
        "AT1": (
            "and("
                "and(ge(Throttle, 0.0), le(Throttle, 100.0)), and("
                "and(ge(Brake, 0.0),    le(Brake, 325.0)),"
                "and(ge(Time, 0.0),     le(Time, 20.0))))",
            "lt(Speed, 115.0)"
        ),
        "AT2": (
            "and("
                "and(ge(Throttle, 0.0), le(Throttle, 100.0)), and("
                "and(ge(Brake, 0.0),    le(Brake, 325.0)),"
                "and(ge(Time, 0.0),     le(Time, 10.0))))",
            "lt(Engine, 4750.0)"
        )
    },
    "CC": {
        "CC1": (
            "and("
                "and(ge(Throttle, 0.0), le(Throttle, 1.0)), and("
                "and(ge(Brake, 0.0),    le(Brake, 1.0)),"
                "and(ge(Time, 0.0),     le(Time, 100.0))))",
            "le(sub(Position5, Position4), 40.0)"
        ),
        "CCX": (
            "and("
                "and(ge(Throttle, 0.0), le(Throttle, 1.0)), and("
                "and(ge(Brake, 0.0),    le(Brake, 1.0)),"
                "and(ge(Time, 0.0),     le(Time, 50.0))))",
            "and("
                "gt(sub(Position5, Position4), 7.5), and("
                "gt(sub(Position4, Position3), 7.5), and("
                "gt(sub(Position3, Position2), 7.5),"
                "gt(sub(Position2, Position1), 7.5))))"
        )
    },
    "EU": {
        "EU1": (
            "and("
                "and(ge(Vin_x, -0.5), le(Vin_x, 0.5)), and("
                "and(ge(Vin_y, -0.5), le(Vin_y, 0.5)),"
                "and(ge(Vin_z, -0.5), le(Vin_z, 0.5))))",
            "le(norm1, 0.01)"
        ),
        "EU2": (
            "and("
                "and(ge(Vin_x, -0.5), le(Vin_x, 0.5)), and("
                "and(ge(Vin_y, -0.5), le(Vin_y, 0.5)),"
                "and(ge(Vin_z, -0.5), le(Vin_z, 0.5))))",
            "le(norm2, 0.02)"
        ),
        "EU3": (
            "and("
                "and(ge(Vin_x, -0.5), le(Vin_x, 0.5)), and("
                "and(ge(Vin_y, -0.5), le(Vin_y, 0.5)),"
                "and(ge(Vin_z, -0.5), le(Vin_z, 0.5))))",
            "and("
                "le(sub(norm_Vin, norm_Vout), 0.01),"
                "ge(sub(norm_Vin, norm_Vout), -0.01))"
        ),
        "EU4": (
            "and("
                "and(ge(Vin_x, -0.5), le(Vin_x, 0.5)), and("
                "and(ge(Vin_y, -0.5), le(Vin_y, 0.5)),"
                "and(ge(Vin_z, -0.5), le(Vin_z, 0.5))))",
            "le(norm3, 0.01)"
        ),
        "EU5": (
            "and("
                "and(ge(Vin_x, -0.5), le(Vin_x, 0.5)), and("
                "and(ge(Vin_y, -0.5), le(Vin_y, 0.5)),"
                "and(ge(Vin_z, -0.5), le(Vin_z, 0.5))))",
            "and("
                "le(sub(det_R, 1.0), 0.01),"
                "ge(sub(det_R, 1.0), -0.01))"
        )
    },
    "NNP": {
        "NNP1": (
            "and("
                "and(ge(xIn, -2.0), le(xIn, 2.0)),"
                "and(ge(yIn, -2.0), le(yIn, 2.0)))",
            "le(zOut, 1.1)"
        ),
        "NNP2": (
            "and("
                "and(ge(xIn, -2.0), le(xIn, 2.0)),"
                "and(ge(yIn, -2.0), le(yIn, 2.0)))",
            "ge(zOut, -0.2)"
        ),
        "NNP3a": (
            "and("
                "and(ge(xIn, -2.0), le(xIn, 2.0)),"
                "and(ge(yIn, -2.0), le(yIn, 2.0)))",
            "and(ge(dzdx, -35.0), le(dzdx, 10.0))"
        ),
        "NNP3b": (
            "and("
                "and(ge(xIn, -2.0), le(xIn, 2.0)),"
                "and(ge(yIn, -2.0), le(yIn, 2.0)))",
            "and(ge(dzdy, -35.0), le(dzdy, 10.0))"
        ),
        "NNP4": (
            "and("
                "and(ge(xIn, -2.0), le(xIn, 2.0)),"
                "and(ge(yIn, -2.0), le(yIn, 2.0)))",
            "and("
                "le(sub(zOut, zOrig), 0.01),"
                "ge(sub(zOut, zOrig), -0.01))"
        )
    },
    "TUI": {
        "TU1": (
            "and("
                "and(ge(xin, -0.5), le(xin, 0.5)),"
                "and(ge(ic, -7.0),  le(ic, 7.0)))",
            "or("
                "eq(reset, 0.0),"
                "and("
                    "eq(reset, 1.0), and("
                    "le(sub(yout, ic), 0.001),"
                    "ge(sub(yout, ic), -0.001))))"
        ),
        "TU2": (
            "and("
                "and(ge(xin, -0.5), le(xin, 0.5)),"
                "and(ge(ic, -7.0), le(ic, 7.0)))",
            "and(le(yout, TL), ge(yout, BL))"
        )
    }
}

INPUT_VARIABLES = {
    "dummy":  {"x"},
    "traces": {"xin", "reset", "TL", "BL", "dT", "ic"},
    "AFC": {"Throttle", "Engine"},
    "AT":  {"Throttle", "Brake"},
    "CC":  {"Throttle", "Brake"},
    "EU":  {"Phi", "Theta", "Psi", "Vin_x", "Vin_y", "Vin_z"},
    "NNP": {"xIn", "yIn"},
    "TUI": {"xin", "reset", "TL", "BL", "dT", "ic"},
}
