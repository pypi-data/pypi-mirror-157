"""Test Unit"""
import pytest
from fractions import Fraction
from unitsofmeasure import decprefix, Dimension, Prefix, PREFIX_1, SCALAR, Unit, UNIT_1

@pytest.mark.parametrize(
    "symbol , name       , dimension        , prefix      , factor          , representation",[
    ("%"    , "percent"  , Dimension()      , PREFIX_1    , Fraction(1,100) , # scalar
        'Unit(symbol="%", name="percent", dimension=Dimension(kg=0, m=0, s=0, A=0, K=0, cd=0, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 100))'),
    ("kg"   , "kilogram" , Dimension(kg=1)  , decprefix.k , Unit.FRACTION_1 , # SI base units
        'Unit(symbol="kg", name="kilogram", dimension=Dimension(kg=1, m=0, s=0, A=0, K=0, cd=0, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=3, symbol="k", name="kilo"), factor=Fraction(1, 1))'),
    ("m"    , "metre"    , Dimension(m=1)   , PREFIX_1    , Unit.FRACTION_1 ,
        'Unit(symbol="m", name="metre", dimension=Dimension(kg=0, m=1, s=0, A=0, K=0, cd=0, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 1))'),
    ("s"    , "second"   , Dimension(s=1)   , PREFIX_1    , Unit.FRACTION_1 ,
        'Unit(symbol="s", name="second", dimension=Dimension(kg=0, m=0, s=1, A=0, K=0, cd=0, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 1))'),
    ("A"    , "ampere"   , Dimension(A=1)   , PREFIX_1    , Unit.FRACTION_1 ,
        'Unit(symbol="A", name="ampere", dimension=Dimension(kg=0, m=0, s=0, A=1, K=0, cd=0, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 1))'),
    ("K"    , "kelvin"   , Dimension(K=1)   , PREFIX_1    , Unit.FRACTION_1 ,
        'Unit(symbol="K", name="kelvin", dimension=Dimension(kg=0, m=0, s=0, A=0, K=1, cd=0, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 1))'),
    ("cd"   , "candela"  , Dimension(cd=1)  , PREFIX_1    , Unit.FRACTION_1 ,
        'Unit(symbol="cd", name="candela", dimension=Dimension(kg=0, m=0, s=0, A=0, K=0, cd=1, mol=0, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 1))'),
    ("mol"  , "mole"     , Dimension(mol=1) , PREFIX_1    , Unit.FRACTION_1 ,
        'Unit(symbol="mol", name="mole", dimension=Dimension(kg=0, m=0, s=0, A=0, K=0, cd=0, mol=1, symbol="", name=""), prefix=Prefix(base=10, exponent=0, symbol="", name=""), factor=Fraction(1, 1))')
])
def test(symbol: str, name: str, dimension: Dimension, prefix: Prefix, factor: Fraction, representation: str) -> None:
    unit = Unit(symbol, name, dimension, prefix, factor)
    assert unit.symbol    == symbol
    assert unit.name      == name
    assert unit.dimension == dimension
    assert unit.prefix    == prefix
    assert unit.factor    == factor

    # test equality
    other = Unit(symbol, name, dimension, prefix, factor)
    assert id(unit) != id(other)
    assert unit == other

    # test string
    assert str(unit) == symbol

    # test representation
    assert repr(unit) == representation

def test_unit_1() -> None:
    assert len(UNIT_1.symbol) == 0
    assert len(UNIT_1.name)   == 0
    assert UNIT_1.dimension   == SCALAR
    assert UNIT_1.prefix      == PREFIX_1
    assert UNIT_1.factor      == Unit.FRACTION_1
