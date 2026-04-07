"""Smoke test — verify all packages are importable."""


def test_packages_importable() -> None:
    import yaga_contracts
    import yaga_persistence
    import yaga_runtime
    import yaga_runtime_core

    assert yaga_contracts is not None
    assert yaga_persistence is not None
    assert yaga_runtime_core is not None
    assert yaga_runtime is not None
