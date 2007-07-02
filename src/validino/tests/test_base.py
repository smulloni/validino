import validino as V

def _assert_invalid(f, msg):
    try:
        f()
    except V.Invalid, e:
        assert e.message==msg
    else:
        assert False, "exception should be raised"

    
def test_clamp():
    msg='You are a pear'
    v=V.clamp(min=30, msg=msg)
    assert v(50)==50
    _assert_invalid(lambda: v(20), msg)

    v=V.clamp(max=100, msg=dict(min='haha', max='kong'))
    assert v(40)==40
    _assert_invalid(lambda: v(120), 'kong')


def test_clamp_length():
    msg='You are a pear'
    v=V.clamp_length(min=3, msg=msg)
    assert v('500')=='500'
    _assert_invalid(lambda: v('eh'), msg)
    v=V.clamp_length(max=10, msg=dict(minlen='haha', maxlen='kong'))
    assert v('40')=='40'
    _assert_invalid(lambda: v('I told you that Ronald would eat it when you were in the bathroom'), 'kong')
    

def test_compose():
    messages=dict(integer='please enter an integer',
                  belongs='invalid choice',
                  min='too small',
                  max='too big')
    v=V.compose(V.default(40),
                V.strip,
                V.integer(msg=messages),
                V.belongs(range(4, 100, 4), messages),
                V.clamp(min=20, max=50, msg=messages))
    assert v(None)==40
    assert v('40')==40
    assert v('44  ')==44
    _assert_invalid(lambda: v(' prick '), messages['integer'])
    _assert_invalid(lambda: v(' 41  '), messages['belongs'])
    _assert_invalid(lambda: v('96'), messages['max'])
    _assert_invalid(lambda: v('8'), messages['min'])
    

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
    _assert_invalid(lambda: v('bonk'), msg)


def test_empty():
    v=V.empty(msg="scorch me")
    assert v('')==''
    _assert_invalid(lambda: v("bob"), 'scorch me')
    
def test_equal():
    v=V.equal('egg', msg="not equal")
    assert v('egg')=='egg'
    _assert_invalid(lambda: v('bob'), 'not equal')

def test_not_equal():
    v=V.not_equal('egg', msg='equal')
    assert v('plop')=='plop'
    _assert_invalid(lambda: v('egg'), 'equal')

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
    msg="rinse me a robot"
    v=V.belongs('pinko widget frog lump'.split(), msg=msg)
    assert v('pinko')=='pinko'
    _assert_invalid(lambda: v('snot'), msg)

def test_not_belongs():
    msg="belittle my humbug"
    v=V.not_belongs(range(5), msg=msg)
    assert v('pinko')=='pinko'
    _assert_invalid(lambda: v(4), msg=msg)

def test_parse_date():
    fmt='%m %d %Y'
    msg='Gargantua and Pantagruel'
    v=V.parse_datetime(fmt, msg)
    dt=v('07 02 2007')
    assert dt.year==2007
    assert dt.month==7
    assert dt.day==2
    
def test_parse_datetime():
    fmt='%m %d %Y %H:%M'
    msg='Gargantua and Pantagruel'
    v=V.parse_datetime(fmt, msg)
    dt=v('07 02 2007 12:34')
    assert dt.year==2007
    assert dt.hour==12
    assert dt.minute==34
    

def test_parse_time():
    fmt='%m %d %Y'
    msg="potted shrimp"
    v=V.parse_time(fmt, msg)
    ts=v('10 03 2007')[:3]
    assert ts==(2007, 10, 3)
    _assert_invalid(lambda: v('tough nuggie'), msg)
    

def test_regex():
    v=V.regex('shrubbery\d{3}$', 'regex')
    assert v('shrubbery222')=='shrubbery222'
    _assert_invalid(lambda: v('buy a shrubbery333, ok?'), 'regex')

def test_regex_sub():
    v=V.regex_sub('shrubbery', 'potted plant')
    res=v('a shrubbery would be nice')
    assert res=='a potted plant would be nice'


def test_schema():
    pass

def test_strip():
    assert V.strip('   foo   ')=='foo'
    assert V.strip(None)==None


    
    
