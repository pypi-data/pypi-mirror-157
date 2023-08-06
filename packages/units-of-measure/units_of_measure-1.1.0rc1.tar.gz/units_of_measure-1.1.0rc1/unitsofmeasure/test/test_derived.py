from unitsofmeasure import derived, PREFIX_1, Unit

def test():
    items = derived.units.items()
    assert len(items) == 22 # there are 22 derived units

    for (key, unit) in items:
        print(key, unit, unit.name, unit.dimension.symbol, unit.dimension.name)

        if (key == "degC"):
            assert unit.symbol == "°C"
        else:
            assert key == unit.symbol
        
        assert len(unit.symbol) > 0
        assert len(unit.name) > 0

        if (key == "kat"):
            assert len(unit.dimension.symbol) == 0
        else:
            assert len(unit.dimension.symbol) > 0
        
        assert len(unit.dimension.name) > 0
        assert unit.prefix == PREFIX_1
        assert unit.factor == Unit.FRACTION_1
