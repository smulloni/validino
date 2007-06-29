import datetime
import re
import time

class Invalid(ValueError):
    # this should support nested exceptions and
    # extracting messages from some context

    def __init__(self, message, subexceptions=()):
        ValueError.__init__(self, message)
        self.subexceptions=tuple(subexceptions)

    

        
        

class NoDefault(object): pass

def Schema(validators):
    def f(data):
        res={}
        exceptions={}
        for k, vfunc in validators.iteritems():
            if isinstance(vfunc, (list, tuple)):
                vfunc=Compose(*vfunc)
            try:
                res[k]=vfunc(data.get(k, NoDefault))
            except Exception, e:
                exceptions[k]=e
        if exceptions:
            raise Invalid(exceptions)
        return res
    return f

def Default(defaultValue):
    def f(value):
        if value is NoDefault:
            return defaultValue
        return value
    return f
        
def Either(*validators):
    last_exception=None
    def f(value):
        for v in validators:
            try:
                value=v(value)
            except Invalid, e:
                last_exception=e
            else:
                return value
        raise last_exception
    return f

def Compose(*validators):
    def f(value):
        for v in validators:
            value=v(value)
        return value
    return f

def Any(*validators):
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
                
def Empty():
    def f(value):
        if value=='':
            return value
        raise Invalid('non-empty value')
    return f

def NotEmpty():
    def f(value):
        if value!='':
            return value
        raise Invalid('empty value')

def Strip():
    def f(value):
        return value.strip()
    return f

def Length(min=None, max=None):
    def f(value):
        vlen=len(value)
        if min is not None:
            if vlen<min:
                raise Invalid("length less than minimum")
        if max is not None:
            if vlen >max:
                raise Invalid("length greater than maximum")
        return value
    return f

def OneOf(domain):
    def f(value):
        if value in domain:
            return value
        raise Invalid("not in domain")
    return f


def Strptime(format):
    """
    
    """
    def f(value):
        try:
            return time.strptime(value, format)
        except ValueError:
            raise Invalid("doesn't match format")
    return f

def Date(format):
    """
    like strptime, but returns a datetime.date object.
    """
    
    def f(value):
        v=Strptime(format)(value)
        return datetime.date(v[:3])
    return f

def Datetime(format):
    """
    like strptime, but returns a datetime.datetime object.
    """
    
    def f(value):
        v=Strptime(format)(value)
        return datetime.date(v[:6])
    return f                

def Integer():
    def f(value):
        try:
            return int(value)
        except ValueError:
            raise Invalid("not an integer")
    return f

def Regex(pat):
    if isinstance(pat, basestring):
        pat=re.compile(pat)
    def f(value):
        m=pat.match(value)
        if not m:
            raise Invalid("does not match pattern")
        return value

def RegexSub(pat, sub):
    if isinstance(pat, basestring):
        pat=re.compile(pat)
    def f(value):
        return pat.sub(value, sub)
    return f

