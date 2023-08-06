from unitsofmeasure import accepted, PREFIX_1, SCALAR, Unit

def test():
    items = accepted.units.items()
    assert len(items) == 7 # there are 7 implemented and accepted units

    for (key, unit) in items:
        print(key, unit, unit.name, unit.dimension.symbol, unit.dimension.name)
        assert key == unit.symbol
        assert len(unit.symbol) > 0
        assert len(unit.name) > 0
        assert unit.dimension != SCALAR
        assert len(unit.dimension.symbol) > 0
        assert len(unit.dimension.name) > 0
        assert unit.prefix == PREFIX_1
        assert unit.factor != Unit.FRACTION_1
