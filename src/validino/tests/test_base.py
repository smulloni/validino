import validino as V
from validino.util import partial
from util import assert_invalid

def test_is_scalar():
    msg='sc'
    v=V.is_scalar(msg=msg)
    assert v(40)==40
    assert_invalid(lambda: v([12]), msg)

def test_is_list():
    msg="list"
    v=V.is_list(msg=msg)
    assert v([40])==[40]
    assert_invalid(lambda: v(40), msg)

def test_to_scalar():
    v=V.to_scalar()
    assert v([40])==40
    assert v(40)==40
    assert v(range(40))==0

def test_to_list():
    v=V.to_list()
    assert v(['a', 'b'])==['a', 'b']
    assert v('a')==['a']
    
    
def test_clamp():
    msg='You are a pear'
    v=V.clamp(min=30, msg=msg)
    assert v(50)==50
    assert_invalid(lambda: v(20), msg)

    v=V.clamp(max=100, msg=dict(min='haha', max='kong'))
    assert v(40)==40
    assert_invalid(lambda: v(120), 'kong')


def test_clamp_length():
    msg='You are a pear'
    v=V.clamp_length(min=3, msg=msg)
    assert v('500')=='500'
    assert_invalid(lambda: v('eh'), msg)
    v=V.clamp_length(max=10, msg=dict(minlen='haha', maxlen='kong'))
    assert v('40')=='40'
    assert_invalid(lambda: v('I told you that Ronald would eat it when you were in the bathroom'), 'kong')
    

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
    assert_invalid(lambda: v(' prick '), messages['integer'])
    assert_invalid(lambda: v(' 41  '), messages['belongs'])
    assert_invalid(lambda: v('96'), messages['max'])
    assert_invalid(lambda: v('8'), messages['min'])

def test_check():
    d=dict(x=5, y=100)
    def add_z(val):
        val['z']=300
    def len_d(v2, size):
        if len(v2)!=size:
            raise V.Invalid("wrong size")
    d2=V.check(add_z, partial(len_d, size=3))(d)
    assert d2 is d
    assert d['z']==300
    
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
    v=V.either(V.empty(), V.integer(msg=msg))
    assert v('')==''
    assert v('40')==40
    assert_invalid(lambda: v('bonk'), msg)


def test_empty():
    v=V.empty(msg="scorch me")
    assert v('')==''
    assert v(None)==None
    assert_invalid(lambda: v("bob"), 'scorch me')
    
def test_equal():
    v=V.equal('egg', msg="not equal")
    assert v('egg')=='egg'
    assert_invalid(lambda: v('bob'), 'not equal')

def test_not_equal():
    v=V.not_equal('egg', msg='equal')
    assert v('plop')=='plop'
    assert_invalid(lambda: v('egg'), 'equal')

def test_integer():
    msg="please enter an integer"
    v=V.integer(msg=msg)
    assert v('40')==40
    assert_invalid(lambda: v('whack him until he screams'), msg)

def test_not_empty():
    msg="hammer my xylophone"
    v=V.not_empty(msg=msg)
    assert v("frog")=='frog'
    assert_invalid(lambda: v(''), msg)
    assert_invalid(lambda: v(None), msg)

def test_belongs():
    msg="rinse me a robot"
    v=V.belongs('pinko widget frog lump'.split(), msg=msg)
    assert v('pinko')=='pinko'
    assert_invalid(lambda: v('snot'), msg)

def test_not_belongs():
    msg="belittle my humbug"
    v=V.not_belongs(range(5), msg=msg)
    assert v('pinko')=='pinko'
    assert_invalid(lambda: v(4), msg=msg)

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
    assert_invalid(lambda: v('tough nuggie'), msg)
    

def test_regex():
    v=V.regex('shrubbery\d{3}$', 'regex')
    assert v('shrubbery222')=='shrubbery222'
    assert_invalid(lambda: v('buy a shrubbery333, ok?'), 'regex')

def test_regex_sub():
    v=V.regex_sub('shrubbery', 'potted plant')
    res=v('a shrubbery would be nice')
    assert res=='a potted plant would be nice'


def test_schema_1():
    s=V.Schema(
        dict(username=(V.strip,
                       V.regex('[a-z][a-z0-9]+',
                               'invalid username'),
                       V.clamp_length(max=16,
                                      msg='username is too long'),
                       ),
             user_id=V.either(V.empty(),
                              V.compose(V.integer('not an integer'),
                                        V.clamp(min=1, max=9999, msg='out of range')
                                        )
                              ),
             department=(V.strip,
                         V.belongs(['interactive', 'programming'],
                                   'department not recognized')
                         ),
             ),
        "there were errors with your submission"
        )
    data=dict(username='jsmullyan',
              user_id='1',
              department='interactive')
    newdata=s(data)
    assert data['username']==newdata['username']
    assert int(data['user_id'])==newdata['user_id']
    assert data['department']==newdata['department']
    
