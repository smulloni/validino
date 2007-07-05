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


def test_credit_card():
    cc='4000000000998'
    v=V.credit_card(msg="aha")
    assert v(cc)==cc
    assert_invalid(lambda: v('pain chocolat'), 'aha')
    assert_invalid(lambda: v(str(int(cc)-1)), 'aha')
    v=V.credit_card(require_type=True,  msg='aha')
    assert v((cc, 'Visa'))==(cc, 'Visa')

def test_url():
    v=V.url()
    u='http://www.wnyc.org/'
    assert v(u)==u
    v=V.url(True)
    assert v(u)==u
