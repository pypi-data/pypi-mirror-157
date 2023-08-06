"""SI Base Units"""
from unitsofmeasure import decprefix, Dimension, Unit

kg  = Unit("kg", "kilogram", Dimension(kg=1, symbol="m", name="mass"), decprefix.k)
m   = Unit("m", "metre", Dimension(m=1, symbol="l", name="length"))
s   = Unit("s", "second", Dimension(s=1, symbol="t", name="time"))
A   = Unit("A", "ampere", Dimension(A=1, symbol="I", name="electric current"))
K   = Unit("K", "kelvin", Dimension(K=1, symbol="T", name="thermodynamic temperature"))
cd  = Unit("cd", "candela", Dimension(cd=1, symbol="Iv", name="luminous intensity"))
mol = Unit("mol", "mole", Dimension(mol=1, symbol="n", name="amount of substance"))

# map symbols to units
units: dict[str, Unit] = {
    "kg":  kg,
    "m":   m,
    "s":   s,
    "A":   A,
    "K":   K,
    "cd":  cd,
    "mol": mol
}
