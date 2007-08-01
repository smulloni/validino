==========
 Validino
==========

Validino is a simple validation/data-conversion library for Python
with a functional flavor.  

Comparison with FormEncode
==========================

Validino is very much indebted to Ian Bicking's FormEncode; indeed, it
is essentially a rewrite of a subset of it that includes only those
features I personally needed, skipping those I either didn't feel the
need for, or felt uncomfortable with. In particular, validino
dispenses with FormEncode's declarative DSL, which I found I kept
stumbling over, and only offers one-way data conversion, while
FormEncode supports two-way conversion (which I've never needed).

In my opinion, FormEncode gets exactly right that validation and data
conversion should be one step, and that validation should be separated
from models and views (at the library level -- applications will
obviously bring them together, but each application will have
different needs for doing so).

FormEncode's declarative style is also a good idea at origin.  But in
using it I often had the feeling that FormEncode's very success had
made its DSL overgrown and unwieldy; I kept running into edge cases
where I was unsure of exactly how to ask FormEncode to do what I
wanted, while the corresponding procedural code would be easy to
write, even if somewhat verbose, and kept having to refer to the
source code to figure out what would really happen when I subclassed a
validator.  The problem here is of course as such if not more with the
bone-like density of my noggin as with FormEncode, but then one point
of a DSL is to make it easier to be used by idiots, and for this idiot
it had begun to fail in that purpose.  My frustration reached a point
where, the next time I had a project that invited the use of
FormEncode, I decided to write a replacement and feel the breeze in my
coding hair rather than buckle down to dutifully untie my FormEncode
knots; the subset I needed was small enough that it only took a few
hours.  (Python encourages reuse through emulation, and I don't
apologize for it.)

The guiding premise was that a validator could be any simple conversion
function -- it would not need to be wrapped in a special Validator
class -- which would return a converted value, or raise an Invalid
exception.  (FormEncode, in addition to passing around values, passes
around a "state" variable; validino doesn't do this.)  To get complex
behavior, you can compose multiple validators::

  from validino import *
  my_validator=compose(strip, either(empty(), 
                                     clamp_length(min=5, max=10)))


















