==========
 Validino
==========

Validino is a simple validation/data-conversion library for Python
with a functional flavor.  

Raison D'etre
=============

Validino is very much indebted to Ian Bicking's FormEncode, but
includes only those features I personally needed and skipped the
rest. It dispenses with that library's declarative DSL, which I found
I kept stumbling over, and only offers one-way data conversion, while
FormEncode supports two-way conversion (which I've never needed).  

While getting rid of the declarative style simplified the library code
and, to my mind, is more transparent, it does make code using validino
somewhat more verbose than the FormEncode equivalent.  

In my opinion, FormEncode gets exactly right that validation and data
conversion should be one step, and that validation should be separated
from models and views (at the library level -- applications will
obviously bring them together, but each application will have
different needs for doing so).










