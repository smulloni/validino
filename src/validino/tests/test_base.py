import validino as V

    
def test_clamp():
    msg='You are a pear'
    v=V.clamp(min=30, msg=msg)
    assert v(50)==50
    try:
        v(20)
    except V.Invalid, e:
        assert e.message==msg
    else:
        assert False, "exception should be raised"

    v=V.clamp(max=100, msg=dict(min='haha', max='kong'))
    assert v(40)==40
    try:
        v(120)
    except V.Invalid, e:
        assert e.message=='kong'
    else:
        assert False, "exception should be raised"

def test_clamp_length():
    msg='You are a pear'
    v=V.clamp_length(min=3, msg=msg)
    assert v('500')=='500'
    try:
        v('eh')
    except V.Invalid, e:
        assert e.message==msg
    else:
        assert False, "exception should be raised"

    v=V.clamp_length(max=10, msg=dict(minlen='haha', maxlen='kong'))
    assert v('40')=='40'
    try:
        v('I told you that Ronald would eat it when you were in the bathroom')
    except V.Invalid, e:
        assert e.message=='kong'
    else:
        assert False, "exception should be raised"

def test_compose():
    pass

def test_default():
    v=V.default("pong")
    assert v(None)=='pong'

def test_dict_nest():
    d={'robots.bob.size' : 34,
       'robots.bob.color' : 'blue',
       'robots.sally.size' : 12,
       'robots.sally.color' : 'green',
       'robots.names' : ['sally', 'bob'],
       'frogs.names' : ['oswald', 'humphrey'],
       'frogs.oswald.size' : 'medium',
       'frogs.humphrey.size' : 'large',
       'x' : 33,
       'y' : 22}
    d1=V.dict_nest(d)
    assert d1['robots']['names']==['sally', 'bob']
    assert d1['x']==33
    assert d1['y']==22
    assert d1['frogs']['oswald']=={'size' : 'medium'}
    d2=V.dict_unnest(d1)
    assert d==d2

def test_either():
    msg="please enter an integer"
    v=V.either(V.empty(), V.integer(msg="please enter an integer"))
    assert v('')==''
    assert v('40')==40
    try:
        v('bonk')
    except V.Invalid, e:
        assert e.message==msg


def test_empty():
    v=V.empty(msg="scorch me")
    assert v('')==''
    try:
        v("bob")
    except V.Invalid, e:
        assert e.message=='scorch me'
    else:
        assert False, "expected an exception to be raised"
    
def test_equal():
    pass

def test_not_equal():
    pass

def test_integer():
    msg="please enter an integer"
    v=V.integer(msg=msg)
    assert v('40')==40
    try:
        v('whack him until he screams')
    except V.Invalid, e:
        assert e.message==msg
    else:
        assert False, "expected an exception to be raised"

def test_not_empty():
    msg="hammer my xylophone"
    v=V.not_empty(msg=msg)
    assert v("frog")=='frog'
    try:
        v('')
    except V.Invalid, e:
        assert e.message==msg
    else:
        assert False, "expected an exception to be raised"

def test_belongs():
    pass

def test_not_belongs():
    pass

def test_parse_date():
    pass

def test_parse_datetime():
    pass

def test_parse_time():
    pass

def test_regex():
    pass

def test_regex_sub():
    pass

def test_schema():
    pass

def test_strip():
    assert V.strip('   foo   ')=='foo'
    assert V.strip(None)==None


    
    
