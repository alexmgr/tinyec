# tinyec
A tiny library to perform arithmetic operations on elliptic curves in pure python. No dependencies.

**This is not a library suitable for production.** It is useful for security professionals to understand the inner workings of EC, and be able to play with pre-defined curves.

## installation
`pip install tinyec`

## usage
There are 2 main classes:
* Curve(), which describes an elliptic curve in a finite field
* Point(), which describes a point belonging to an EC

**Warning** Calculation on points outside the curve are allowed. They will only raise a warning.

### working on existing curves
Example use on the NIST routine samples => https://www.nsa.gov/ia/_files/nist-routines.pdf:
```python
>>> import tinyec.ec as ec
>>> import tinyec.registry as reg
>>> c = reg.get_curve("secp192r1")
>>> s = ec.Point(c, 0xd458e7d127ae671b0c330266d246769353a012073e97acf8, 0x325930500d851f336bddc050cf7fb11b5673a1645086df3b)
>>> t = ec.Point(c, 0xf22c4395213e9ebe67ddecdd87fdbd01be16fb059b9753a4, 0x264424096af2b3597796db48f8dfb41fa9cecc97691a9c79)
>>> r = s + t
>>> r
(1787070900316344022479363585363935252075532448940096815760, 1583034776780933252095415958625802984888372377603917916747) on secp192r1 => y^2 = x^3 + 6277101735386680763835789423207666416083908700390324961276x + 2455155546008943817740293915197451784769108058161191238065 
(mod 6277101735386680763835789423207666416083908700390324961279)
>>> hex(r.x)
'0x48e1e4096b9b8e5ca9d0f1f077b8abf58e843894de4d0290L'
>>> hex(r.y)
'0x408fa77c797cd7dbfb16aa48a3648d3d63c94117d7b6aa4bL'
>>> r = s - t
>>> r
(6193438478050209507979672067809269724375390027440522152494, 226636415264149817017346905052752138772359775362461041003) on secp192r1 => y^2 = x^3 + 6277101735386680763835789423207666416083908700390324961276x + 2455155546008943817740293915197451784769108058161191238065 (
mod 6277101735386680763835789423207666416083908700390324961279)
>>> hex(r.x)
'0xfc9683cc5abfb4fe0cc8cc3bc9f61eabc4688f11e9f64a2eL'
>>> hex(r.y)
'0x93e31d00fb78269732b1bd2a73c23cdd31745d0523d816bL'
>>> r = 2 * s
>>> r
(1195895923065450997501505402941681398272052708885411031394, 340030206158745947396451508065335698335058477174385838543) on secp192r1 => y^2 = x^3 + 6277101735386680763835789423207666416083908700390324961276x + 2455155546008943817740293915197451784769108058161191238065 (
mod 6277101735386680763835789423207666416083908700390324961279)
>>> hex(r.x)
'0x30c5bc6b8c7da25354b373dc14dd8a0eba42d25a3f6e6962L'
>>> hex(r.y)
'0xdde14bc4249a721c407aedbf011e2ddbbcb2968c9d889cfL'
>>> d = 0xa78a236d60baec0c5dd41b33a542463a8255391af64c74ee
>>> r = d * s
>>> hex(r.x)
'0x1faee4205a4f669d2d0a8f25e3bcec9a62a6952965bf6d31L'
>>> hex(r.y)
'0x5ff2cdfa508a2581892367087c696f179e7a4d7e8260fb06L'
>>> e = 0xc4be3d53ec3089e71e4de8ceab7cce889bc393cd85b972bc
>>> r = d * s + e * t
>>> r
(39786866609245082371772779541859439402855864496422607838, 547967566579883709478937502153554894699060378424501614148) on secp192r1 => y^2 = x^3 + 6277101735386680763835789423207666416083908700390324961276x + 2455155546008943817740293915197451784769108058161191238065 (mo
d 6277101735386680763835789423207666416083908700390324961279)
>>> hex(r.x)
'0x19f64eed8fa9b72b7dfea82c17c9bfa60ecb9e1778b5bdeL'
>>> hex(r.y)
'0x16590c5fcd8655fa4ced33fb800e2a7e3c61f35d83503644L'
```

### working on custom curves
If needed, you can also work on your own curves. Here we take a a prime field 97, with a generator point (1, 2), an order 5 and a cofactor of 1:
```python
>>> import tinyec.ec as ec
>>> field = ec.SubGroup(97, (1, 2), 5, 1)
>>> curve = ec.Curve(2, 3, field)
tinyec/ec.py:115: UserWarning: Point (1, 2) is not on curve "undefined" => y^2 = x^3 + 2x + 3 (mod 97)
  warnings.warn("Point (%d, %d) is not on curve %s" % (self.x, self.y, self.curve))
>>> # Warning is generated because the generator point does not belong to the curve
>>> p1 = ec.Point(curve, -5, 3)
>>> p1.on_curve
False
>>> p2 = ec.Point(curve, 22, 5)
>>> p2.on_curve
True
>>> print(p1 + p2)
(18, 42) off "undefined" => y^2 = x^3 + 2x + 3 (mod 97)
```
