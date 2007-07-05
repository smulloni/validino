import validino as V

def assert_invalid(f, msg):
    try:
        f()
    except V.Invalid, e:
        assert e.message==msg
    else:
        assert False, "exception should be raised"

