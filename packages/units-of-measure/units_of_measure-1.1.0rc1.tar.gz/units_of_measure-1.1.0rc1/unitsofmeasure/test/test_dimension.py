"""Test Dimension"""
import pytest
from unitsofmeasure import Dimension, SCALAR

@pytest.mark.parametrize(
    "dimension, kg, m, s, A, K, cd, mol, symbol, name, representation",[
    (Dimension(), 0, 0, 0, 0, 0, 0, 0, "", "",
        'Dimension(kg=0, m=0, s=0, A=0, K=0, cd=0, mol=0, symbol="", name="")'), # scalar
    (Dimension(kg=1, symbol="m", name="mass"), 1, 0, 0, 0, 0, 0, 0, "m", "mass",
        'Dimension(kg=1, m=0, s=0, A=0, K=0, cd=0, mol=0, symbol="m", name="mass")'), # SI base units
    (Dimension(m=1, symbol="l", name="length"), 0, 1, 0, 0, 0, 0, 0, "l", "length",
        'Dimension(kg=0, m=1, s=0, A=0, K=0, cd=0, mol=0, symbol="l", name="length")'),
    (Dimension(s=1, symbol="t", name="time"), 0, 0, 1, 0, 0, 0, 0, "t", "time",
        'Dimension(kg=0, m=0, s=1, A=0, K=0, cd=0, mol=0, symbol="t", name="time")'),
    (Dimension(A=1, symbol="I", name="electric current"), 0, 0, 0, 1, 0, 0, 0, "I", "electric current",
        'Dimension(kg=0, m=0, s=0, A=1, K=0, cd=0, mol=0, symbol="I", name="electric current")'),
    (Dimension(K=1, symbol="T", name="thermodynamic temperature"), 0, 0, 0, 0, 1, 0, 0, "T", "thermodynamic temperature",
        'Dimension(kg=0, m=0, s=0, A=0, K=1, cd=0, mol=0, symbol="T", name="thermodynamic temperature")'),
    (Dimension(cd=1, symbol="Iv", name="luminous intensity"), 0, 0, 0, 0, 0, 1, 0, "Iv", "luminous intensity",
        'Dimension(kg=0, m=0, s=0, A=0, K=0, cd=1, mol=0, symbol="Iv", name="luminous intensity")'),
    (Dimension(mol=1, symbol="n", name="amount of substance"), 0, 0, 0, 0, 0, 0, 1, "n", "amount of substance",
        'Dimension(kg=0, m=0, s=0, A=0, K=0, cd=0, mol=1, symbol="n", name="amount of substance")')
])
def test(dimension: Dimension, kg: int, m: int, s: int, A: int, K: int, cd: int, mol: int, symbol: str, name: str, representation: str) -> None:
    assert dimension.kg == kg
    assert dimension.m == m
    assert dimension.s == s
    assert dimension.A == A
    assert dimension.K == K
    assert dimension.cd == cd
    assert dimension.mol == mol
    assert dimension.symbol == symbol
    assert dimension.name == name

    # test equality
    other = Dimension(kg, m, s, A, K, cd, mol)
    assert id(dimension) != id(other)
    assert dimension == other

    # test string
    assert str(dimension) == symbol

    # test representation
    assert repr(dimension) == representation

@pytest.mark.parametrize(
    "kg  , m   , s   , A   , K   , cd  , mol",[
    (0.5 , 0   , 0   , 0   , 0   , 0   , 0  ),
    (0   , 0.5 , 0   , 0   , 0   , 0   , 0  ),
    (0   , 0   , 0.5 , 0   , 0   , 0   , 0  ),
    (0   , 0   , 0   , 0.5 , 0   , 0   , 0  ),
    (0   , 0   , 0   , 0   , 0.5 , 0   , 0  ),
    (0   , 0   , 0   , 0   , 0   , 0.5 , 0  ),
    (0   , 0   , 0   , 0   , 0   , 0   , 0.5),
    ("1" , 0   , 0   , 0   , 0   , 0   , 0  ),
    (0   , "1" , 0   , 0   , 0   , 0   , 0  ),
    (0   , 0   , "1" , 0   , 0   , 0   , 0  ),
    (0   , 0   , 0   , "1" , 0   , 0   , 0  ),
    (0   , 0   , 0   , 0   , "1" , 0   , 0  ),
    (0   , 0   , 0   , 0   , 0   , "1" , 0  ),
    (0   , 0   , 0   , 0   , 0   , 0   , "1")
])
def test_exceptions(kg: int, m: int, s: int, A: int, K: int, cd: int, mol: int) -> None:
    with pytest.raises(TypeError, match="^The exponent must be an integer.$"):
        Dimension(kg, m, s, A, K, cd, mol)

def test_scalar() -> None:
    assert SCALAR.kg  == 0
    assert SCALAR.m   == 0
    assert SCALAR.s   == 0
    assert SCALAR.A   == 0
    assert SCALAR.K   == 0
    assert SCALAR.cd  == 0
    assert SCALAR.mol == 0
    assert len(SCALAR.symbol) == 0
    assert len(SCALAR.name) == 0
