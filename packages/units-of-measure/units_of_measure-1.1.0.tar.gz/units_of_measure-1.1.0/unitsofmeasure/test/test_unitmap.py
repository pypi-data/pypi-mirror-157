"""Test UnitMap"""
import pytest
from unitsofmeasure import get_unit, map_to_unit, set_unit, Unit, UnitMap

def test() -> None:
    units = UnitMap()
    assert len(units.units) == 0
    assert units.value == Unit

    # Not all objects are weakly referencable, but class instances are.
    # https://docs.python.org/3/library/weakref.html
    class Measure:
        def __init__(self, value: object) -> None:
            self.value = value
    
    measure = Measure(8)
    b = Unit("b", "bit")

    with pytest.raises(KeyError):
        units.get(measure)
    
    units.set(measure, b)
    unit = units.get(measure)
    assert unit == b

def test_decorator() -> None:
    b = Unit("b", "bit")

    def f1() -> int:
        return 8
    
    with pytest.raises(KeyError):
        get_unit(f1)
    
    @map_to_unit(b)
    def f2() -> int:
        return 16

    unit = get_unit(f2)
    assert unit == b

def test_set_unit() -> None:
    class Measure:
        def __init__(self, value: object) -> None:
            self.value = value
    
    measure = Measure(8)
    B = Unit("B", "byte")
    set_unit(measure, B)
    unit = get_unit(measure)
    assert unit == B
