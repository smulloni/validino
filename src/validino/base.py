import datetime
import re
import time

from .messages import getMessages

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
         'is_list',
         'is_scalar',
         'not_equal',
         'integer',
         'not_empty',
         'not_belongs',
         'belongs',
         'parse_date',
         'parse_datetime',
         'parse_time',
         'regex',
         'regex_sub',
         'Schema',
         'strip',
         'to_list',
         'to_scalar',
         'to_unicode',
         'translate']


def _add_error_message(d, k, msg):
    """
    internal utility for adding an error message to a
    dictionary of messages.
    """
    d.setdefault(k, [])
    if msg not in d[k]:
        d[k].append(msg)


def _msg(msg, key, default):
    """
    internal message-handling routine.
    """
    if msg is None:
        msg=getMessages()
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
        
class Invalid(Exception):
    # this should support nested exceptions and
    # extracting messages from some context

    def __init__(self,
                 *args,
                 **kw):
        d={}
        p=[]
        for a in args:
            if isinstance(a, dict):
                self._join_dicts(d, a)
            else:
                p.append(a)
        d.update(self._normalize_dict(kw))
        Exception.__init__(self, p)
        self.errors=d
        if p:
            self.message=p[0]
        else:
            self.message=None

        
    @staticmethod
    def _join_dicts(res, d):
        for k, v in d.iteritems():
            res.setdefault(k, [])
            if not isinstance(v, (list,tuple)):
                res[k].append(v)
            else:
                res[k].extend(v)


    @staticmethod
    def _normalize_dict(d):
        res={}
        if d:
            for k, v in d.iteritems():
                if not isinstance(v, (list,tuple)):
                    res[k]=[v]
                else:
                    res[k]=v
        return res

    @staticmethod
    def _safe_append(adict, key, thing):
        if not isinstance(thing, (list, dict)):
            thing=[thing]
        try:
            adict[key].extend(thing)
        except KeyError:
            adict[key]=thing


    def add_error_message(self, key, message):
        _add_error_message(self.errors, key, message)
        

    def unpack_errors(self, force_dict=True):
        if self.errors or force_dict:
            if self.message:
                # drop the top level message if it is empty
                result={None: [self.message]}
            else:
                result={}
        else:
            return self.message
        
        if self.errors:
            for name, msglist in self.errors.iteritems():
                for m in msglist:
                    if isinstance(m, Exception):
                        try:
                            unpacked=m.unpack_errors(force_dict=False)
                        except AttributeError:
                            self._safe_append(result, name, m.args[0])
                        
                        else:
                            if isinstance(unpacked, dict):
                                self._join_dicts(result, unpacked)
                            elif unpacked:
                                self._safe_append(result, name, unpacked)
                    else:
                        self._safe_append(result, name, m)
        
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

    def _keys(self):
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
            schemakeys=self._keys()
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
                vdata=tuple(res.get(x, data.get(x)) for x in k)
            else:
                vdata=res.get(k, data.get(k))
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
                          exceptions)
        return res        
            

def confirm_type(typespec, msg=None):
    def f(value):
        if isinstance(value, f.typespec):
            return value
        raise Invalid(_msg(f.msg,
                           "confirm_type",
                           "unexpected type"))
    f.typespec=typespec
    f.msg=msg
    return f

def translate(mapping, msg=None):
    def f(value):
        try:
            return f.mapping[value]
        except KeyError:
            raise Invalid(_msg(f.msg,
                               "belongs",
                               "invalid choice"))
    f.mapping=mapping
    f.msg=msg
    return f

def to_unicode(encoding='utf8', errors='strict', msg=None):
    def f(value):
        if isinstance(value, unicode):
            return value
        else:
            try:
                return value.decode(f.encoding, f.errors)
            except UnicodeError, e:
                raise Invalid(_msg(f.msg,
                                   'to_unicode',
                                   'decoding error'))
    f.encoding=encoding
    f.errors=errors
    f.msg=msg
    return f


def is_scalar(msg=None, listtypes=(list,)):
    """
    Raises an exception if the value is not a scalar.
    """
    def f(value):
        if isinstance(value, f.listtypes):
            raise Invalid(_msg(f.msg,
                               'is_scalar',
                               'expected scalar value'))
        return value
    f.listtypes=listtypes
    f.msg=msg
    return f

def is_list(msg=None, listtypes=(list,)):
    """
    Raises an exception if the value is not a list.
    """
    def f(value):
        if not isinstance(value, f.listtypes):
            raise Invalid(_msg(f.msg,
                               "is_list",
                               "expected list value"))
        return value
    f.listtypes=listtypes
    f.msg=msg    
    return f

def to_scalar(listtypes=(list,)):
    """
    if the value is a list, return the first element.
    Otherwise, return the value.

    This raises no exceptions.
    """
    def f(value):
        if isinstance(value, f.listtypes):
            return value[0]
        return value
    f.listtypes=listtypes
    return f

def to_list(listtypes=(list,)):
    """
    if the value is a scalar, wrap it in a list.
    Otherwise, return the value.

    This raises no exceptions.
    """
    def f(value):
        if not isinstance(value, f.listtypes):
            return [value]
        return value
    f.listtypes=listtypes
    return f

