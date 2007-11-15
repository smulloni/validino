
from threading import local

_messagelocal=local()
_messagelocal.messages={}

__all__=['getMessages']

try:
    from contextlib import contextmanager
except ImportError:
    pass
else:
    @contextmanager
    def msg(messages):
        oldmessages=_messagelocal.messages
        _messagelocal.messages=messages
        try:
            yield
        finally:
            _messagelocal.messages=oldmessages
            
    __all__.append('msg')
    
def getMessages():
    return _messagelocal.messages


