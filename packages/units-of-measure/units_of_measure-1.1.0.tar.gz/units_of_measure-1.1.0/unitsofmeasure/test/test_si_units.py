"""Test SI Units"""
from unitsofmeasure import accepted, base, derived

def test() -> None:
    units = base.units | derived.units | accepted.units
    for (key, unit) in units.items():
        print(key, unit, unit.name)
        if (key == "degC"):
            assert unit.symbol == "°C"
        else:
            assert key == unit.symbol
