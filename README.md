Universal conversion tool for pint.


```
# defaults to base units
$ unitcalc 2.2lb
0.9979032140000003 kilogram

$ unitcalc 50stones kg
317.514659 kilogram

$ unitcalc 50stones kg lb "newton/(ft/s^2)"
317.514659 kilogram
700.0000000000001 pound
96.7784680632 newton * second ** 2 / foot

$ unitcalc 1lightyear nm
9.460730472580798e+24 nanometer

$ unitcalc 7fortnights decades
0.02683093771389459 decade

$ unitcalc 99mi/sec fathom/month
229107717783.648 fathom / month

$ unitcalc 3.14radians/week degrees/ms
2.974681674455662e-07 degree / millisecond

$ unitcalc 0.2W eV/century
3.93934093536406e+27 electron_volt / century

$ unitcalc 0.2J/ns ton_TNT/month
125707.45697896747 ton_TNT / month

```

NOTE: https://pint.readthedocs.io/en/latest/pint-convert.html is better, you prob want that instead.
