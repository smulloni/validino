"""
contains a function for validating credit card numbers.
Supported card types are MasterCard, Visa, Amex, Diners Club,
Carte Blanche, Discover, En Route, and JCB.

"""

import re
import operator

_numonlyRE=re.compile(r'[- ]')

##########################################################################
# taken from: http://www.beachnet.com/~hstiles/cardtype.html
##########################################################################
## CARD TYPE                 Prefix         Length  Check digit algorithm
## Mastercard                51-55          16      mod 10
## Visa                      4              13,16   mod 10
## Amex                      34,37          15      mod 10
## Diners Club/Carte Blanche 300-305,36,38  14      mod 10
## Discover                  6011           16      mod 10
## enRoute                   2014,2149      15      any
## JCB                       3              16      mod 10
## JCB                       2131, 1800     15      mod 10
##########################################################################

# info updated according to http://en.wikipedia.org/wiki/Credit_card_number


cards=(MASTERCARD,
       VISA,
       AMEX,
       DINERS_CLUB,
       CARTE_BLANCHE,
       DISCOVER,
       EN_ROUTE,
       JCB)=('MasterCard',
             'Visa',
             'American Express',
             'Diners Club',
             'Carte Blanche',
             'Discover',
             'En Route',
             'JCB')
          
card_table=[(MASTERCARD, '51', (16,)),
            (MASTERCARD, '52', (16,)),
            (MASTERCARD, '53', (16,)),
            (MASTERCARD, '54', (16,)),
            (MASTERCARD, '55', (16,)),
            (VISA, '4', (13, 16)),
            (AMEX, '34', (15,)),
            (AMEX, '37', (15,)),
            (DINERS_CLUB, '300', (14,)),
            (DINERS_CLUB, '301', (14,)),
            (DINERS_CLUB, '302', (14,)),
            (DINERS_CLUB, '303', (14,)),
            (DINERS_CLUB, '304', (14,)),
            (DINERS_CLUB, '305', (14,)),
            (DINERS_CLUB, '36', (14,)),
            (DINERS_CLUB, '38', (14,)),
            (CARTE_BLANCHE, '300', (14,)),
            (CARTE_BLANCHE, '301', (14,)),
            (CARTE_BLANCHE, '302', (14,)),
            (CARTE_BLANCHE, '303', (14,)),
            (CARTE_BLANCHE, '304', (14,)),
            (CARTE_BLANCHE, '305', (14,)),
            (CARTE_BLANCHE, '36', (14,)),
            (CARTE_BLANCHE, '38', (14,)),
            (DISCOVER, '6011', (16,)),
            (DISCOVER, '65', (16,)),
            (EN_ROUTE, '2014', (15,)),
            (EN_ROUTE, '2149', (15,)),
            (JCB, '3', (16,)),
            (JCB, '2131', (15,)),
            (JCB, '1800', (15,))]

card_prefix_map={}
prefix_card_map={}
prefix_length_map={}
prefixes=[]

for c in cards:
    card_prefix_map[c]=[]
for ct, prefix, lengths  in card_table:
    card_prefix_map[ct].append(prefix)
    prefix_card_map[prefix]=ct
    prefix_length_map[prefix]=lengths
    prefixes.append(prefix)
prefixes=[(len(x[1]), x[1]) for x in card_table]
prefixes.sort()
prefixes.reverse()
prefixes=[x[1] for x in prefixes]

def prefix_for_ccnum(ccnum):
    for p in prefixes:
        if ccnum.startswith(p):
            return p

def type_for_prefix(prefix):
    return prefix_card_map.get(prefix)

def length_for_prefix(prefix):
    return prefix_length_map.get(prefix)


class CreditCardValidationException(Exception):
    pass

class BadCreditCardTypeException(CreditCardValidationException):
    pass

class UnknownCreditCardPrefixException(CreditCardValidationException):
    pass

class CreditCardFormatException(CreditCardValidationException):
    pass

def check_credit_card(ccnum, cctype=None):
    """
    checks the cc number for improper characters, matches against the
    credit card type, if provided, checks the length of the credit
    card number, and verifies the check digit with Luhn's formula.
    Raises a CreditCardValidationException subclass on failing any of
    these tests.  However, if cctype is specified, and it is not
    a supported credit card type, a ValueError will be raised.
    """
    cc=_numonlyRE.sub('', ccnum)
    try:
        long(cc)
    except ValueError:
        raise CreditCardValidationException, \
              "bad characters in card number: %s" % cc
    prefix=prefix_for_ccnum(cc)
    if not prefix:
        raise UnknownCreditCardPrefixException, cc
    foundtype=type_for_prefix(prefix)
    if cctype is not None:
        if cctype not in cards:
            raise ValueError, "unrecognized card type: %s" % cctype
        if foundtype!=cctype:
            raise BadCreditCardTypeException, \
                  "expected %s, found %s" % (cctype, foundtype)
    realLengths=length_for_prefix(prefix)
    if not realLengths or len(cc) not in realLengths:
        raise CreditCardFormatException, "bad length"
    cc=map(int, list(cc))
    cc.reverse()
    s=0
    for i in range(len(cc)):
       s+=reduce(operator.add, divmod((1+(i%2))*cc[i], 10))
    # apparently En Route, whatever that is, doesn't use the check bit
    if foundtype!=EN_ROUTE and (s % 10) != 0:
        raise CreditCardFormatException, "wrong check digit"

def _gen_fake(cctype,
              start=None,
              num=1,
              prefix=None,
              length=None):
    """
    generates valid test credit cards, for testing.
    This isn't particularly efficient, as it simply
    cycles through numbers in sequence and tests
    them, rather than generating the check digits from
    the rest of the number.  But I have no reason to make
    this efficient.
    """
    if prefix is None:
        prefix=card_prefix_map[cctype][0]
    elif prefix not in card_prefix_map[cctype]:
        raise ValueError, "invalid prefix for card type: %s" % prefix
    if length is None:
        length=prefix_length_map[prefix][0]
    elif length not in prefix_length_map[prefix]:
        raise ValueError, \
              "invalid length for card prefix %s: %s" % (prefix, length)
    if start is None:
        start='%s%s' % (prefix, '0' * (length-len(prefix)))
    elif not (start.startswith(prefix) and len(start)==length):
        raise ValueError, "starting value %s inconsistent with "\
              "prefix %s and length %s" % (start, prefix, length)
    
    res=[]
    while 1:
        if len(start)!=length or not start.startswith(prefix):
            break
        try:
            check_credit_card(start, cctype)
            res.append(start)
            if num and len(res)>=num:
                break
        except CreditCardFormatException:
            pass
        start=str(long(start)+1)
    return res

        
     
    