def default(defaultValue):
    """
    if the value is None, return defaultValue instead.

    This raises no exceptions.
    """
    def f(value):
        if value is None:
            return f.defaultValue
        return value
    f.defaultValue=defaultValue
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
            except Exception, e:
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

def equal(val, msg=None):
    def f(value):
        if value==f.val:
            return value
        raise Invalid(_msg(f.msg, 'eq', 'invalid value'))
    f.val=val
    f.msg=msg
    return f

def not_equal(val, msg=None):
    def f(value):
        if value!=f.val:
            return value
        raise Invalid(_msg(f.msg, 'eq', 'invalid value'))
    f.val=val
    f.msg=msg
    return f

def empty(msg=None):
    def f(value):
        if value == '' or value is None:
            return value
        raise Invalid(_msg(f.msg,
                           "empty",
                           "No value was expected"))
    f.msg=msg
    return f

def not_empty(msg=None):
    def f(value):
        if value!='' and value != None:
            return value
        raise Invalid(_msg(f.msg,
                           'notempty',
                           "A non-empty value was expected"))
    f.msg=msg
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
        if f.min is not None and value < f.min:
            raise Invalid(_msg(f.msg,
                               "min",
                               "value below minimum"))
        if f.max is not None and value > f.max:
            raise Invalid(_msg(f.msg,
                               "max",
                               "value above maximum"))
        return value
    f.min=min
    f.max=max
    f.msg=msg
    return f

def clamp_length(min=None, max=None, msg=None):
    """
    clamp a value between minimum and maximum lengths (either
    of which are optional).
    """
    def f(value):
        vlen=len(value)
        if f.min is not None and vlen<f.min:
                raise Invalid(_msg(f.msg,
                                   "minlen",
                                   "too short"))
        if f.max is not None and vlen >f.max:
                raise Invalid(_msg(f.msg,
                                   "maxlen",
                                   "too long"))
        return value
    f.min=min
    f.max=max
    f.msg=msg
    return f

def belongs(domain, msg=None):
    """
    ensures that the value belongs to the domain
    specified.
    """
    def f(value):
        if value in f.domain:
            return value
        raise Invalid(_msg(f.msg,
                           "belongs",
                           "invalid choice"))
    f.domain=domain
    f.msg=msg
    return f

def not_belongs(domain, msg=None):
    """
    ensures that the value does not belong to the domain
    specified.
    """
    def f(value):
        if value not in f.domain:
            return value
        raise Invalid(_msg(f.msg,
                           "not_belongs",
                           "invalid choice"))
    f.domain=domain
    f.msg=msg
    return f



def parse_time(format, msg=None):
    """
    attempts to parse the time according to
    the given format, returning a timetuple,
    or raises an Invalid exception.
    """
    def f(value):
        try:
            return time.strptime(value, f.format)
        except ValueError:
            raise Invalid(_msg(f.msg,
                               'parse_time',
                               "invalid time"))
    f.format=format
    f.msg=msg
    return f

def parse_date(format, msg=None):
    """
    like parse_time, but returns a datetime.date object.
    """
    
    def f(value):
        v=parse_time(f.format, f.msg)(value)
        return datetime.date(*v[:3])
    f.format=format
    f.msg=msg
    return f

def parse_datetime(format, msg=None):
    """
    like parse_time, but returns a datetime.datetime object.
    """
    
    def f(value):
        v=parse_time(f.format, f.msg)(value)
        return datetime.datetime(*v[:6])
    f.format=format
    f.msg=msg
    return f                

def integer(msg=None):
    """
    attempts to coerce the value into an integer.
    """
    def f(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise Invalid(_msg(f.msg,
                               "integer",
                               "not an integer"))
    f.msg=msg
    return f


def regex(pat, msg=None):
    """
    tests the value against the given regex pattern
    and raises Invalid if it doesn't match.
    
    """
    def f(value):
        m=re.match(f.pat, value)
        if not m:
            raise Invalid(_msg(f.msg,
                               'regex',
                               "does not match pattern"))
        return value
    f.pat=pat
    f.msg=msg
    return f

def regex_sub(pat, sub):
    """
    performs regex substitution on the input value.
    """
    def f(value):
        return re.sub(f.pat, f.sub, value)
    f.pat=pat
    f.sub=sub
    return f

def fields_equal(msg=None, field=None):
    """
    when passed a collection of values,
    verifies that they are all equal.
    """
    def f(values):
        if len(set(values))!=1:
            m=_msg(f.msg,
                   'fields_equal',
                   "fields not equal")
            if f.field is None:
                raise Invalid(m)
            else:
                raise Invalid({f.field: m})
        return values
    f.msg=msg
    f.field=field
    return f

def fields_match(name1, name2, msg=None, field=None):
    """
    verifies that the values associated with the keys 'name1' and
    'name2' in value (which must be a dict) are identical.
    """
    def f(value):
        if value[f.name1]!=value[f.name2]:
            m=_msg(f.msg,
                   'fields_match',
                   'fields do not match')
            if f.field is not None:
                raise Invalid({f.field: m})
            else:
                raise Invalid(m)
        return value
    f.name1=name1
    f.name2=name2
    f.msg=msg
    f.field=field
    return f
