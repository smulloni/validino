import validino as V

def assert_invalid(f, msg):
    try:
        f()
    except V.Invalid, e:
        print e.message, e.errors
        if isinstance(msg, basestring):
            assert e.message==msg, "expected '%s', got '%s'" % (msg, e.message)
        else:
            assert e.errors==msg
    else:
        assert False, "exception should be raised"

