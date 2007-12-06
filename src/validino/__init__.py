## Copyright (c) 2007 Jacob Smullyan <jsmullyan@gmail.com>
##
## Permission is hereby granted, free of charge, to any person
## obtaining a copy of this software and associated documentation
## files (the "Software"), to deal in the Software without
## restriction, including without limitation the rights to use,
## copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the
## Software is furnished to do so, subject to the following
## conditions:
##
## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
## OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
## HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
## WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
## OTHER DEALINGS IN THE SOFTWARE.

"""
A data conversion and validation package.

In typical use, you create a Schema with
various subvalidators.  For instance:
>>> import validino as V
>>> validators=dict(username=(V.strip,
...                           V.not_empty('Pledge enter a username'),
...                           V.clamp_length(max=20)),
...                 password=V.not_empty('Please enter a password'))
>>> s=V.Schema(validators)
>>> confirmed=s(dict(username='henry', password='dogwood'))
"""

from validino.base import *
from validino.extra import *
from validino.messages import *
from validino.field import *

__version__='0.2.2'
