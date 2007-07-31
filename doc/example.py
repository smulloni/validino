"""
an example validator.
"""
import re

from validino import *

VALID_STATES=['NJ', 'NY', 'CT', 'AZ']

def convert_telephone(tel):
    pat='(\d{3})[/-]?(\d{3})-?(\d{4})'
    m=re.match(pat, tel)
    if m:
        return ''.join(m.groups())
    raise Invalid("Please enter a valid telephone number (e.g., 555-123-4567)")



validators=dict(
    spank_level=either(empty(),
                       equal('other'),
                       integer("Please enter a valid number of spanks")),
    preference=either(empty(),
                      belongs(['chicken',
                               'fish',
                               'monkey brains',
                               'soy meal'])),
    honorific=either(empty(), belongs(['Dr.', 'Mr.',
                                       'Ms.', 'Mrs.',
                                       'Rear Admiral'])),
    firstname=(strip,
               not_empty("Please enter a first name"),
               clamp_length(min=1, max=20)),
    middlename=(strip,
                either(empty(),
                       clamp_length(max=20))),
    lastname=(strip,
              not_empty("Please enter a last name"),
              clamp_length(min=1, max=40)),
    address1=(strip,
              not_empty("Please enter an address"),
              clamp_length(min=1, max=40)),
    address2=(strip,
              clamp_length(max=40)),
    city=(strip,
          not_empty("Please enter a city"),
          clamp_length(min=1, max=30)),
    state=(default(''), belongs(VALID_STATES)),
    zip_code=(strip,
              not_empty("Please enter a zip code"),
              clamp_length(max=5)),
    zip_extension=(strip,
                   default(''),
                   clamp_length(max=4)),
    phone=(strip,
           either(empty(),
                  convert_telephone)),
    email=(not_empty("Please enter an email address"),
           email("Please enter a valid email address")),
    email_confirm=lambda x: x,
    comment=(strip,
             default(''),
             clamp_length(max=200)))

validators[('email',
            'email_confirm')]=\
            fields_equal(msg='Please re-enter your email address',
                         field='email_confirm')
schema=Schema(validators,
              msg="The submitted data contains naughty errors.",
              allow_extra=True,
              allow_missing=True)

data=getDataFromSomewhere()

try:
    converted=schema(data)
except Invalid, e:
    errors=e.unpack_errors()
    doSomethingWithErrors(errors, data)
else:
    goToTown(converted)

    