def test_schema_2():
    s=V.Schema(
        dict(x=(V.integer('intx'), V.clamp(min=5, max=100, msg='clampx')),
             y=(V.integer('inty'), V.clamp(min=5, max=100, msg='clampy')),
             text=V.strip),
        "schema"
        )
    def check_keys(data):
        allkeys=set(('x', 'y', 'text'))
        found=set(data.keys())
        if allkeys.difference(found):
            raise V.Invalid("incomplete data")
        if found.difference(allkeys):
            raise V.Invalid("extra data")
    v=V.compose(V.check(check_keys), s)
    d1=dict(x=40, y=20, text='hi there')
    assert v(d1)==d1
    d2=dict(x=1, y=20, text='hi there')
    assert_invalid(lambda: v(d2), 'schema')
    d3=dict(x=10, y=10)
    assert_invalid(lambda: v(d3), 'incomplete data')
    d4=dict(x=10, y=10, text='ho', pingpong='lather')
    assert_invalid(lambda: v(d4), 'extra data')

             
def test_schema_3():
    v=V.Schema(
        dict(x=(V.integer('intx'), V.clamp(min=5, max=100, msg='clampx')),
             y=(V.integer('inty'), V.clamp(min=5, max=100, msg='clampy')),
             text=V.strip),
        {'schema.error' : 'schema',
         'schema.extra' : 'extra',
         'schema.missing' : 'missing'},
        False,
        False
        )

    d1=dict(x=40, y=20, text='hi there')
    assert v(d1)==d1
    d2=dict(x=1, y=20, text='hi there')
    assert_invalid(lambda: v(d2), 'schema')
    d3=dict(x=10, y=10)
    assert_invalid(lambda: v(d3), 'missing')
    d4=dict(x=10, y=10, text='ho', pingpong='lather')
    assert_invalid(lambda: v(d4), 'extra')
    

def test_strip():
    assert V.strip('   foo   ')=='foo'
    assert V.strip(None)==None


    
    
def test_fields_match():
    d=dict(foo=3,
           goo=3,
           poo=56)
    v=V.fields_match('foo', 'goo')
    assert d==v(d)
    v=V.fields_match('foo', 'poo', 'oink')
    assert_invalid(lambda: v(d), 'oink')

def test_fields_equal():
    values=("pong", "pong")
    v=V.fields_equal('hog')
    assert values==v(values)
    values=('tim', 'worthy')
    assert_invalid(lambda: v(values), 'hog')

def test_excursion():
    x='gadzooks@wonko.com'

    v=V.excursion(lambda x: x.split('@')[0],
                  V.belongs(['gadzooks', 'willy'],
                            msg='pancreatic'))
    assert x==v(x)
    assert_invalid(lambda: v('hieratic impulses'), 'pancreatic')
    

def test_confirm_type():
    v=V.confirm_type((int, float), 'not a number')
    assert v(45)==45
    assert_invalid(lambda: v('45'), 'not a number')


def test_translate():
    v=V.translate(dict(y=True, f=False),  'dong')
    assert v('y')==True
    assert_invalid(lambda: v('pod'), 'dong')

def test_to_unicode():
    v=V.to_unicode(msg='cats')
    assert v(u"brisbane")==u"brisbane"
    u=u"\N{GREEK CAPITAL LETTER OMEGA} my gawd"
    s=u.encode('utf-8')
    assert v(s)==u


def test_map():
    data=['pig', 'frog', 'lump']
    v=lambda value: map(V.clamp_length(max=4), value)
    assert v(data)==data

def test_unpack_1():
    
    e=V.Invalid({'ding' : [V.Invalid('pod')],
                 'dong' : [V.Invalid('piddle')]})
    res=e.unpack_errors()
    print res
    assert res=={'ding' : ['pod'], 'dong' : ['piddle']}
    e2=V.Invalid({'' : [e]})
    res2=e.unpack_errors()
    print res2
    assert res==res2


def test_unpack_2():
    e=V.Invalid({'ding' : [V.Invalid('pod')],
                 'dong' : [V.Invalid('piddle')]})    
    
    e2=V.Invalid({'' : [e]})
    e3=V.Invalid({'' : [e2]})
    r1=e.unpack_errors()
    print
    print r1
    r2=e2.unpack_errors()
    print r2
    r3=e3.unpack_errors()
    print r3
    assert r1==r3

def test_unpack_3():
    errors=dict(frog="My peachy frog hurts",
                dog="My dog has warts up and down his spine",
                insect="I would characterize this insect as flawed")
    e=V.Invalid(**errors)

    u=e.unpack_errors()
    print u
    assert set(u)==set(('frog', 'dog', 'insect'))
    for v in u.itervalues():
        assert isinstance(v, list)
        assert len(v)==1

    e2=V.Invalid(frog='squished')
    u2=e2.unpack_errors()
    assert u2==dict(frog=['squished'])

    e3=V.Invalid(errors,
                 {'' : [e2]})
    u3=e3.unpack_errors()
    assert set(u3)==set(('frog', 'dog', 'insect'))
    for k, v in u3.iteritems():
        assert isinstance(v, list)
        if k=='frog':
            assert len(v)==2
        else:
            assert len(v)==1
                
                            
