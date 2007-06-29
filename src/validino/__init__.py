import datetime
import re
import time

try:
    from functools import partial
except ImportError:
    def partial(func, *args, **kw):
        def inner(*_args, **_kw):
            d = kw.copy()
            d.update(_kw)
            return func(*(args + _args), **d)
        return inner            

         
def dict_decode(data, separator='.'):
    """
    
    takes a flat dictionary with string keys and turns it into a
    nested one by splitting keys on the given separator.
    
    """
    res={}
    for k in data:
        levels=k.split(separator)
        d=res
        for k in levels[:-1]:
            d.setdefault(k, {})
            d=d[k]
        d[levels[-1]]=data[k]
    return res

def dict_encode(data, separator='.'):
    """
    the inverse operation of dict_decode.
    """
    res={}
    for k, v in data.iteritems():
        if isinstance(v, dict):
            v=dict_encode(v, separator)
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

    def unpack_errors(self):
        result={}
        if self.subexceptions:
            for name, exc in self.subexceptions:
                try:
                    result[name]=exc.unpack_errors()
                except AttributeError:
                    result[name]=exc
        return result

    # change messages here
    MESSAGES={}

    def format_message(self):
        return self.MESSAGES.get(self.message, self.message)

    @classmethod
    def get_exception(cls, messageKey, defaultMessage, subexceptions=None):
        cls.MESSAGES.setdefault(messageKey, defaultMessage)
        return cls(messageKey, subexceptions)


class NoDefault(object): pass

def schema(validators):
    def f(data):
        res={}
        exceptions={}
        for k, vfunc in validators.iteritems():
            if isinstance(vfunc, (list, tuple)):
                vfunc=compose(*vfunc)
            try:
                res[k]=vfunc(data.get(k, NoDefault))
            except Exception, e:
                exceptions[k]=e
        if exceptions:
            raise Invalid.get_exception("schema_error",
                                        "Problems were found in the submitted data.",
                                        exceptions)
        return res
    return f

def default(defaultValue):
    def f(value):
        if value is NoDefault:
            return defaultValue
        return value
    return f
        
def either(*validators):
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
    def f(value):
        for v in validators:
            value=v(value)
        return value
    return f

def any(*validators):
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

def empty():
    def f(value):
        if value=='':
            return value
        raise Invalid.get_exception("empty", "No value was expected")
    return f

def not_empty():
    def f(value):
        if value!='':
            return value
        raise Invalid('not_empty', "A non-empty value was expected")

def strip():
    def f(value):
        return value.strip()
    return f

def length(min=None, max=None):
    def f(value):
        vlen=len(value)
        if min is not None:
            if vlen<min:
                raise Invalid.get_exception("min_length", "too long")
        if max is not None:
            if vlen >max:
                raise Invalid.get_exception("max_length", "too short")
        return value
    return f

def in_domain(domain):
    def f(value):
        if value in domain:
            return value
        raise Invalid.get_exception("domain_error", "not in domain")
    return f


def parse_time(format):
    """
    
    """
    def f(value):
        try:
            return time.strptime(value, format)
        except ValueError:
            raise Invalid.get_exception('parse_time', "invalid time")
    return f

def parse_date(format):
    """
    like parse_time, but returns a datetime.date object.
    """
    
    def f(value):
        v=parse_time(format)(value)
        return datetime.date(v[:3])
    return f

def parse_datetime(format):
    """
    like parse_time, but returns a datetime.datetime object.
    """
    
    def f(value):
        v=parse_time(format)(value)
        return datetime.date(v[:6])
    return f                

def integer():
    def f(value):
        try:
            return int(value)
        except ValueError:
            raise Invalid.get_exception("integer", "not an integer")
    return f

def regex(pat):
    if isinstance(pat, basestring):
        pat=re.compile(pat)
    def f(value):
        m=pat.match(value)
        if not m:
            raise Invalid.get_exception('regex', "does not match pattern")
        return value

def regex_sub(pat, sub):
    if isinstance(pat, basestring):
        pat=re.compile(pat)
    def f(value):
        return pat.sub(value, sub)
    return f

