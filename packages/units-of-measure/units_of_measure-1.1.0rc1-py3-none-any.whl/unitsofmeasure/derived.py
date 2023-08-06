"""SI Derived Units

The symbol of unit ohm is Ω (Unicode Ohm Sign).
You can map this to other identifiers by assignment (e.g. `ohm = Ω`).

The symbol of unit degree Celsius is °C, but that is not a valid Python identifier.
Therefore it is mapped to degC.

The symbol of quantity plane angle is θ (Unicode Greek Small Letter Theta).
The symbol of quantity solid angle is Ω (Unicode Greek Capital Letter Omega).
The symbol of quantity magnetic flux is Φ (Unicode Greek Capital Letter Phi).
"""
from unitsofmeasure import base, Dimension, Unit

rad  = Unit("rad", "radian", Dimension(symbol="θ", name="plane angle"))
sr   = Unit("sr", "steradian", Dimension(symbol="Ω", name="solid angle"))
Hz   = Unit("Hz", "hertz", Dimension(s=-1, symbol="f", name="frequency"))
N    = Unit("N", "newton", Dimension(kg=1, m=1, s=-2, symbol="F", name="force"))
Pa   = Unit("Pa", "pascal", Dimension(kg=1, m=-1, s=-2, symbol="p", name="pressure"))
J    = Unit("J", "joule", Dimension(kg=1, m=2, s=-2, symbol="E", name="energy"))
W    = Unit("W", "watt", Dimension(kg=1, m=2, s=-3, symbol="P", name="power"))
C    = Unit("C", "coulomb", Dimension(A=1, s=1, symbol="q", name="electric charge"))
V    = Unit("V", "volt", Dimension(kg=1, m=2, s=-3, A=-1, symbol="V", name="voltage")) # electric potential difference
F    = Unit("F", "farad", Dimension(kg=-1, m=-2, s=4, A=2, symbol="C", name="capacitance"))
Ω    = Unit("Ω", "ohm", Dimension(kg=1, m=2, s=-3, A=-2, symbol="R", name="electric resistance"))
S    = Unit("S", "siemens", Dimension(kg=-1, m=-2, s=3, A=2, symbol="G", name="electric conductance"))
Wb   = Unit("Wb", "weber", Dimension(kg=1, m=2, s=-2, A=-1, symbol="Φ", name="magnetic flux"))
T    = Unit("T", "tesla", Dimension(kg=1, s=-2, A=-1, symbol="B", name="magnetic flux density"))
H    = Unit("H", "henry", Dimension(kg=1, m=2, s=-2, A=-2, symbol="L", name="inductance"))
degC = Unit("°C", "degree Celsius", base.K.dimension) # Celsius temperature
lm   = Unit("lm", "lumen", Dimension(cd=1, symbol="Φv", name="luminous flux"))
lx   = Unit("lx", "lux", Dimension(cd=1, m=-2, symbol="Ev", name="illuminance"))
Bq   = Unit("Bq", "becquerel", Dimension(s=-1, symbol="A", name="radioactivity")) # activity referred to a radionuclide
Gy   = Unit("Gy", "gray", Dimension(m=2, s=-2, symbol="D", name="absorbed dose"))
Sv   = Unit("Sv", "sievert", Dimension(m=2, s=-2, symbol="H", name="equivalent dose"))
kat  = Unit("kat", "katal", Dimension(mol=1, s=-1, name="catalytic activity"))

# map symbols to units
units: dict[str, Unit] = {
    "rad":  rad,
    "sr":   sr,
    "Hz":   Hz,
    "N":    N,
    "Pa":   Pa,
    "J":    J,
    "W":    W,
    "C":    C,
    "V":    V,
    "F":    F,
    "Ω":    Ω,
    "S":    S,
    "Wb":   Wb,
    "T":    T,
    "H":    H,
    "degC": degC, # TODO map degC and/or °C?
    "lm":   lm,
    "lx":   lx,
    "Bq":   Bq,
    "Gy":   Gy,
    "Sv":   Sv,
    "kat":  kat
}
