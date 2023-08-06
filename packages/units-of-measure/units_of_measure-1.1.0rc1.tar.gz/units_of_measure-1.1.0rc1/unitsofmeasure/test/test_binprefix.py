from unitsofmeasure import binprefix

def test():
    items = binprefix.prefixes.items()
    assert len(items) == 8 # there are 8 binary prefixes

    for (key, prefix) in items:
        print(key, prefix)
        assert key == prefix.symbol
        assert prefix.base == 2
        assert prefix.exponent >= 10
        assert prefix.exponent <= 80
        assert len(prefix.symbol) > 0
        assert len(prefix.name) > 0

def test_order():
    prefixes = [
        binprefix.Ki,
        binprefix.Mi,
        binprefix.Gi,
        binprefix.Ti,
        binprefix.Pi,
        binprefix.Ei,
        binprefix.Zi,
        binprefix.Yi
    ]
    
    prev = None
    for prefix in prefixes:
        if prev is not None:
            print(prev, "<", prefix)
            assert prev < prefix
            assert prefix > prev
        prev = prefix
