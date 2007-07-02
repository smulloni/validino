import datetime
import re
import time

## try:
##     from functools import partial
## except ImportError:
##     def partial(func, *args, **kw):
##         def inner(*_args, **_kw):
##             d = kw.copy()
##             d.update(_kw)
##             return func(*(args + _args), **d)
##         return inner            

__all__=['Invalid',
         'clamp',
         'clamp_length',
         'compose',
         'default',
         'dict_nest',
         'dict_unnest',
         'either',
         'empty',
         'equal',
         'not_equal',
         'integer',
         'not_empty',
         'not_belongs',
         'belongs',
         'parse_date',
         'parse_datetime',
         'parse_time',
#         'partial',
         'regex',
         'regex_sub',
         'schema',
         'strip']


def _msg(msg, key, default):
    """
    internal message-handling routine.
    """
    if msg is None:
        return default
    if isinstance(msg, basestring):
        return msg
    return msg.get(key, default)

         
def dict_nest(data, separator='.'):
    """
    takes a flat dictionary with string keys and turns it into a
    nested one by splitting keys on the given separator.
    """
    res={}
    for k in data:
        levels=k.split(separator)
        d=res
        for k1 in levels[:-1]:
            d.setdefault(k1, {})
            d=d[k1]
        d[levels[-1]]=data[k]
    return res

def dict_unnest(data, separator='.'):
    """
    takes a dictionary with string keys and values which may be either
    such dictionaries or non-dictionary values, and turns them into a
    flat dictionary with keys consisting of paths into the nested
    structure, with path elements delimited by the given separator.

    This is the inverse operation of dict_nest().
    """
    res={}
    for k, v in data.iteritems():
        if isinstance(v, dict):
            v=dict_unnest(v, separator)
            for k1, v1 in v.iteritems():
                res["%s%s%s" % (k, separator, k1)]=v1
        else:
            res[k]=v
    return res
        
class Invalid(ValueError):
    # this should support nested exceptions and
    # extracting messages from some context

    def __init__(self, message, subexceptions=None):
        ValueError.__init__(self, message)
        self.subexceptions=subexceptions
        self.message=message

    def unpack_errors(self):
        result={}
        if self.subexceptions:
            for name, exc in self.subexceptions:
                try:
                    result[name]=exc.unpack_errors()
                except AttributeError:
                    result[name]=exc
        return result

def schema(validators, msg=None):
    def f(data):
        res={}
        exceptions={}
        for k, vfunc in validators.iteritems():
            if isinstance(vfunc, (list, tuple)):
                vfunc=compose(*vfunc)
            try:
                res[k]=vfunc(data.get(k))
            except Exception, e:
                exceptions[k]=e
        if exceptions:
            raise Invalid(_msg(msg,
                               "schema_error",
                               "Problems were found in the submitted data."),
                          exceptions)
        return res
    return f

def default(defaultValue):
    """
    if the value is None, return defaultValue instead.

    This raises no exceptions.
    """
    def f(value):
        if value is None:
            return defaultValue
        return value
    return f
        
def either(*validators):
    """
    Tries each of a series of validators in turn, swallowing any
    exceptions they raise, and returns the result of the first one
    that works.  If none work, the last exception caught is re-raised.
    """
    last_exception=None
    def f(value):
        for v in validators:
            try:
                value=v(value)
            except ValueError, e:
                last_exception=e
            else:
                return value
        raise last_exception
    return f

def compose(*validators):
    """
    Applies each of a series of validators in turn, passing the return
    value of each to the next.  
    """
    def f(value):
        for v in validators:
            value=v(value)
        return value
    return f

def equal(val, msg=None):
    def f(value):
        if value==val:
            return value
        raise Invalid(_msg(msg, 'eq', 'invalid value'))
    return f

def not_equal(val, msg=None):
    def f(value):
        if value!=val:
            return value
        raise Invalid(_msg(msg, 'eq', 'invalid value'))
    return f

def empty(msg=None):
    def f(value):
        if value == '' or value is None:
            return value
        raise Invalid(_msg(msg,
                           "empty",
                           "No value was expected"))
    return f

def not_empty(msg=None):
    def f(value):
        if value!='':
            return value
        raise Invalid(_msg(msg,
                           'notempty',
                           "A non-empty value was expected"))
    return f

def strip(value):
    """
    For string/unicode input, strips the value to remove pre- or
    postpended whitespace.  For other values, does nothing; raises no
    exceptions.
    """
    try:
        return value.strip()
    except AttributeError:
        return value

def clamp(min=None, max=None, msg=None):
    """
    clamp a value between minimum and maximum values (either
    of which are optional).
    """
    def f(value):
        if min is not None and value < min:
            raise Invalid(_msg(msg,
                               "min",
                               "value below minimum"))
        if max is not None and value > max:
            raise Invalid(_msg(msg,
                               "max",
                               "value above maximum"))
        return value
    return f

def clamp_length(min=None, max=None, msg=None):
    """
    clamp a value between minimum and maximum lengths (either
    of which are optional).
    """
    def f(value):
        vlen=len(value)
        if min is not None and vlen<min:
                raise Invalid(_msg(msg,
                                   "minlen",
                                   "too long"))
        if max is not None and vlen >max:
                raise Invalid(_msg(msg,
                                   "maxlen",
                                   "too short"))
        return value
    return f

def belongs(domain, msg=None):
    """
    ensures that the value belongs to the domain
    specified.
    """
    def f(value):
        if value in domain:
            return value
        raise Invalid(_msg(msg,
                           "belongs",
                           "invalid choice"))
    return f

def not_belongs(domain, msg=None):
    """
    ensures that the value belongs to the domain
    specified.
    """
    def f(value):
        if value not in domain:
            return value
        raise Invalid(_msg(msg,
                           "not_belongs",
                           "invalid choice"))
    return f



def parse_time(format, msg=None):
    """
    
    """
    def f(value):
        try:
            return time.strptime(value, format)
        except ValueError:
            raise Invalid(_msg(msg,
                               'parse_time',
                               "invalid time"))
    return f

def parse_date(format, msg=None):
    """
    like parse_time, but returns a datetime.date object.
    """
    
    def f(value):
        v=parse_time(format, msg)(value)
        return datetime.date(*v[:3])
    return f

def parse_datetime(format, msg=None):
    """
    like parse_time, but returns a datetime.datetime object.
    """
    
    def f(value):
        v=parse_time(format, msg)(value)
        return datetime.datetime(*v[:6])
    return f                

def integer(msg=None):
    def f(value):
        try:
            return int(value)
        except ValueError:
            raise Invalid(_msg(msg,
                               "integer",
                               "not an integer"))
    return f


def regex(pat, msg=None):
    def f(value):
        m=re.match(pat, value)
        if not m:
            raise Invalid(_msg(msg,
                               'regex',
                               "does not match pattern"))
        return value

def regex_sub(pat, sub):
    def f(value):
        return re.sub(pat, value, sub)
    return f

