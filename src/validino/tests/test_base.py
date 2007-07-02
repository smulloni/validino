import validino as V

def test_dict_decode_encode():
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
    d1=V.dict_decode(d)
    assert d1['robots']['names']==['sally', 'bob']
    assert d1['x']==33
    assert d1['y']==22
    assert d1['frogs']['oswald']=={'size' : 'medium'}
    d2=V.dict_encode(d1)
    assert d==d2
    
    
