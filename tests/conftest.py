def pytest_terminal_summary(terminalreporter):
    """Report how close the rebuild is to the golden files, not only pass/fail."""
    import sys
    parity = sys.modules.get("tests.parity")
    if parity is None or not parity.STATS["floats"]:
        return
    s = parity.STATS
    terminalreporter.write_sep("-", "v3 parity (Tier A)")
    terminalreporter.write_line(
        f"{s['floats']} floats compared: {s['bit_identical']} bit-identical, "
        f"max relative difference {s['max_rel']:.3g} (tolerance {parity.REL_TOL:g}); "
        f"{s['strings']} display strings compared exactly")
