class Field(object):

    _default_attrs={}

    _default_validators=()
    
    def __init__(self, *validators, **attributes):
        a=self._default_attrs.copy()
        a.update(attributes)
        self.required=a.pop('required', False)
        self.type=a.pop('type', None)
        self._attributes=a        
        self._validator=self._make_validator(validators)

    def _make_validator(self, validators):
        validators=self._default_validators + validators
        if not self.required:
            return V.either(V.empty(), *validators)
        else:
            return V.compose(*validators)

    def __getattr__(self, k):
        try:
            return self._attributes[k]
        except KeyError:
            raise AttributeError("no such attribute: %s" % k)

    def __call__(self, data):
        return self._validator(data)


class DateField(Field):

    _default_attrs=dict(format='%m/%d/%Y',
                        type='date')

    def _make_validator(self, validators):
        validators=(V.parse_date(self.format),) + validators
        return super(DateField, self)._make_validator(validators)
    
                                        
class DateTimeField(Field):

    _default_attrs=dict(format='%m/%d/%Y %H:%M',
                        type='datetime')

    def _make_validator(self, validators):
        validators=(V.parse_datetime(self.format),) + validators
        return super(DateTimeField, self)._make_validator(validators)
    
class TimeField(Field):
    _default_attrs=dict(format='%H:%M',
                        type="time")

    def _make_validator(self, validators):
        validators=(V.parse_time(self.format),) + validators
        return super(TimeField, self)._make_validator(validators)
        
