from __future__ import with_statement

import validino as V
from validino.messages import msg, getMessages
from util import assert_invalid

def test_msg():
    messages=dict(
        integer="hey, I said use a number")
    with msg(messages):
        assert messages == getMessages()
        assert_invalid(lambda: V.integer()('lump'), messages['integer'])
    assert getMessages() == {}
    assert_invalid(lambda: V.integer()('lump'), "not an integer")
