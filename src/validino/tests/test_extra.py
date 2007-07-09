import validino as V
from util import assert_invalid

def test_email():
    v=V.email()
    e="jsmullyan@scazzab.com"
    assert v(e)==e
    e='notrealatall@whitehouse.gov'
    v=V.email(True, 'snog')
    assert v(e)==e
    assert_invalid(lambda: v('notrealatall@zzzzonononononofgfgfg.dfg'), 'snog')
    
def test_ip():
    v=V.ip('donkey')
    i='192.168.1.243'
    assert v(i)==i
    assert_invalid(lambda: v("this is not an ip"), 'donkey')


def test_credit_card_1():
    cc='4000000000998'
    v=V.credit_card(msg="aha")
    assert v(cc)==cc
    assert_invalid(lambda: v('pain chocolat'), 'aha')
    assert_invalid(lambda: v(str(int(cc)-1)), 'aha')
    v=V.credit_card(require_type=True,  msg='aha')
    assert v((cc, 'Visa'))==(cc, 'Visa')


def test_credit_card_2():    
    cc='4000000000998'
    invalid_cc=str(int(cc)-1)
    s=V.Schema(dict(cc_card=(V.strip, V.not_empty("Please enter a credit card number")),
                    cc_type=V.belongs(('Visa', 'Discover'), msg="belongs")))
    v=V.credit_card(require_type=True,
                    cc_field='cc_card',
                    cc_type_field='cc_type')
    s.subvalidators[('cc_card', 'cc_type')]=v                
                                                         
    data=dict(cc_card=cc,
              cc_type='Visa')
    assert s(data)==data

    data['cc_card']=invalid_cc
    try:
        s(data)
    except V.Invalid, e:
        errors=e.unpack_errors()
        assert set(errors.keys())==set((None, 'cc_card'))
    else:
        assert False, "there should be an error"
    data=dict(cc_card=cc,
              cc_type="Frog")
    try:
        s(data)
    except V.Invalid, e:
        errors=e.unpack_errors()
        assert set(errors.keys())==set((None, 'cc_type'))
    else:
        assert False, "there should be an error"
    

    

def test_url():
    v=V.url()
    u='http://www.wnyc.org/'
    assert v(u)==u
    v=V.url(True)
    assert v(u)==u
