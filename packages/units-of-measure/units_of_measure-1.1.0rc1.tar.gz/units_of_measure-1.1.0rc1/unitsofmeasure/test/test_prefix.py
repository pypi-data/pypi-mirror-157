"""Test Prefix"""
import pytest
from unitsofmeasure import Prefix, PREFIX_1

@pytest.mark.parametrize(
    "base , exponent , symbol , name    , representation",[
    (  10 ,        0 , ""     , ""      , 'Prefix(base=10, exponent=0, symbol="", name="")'        ),
    (  10 ,        1 , "da"   , "deca"  , 'Prefix(base=10, exponent=1, symbol="da", name="deca")'  ), # SI prefixes (decimal)
    (  10 ,        2 , "h"    , "hecto" , 'Prefix(base=10, exponent=2, symbol="h", name="hecto")'  ),
    (  10 ,        3 , "k"    , "kilo"  , 'Prefix(base=10, exponent=3, symbol="k", name="kilo")'   ),
    (  10 ,        6 , "M"    , "mega"  , 'Prefix(base=10, exponent=6, symbol="M", name="mega")'   ),
    (  10 ,        9 , "G"    , "giga"  , 'Prefix(base=10, exponent=9, symbol="G", name="giga")'   ),
    (  10 ,       12 , "T"    , "tera"  , 'Prefix(base=10, exponent=12, symbol="T", name="tera")'  ),
    (  10 ,       15 , "P"    , "peta"  , 'Prefix(base=10, exponent=15, symbol="P", name="peta")'  ),
    (  10 ,       18 , "E"    , "exa"   , 'Prefix(base=10, exponent=18, symbol="E", name="exa")'   ),
    (  10 ,       21 , "Z"    , "zetta" , 'Prefix(base=10, exponent=21, symbol="Z", name="zetta")' ),
    (  10 ,       24 , "Y"    , "yotta" , 'Prefix(base=10, exponent=24, symbol="Y", name="yotta")' ),
    (  10 ,       -1 , "d"    , "deci"  , 'Prefix(base=10, exponent=-1, symbol="d", name="deci")'  ),
    (  10 ,       -2 , "c"    , "centi" , 'Prefix(base=10, exponent=-2, symbol="c", name="centi")' ),
    (  10 ,       -3 , "m"    , "milli" , 'Prefix(base=10, exponent=-3, symbol="m", name="milli")' ),
    (  10 ,       -6 , "µ"    , "micro" , 'Prefix(base=10, exponent=-6, symbol="µ", name="micro")' ),
    (  10 ,       -9 , "n"    , "nano"  , 'Prefix(base=10, exponent=-9, symbol="n", name="nano")'  ),
    (  10 ,      -12 , "p"    , "pico"  , 'Prefix(base=10, exponent=-12, symbol="p", name="pico")' ),
    (  10 ,      -15 , "f"    , "femto" , 'Prefix(base=10, exponent=-15, symbol="f", name="femto")'),
    (  10 ,      -18 , "a"    , "atto"  , 'Prefix(base=10, exponent=-18, symbol="a", name="atto")' ),
    (  10 ,      -21 , "z"    , "zepto" , 'Prefix(base=10, exponent=-21, symbol="z", name="zepto")'),
    (  10 ,      -24 , "y"    , "yocto" , 'Prefix(base=10, exponent=-24, symbol="y", name="yocto")')
])
def test(base: int, exponent: int, symbol: str, name: str, representation: str) -> None:
    prefix = Prefix(base, exponent, symbol, name)
    assert prefix.base     == base
    assert prefix.exponent == exponent
    assert prefix.symbol   == symbol
    assert prefix.name     == name

    # test equality
    other = Prefix(base, exponent)
    assert id(prefix) != id(other)
    assert prefix == other

    # test string
    assert str(prefix) == symbol

    # test representation
    assert repr(prefix) == representation

@pytest.mark.parametrize(
    "base , exception",[
    ( 1   , ValueError),
    ( 0   , ValueError),
    (-1   , ValueError),
    ( 0.5 , TypeError ),
    ("10" , TypeError )
])
def test_base(base: int, exception: Exception) -> None:
    with pytest.raises(exception, match="^The base must be an integer greater than 1.$"):
        Prefix(base, 1)

@pytest.mark.parametrize(
    "exponent , exception",[
    (     0.5 , TypeError),
    (     "1" , TypeError)
])
def test_exponent(exponent: int, exception: Exception) -> None:
    with pytest.raises(exception, match="^The exponent must be an integer.$"):
        Prefix(10, exponent)

@pytest.mark.parametrize(
    "base1 , exponent1 , base2 , exponent2 , equal_to",[
    (    2 ,         1 ,     2 ,         1 , True),
    (   10 ,         1 ,    10 ,         1 , True),
    (    2 ,         0 ,    10 ,         0 , True)
])
def test_eq(base1: int, exponent1: int, base2: int, exponent2: int, equal_to: bool) -> None:
    p1 = Prefix(base1, exponent1)
    p2 = Prefix(base2, exponent2)
    assert (p1 == p2) == equal_to

@pytest.mark.parametrize(
    "base1 , exponent1 , base2 , exponent2 , less_than",[
    (    2 ,         1 ,     2 ,         2 , True),
    (   10 ,         1 ,    10 ,         2 , True),
    (   10 ,         3 ,     2 ,        10 , True)
])
def test_lt(base1: int, exponent1: int, base2: int, exponent2: int, less_than: bool) -> None:
    p1 = Prefix(base1, exponent1)
    p2 = Prefix(base2, exponent2)
    assert (p1 < p2) == less_than

@pytest.mark.parametrize(
    "base1 , exponent1 , base2 , exponent2 , greater_than",[
    (    2 ,         2 ,     2 ,         1 , True),
    (   10 ,         2 ,    10 ,         1 , True),
    (    2 ,        10 ,    10 ,         3 , True)
])
def test_gt(base1: int, exponent1: int, base2: int, exponent2: int, greater_than: bool) -> None:
    p1 = Prefix(base1, exponent1)
    p2 = Prefix(base2, exponent2)
    assert (p1 > p2) == greater_than

def test_prefix_1() -> None:
    assert PREFIX_1.base        == 10
    assert PREFIX_1.exponent    == 0
    assert len(PREFIX_1.symbol) == 0
    assert len(PREFIX_1.name)   == 0
