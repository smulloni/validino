import datetime
import re
import time

__all__=['Invalid',
         'check',
         'clamp',
         'clamp_length',
         'compose',
         'confirm_type',
         'default',
         'dict_nest',
         'dict_unnest',
         'either',
         'empty',
         'equal',
         'excursion',
         'fields_equal',
         'fields_match',
         'not_equal',
         'integer',
         'not_empty',
         'not_belongs',
         'belongs',
         'parse_date',
         'parse_datetime',
         'parse_time',
         'pluralize',
         'regex',
         'regex_sub',
         'Schema',
         'strip',
         'to_unicode',
         'translate']


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

    def __init__(self, message, field=None, subexceptions=None):
        ValueError.__init__(self, message)
        self.subexceptions=subexceptions
        self.message=message
        self.field=field

    def unpack_errors(self, force_dict=True):
        if self.subexceptions or force_dict:
            result={None: [self.message]}
        else:
            result=self.message
        if self.subexceptions:

            for name, excs in self.subexceptions.iteritems():
                result.setdefault(name, [])
                for exc in excs:
                    try:
                        result[name].append(exc.unpack_errors(force_dict=False))
                    except AttributeError:
                        result[name].append(exc.args[0])


        return result


class Schema(object):
    """
    creates a validator from a dictionary of subvalidators that will
    be used to validate a dictionary of data, returning a new
    dictionary that contains the converted values.

    The keys in the validator dictionary may be either singular -- atoms
    (presumably strings) that match keys in the data dictionary, or
    plural -- lists/tuples of such atoms.

    The values associated with those keys should be subvalidator
    functions (or lists/tuples of functions that will be composed
    automatically) that are passed a value or values taken from the
    data dictionary according to the corresponding key in the data
    dictionary.  If the key is singular, the subvalidator will be
    passed the data dictionary's value for the key (or None); if
    plural, it will be passed a tuple of the data dictionary's values
    for all the items in the plural key (e.g., tuple(data[x] for x in
    key)).  In either case, the return value of the subvalidator
    should match the structure of the input.

    The subvalidators are sorted by key before being executed.  Therefore,
    subvalidators with plural keys will always be executed after those
    with singular keys.

    If allow_missing is False, then any missing keys in the input will
    give rise to an error.  Similarly, if allow_extra is False, any
    extra keys will result in an error.

    """    
    def __init__(self,
                 subvalidators,
                 msg=None,
                 allow_missing=True,
                 allow_extra=True):
        self.subvalidators=subvalidators
        self.msg=msg
        self.allow_missing=allow_missing
        self.allow_extra=allow_extra

    def keys(self):
        schemakeys=set()
        for x in self.subvalidators:
            if isinstance(x, (list, tuple)):
                for x1 in x:
                    schemakeys.add(x1)
            else:
                schemakeys.add(x)
        return schemakeys


    def __call__(self, data):
        res={}
        exceptions={}
        if not (self.allow_extra and self.allow_missing):
            inputkeys=set(data.keys())
            schemakeys=self.keys()
            if not self.allow_extra:
                if inputkeys.difference(schemakeys):
                    raise Invalid(_msg(self.msg,
                                       'schema.extra',
                                       'extra keys in input'))
            if not self.allow_missing:
                if schemakeys.difference(inputkeys):
                    raise Invalid(_msg(self.msg,
                                       'schema.missing',
                                       'missing keys in input'))
                
        for k in sorted(self.subvalidators):
            vfunc=self.subvalidators[k]
            if isinstance(vfunc, (list, tuple)):
                vfunc=compose(*vfunc)
            have_plural=isinstance(k, (list,tuple))
            if have_plural:
                vdata=tuple(data.get(x) for x in k)
            else:
                vdata=data.get(k)
            try:
                tmp=vfunc(vdata)
            except Exception, e:
                # if the exception specifies a field name,
                # let that override the key in the validator
                # dictionary
                name=getattr(e, 'field', k) or k
                exceptions.setdefault(name, [])
                exceptions[name].append(e)
            else:
                if have_plural:
                    res.update(dict(zip(k, tmp)))
                else:
                    res[k]=tmp

        if exceptions:
            raise Invalid(_msg(self.msg,
                               "schema.error",
                               "Problems were found in the submitted data."),
                          subexceptions=exceptions)
        return res        
            

def confirm_type(typespec, msg=None):
    def f(value):
        if isinstance(value, typespec):
            return value
        raise Invalid(_msg(msg,
                           "confirm_type",
                           "unexpected type"))
    return f

def translate(mapping, msg=None):
    def f(value):
        try:
            return mapping[value]
        except KeyError:
            raise Invalid(_msg(msg,
                               "belongs",
                               "invalid choice"))
    return f

def to_unicode(encoding='utf8', errors='strict', msg=None):
    def f(value):
        if isinstance(value, unicode):
            return value
        else:
            try:
                return value.decode(encoding, errors)
            except UnicodeError, e:
                raise Invalid(_msg(msg,
                                   'to_unicode',
                                   'decoding error'))

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

def check(*validators):
    """
    Returns a function that runs each of a series of validators
    against input data, which is passed to each validator in turn,
    ignoring the validators return value.  The function returns the
    original input data (which, if it mutable, may have been changed).
    
    """
    def f(value):
        for v in validators:
            v(value)
        return value
    return f

def excursion(*validators):
    """
    perform a series of validations that may break down the data
    passed in into a form that you don't deserve to retain; if the
    data survives validation, you carry on from the point the
    excursion started.
    """
    def f(value):
        compose(*validators)(value)
        return value
    return f

def pluralize(val):
    if not isinstance(val, (list,tuple)):
        return [val]
    return val

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
        if value!='' and value != None:
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
    ensures that the value does not belong to the domain
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
    attempts to parse the time according to
    the given format, returning a timetuple,
    or raises an Invalid exception.
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
    """
    attempts to coerce the value into an integer.
    """
    def f(value):
        try:
            return int(value)
        except ValueError:
            raise Invalid(_msg(msg,
                               "integer",
                               "not an integer"))
    return f


def regex(pat, msg=None):
    """
    tests the value against the given regex pattern
    and raises Invalid if it doesn't match.
    
    """
    def f(value):
        m=re.match(pat, value)
        if not m:
            raise Invalid(_msg(msg,
                               'regex',
                               "does not match pattern"))
        return value
    return f

def regex_sub(pat, sub):
    """
    performs regex substitution on the input value.
    """
    def f(value):
        return re.sub(pat, sub, value)
    return f

def fields_equal(msg=None, field=None):
    """
    when passed a collection of values,
    verifies that they are all equal.
    """
    def f(values):
        if len(set(values))!=1:
            raise Invalid(_msg(msg,
                               'fields_equal',
                               "fields not equal"),
                          field=field)
        return values
    return f

def fields_match(name1, name2, msg=None, field=None):
    """
    verifies that the values associated with the keys 'name1' and
    'name2' in value (which must be a dict) are identical.
    """
    def f(value):
        if value[name1]!=value[name2]:
            raise Invalid(_msg(msg,
                               'fields_match',
                               'fields do not match'),
                          field=field)
        return value
    return f
