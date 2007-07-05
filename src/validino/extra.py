"""
Some validators commonly used in web applications.
"""

import httplib
import re
import socket
import urlparse

from validino.base import Invalid, _msg, regex
import validino.ccvalidate as _cc
from validino.util import partial

# lifted from formencode
_usernameRE = re.compile(r"^[^ \t\n\r@<>()]+$", re.I)
_domainRE = re.compile(r"^[a-z0-9][a-z0-9\.\-_]*\.[a-z]+$", re.I)

try:
    import DNS
except ImportError:
    DNS=None
else:
    DNS.DiscoverNameServers()

__all__=['email',
         'credit_card',
         'ip',
         'url']


def email(check_dns=False, msg=None):
    if check_dns and DNS is None:
        raise RuntimeError, "pyDNS not installed, cannot check DNS"
    def f(value):
        try:
            username, domain=value.split('@', 1)
        except ValueError:
            raise Invalid(_msg(msg,
                               'email.format',
                               'invalid format'))
        if not _usernameRE.match(username):
            raise Invalid(_msg(msg,
                               'email.username',
                               'invalid username'))
        if not _domainRE.match(domain):
            raise Invalid(_msg(msg,
                               'email.domain',
                               'invalid domain'))
        
        if check_dns:
            try:
                a=DNS.DnsRequest(domain, qtype='mx').req().answers
                if not a:
                    a=DNS.DnsRequest(domain, qtype='a').req().answers
                dnsdomains=[x['data'] for x in a]
	    except (socket.error, DNS.DNSError), e:
		raise Invalid(_msg(msg,
                                   'email.socket_error',
                                   'socket error'))
            if not dnsdomains:
                raise Invalid(_msg(msg,
                                   'email.domain_error',
                                   'no such domain'))
        return value
            
    return f


def credit_card(types=None, require_type=False, msg=None):
    if types is None:
        types=_cc.cards
    def f(values):
        if isinstance(values, (list, tuple)):
            cardnumber, cc_type=values
        else:
            cardnumber, cc_type=values, None
        if require_type and cc_type is None:
            raise Invalid(_msg(msg,
                               "credit_card.require_type",
                               "no credit card type specified"))
        if not (cc_type is None) and cc_type not in types:
            raise Invalid(_msg(msg,
                               "credit_card.type_check",
                               "unrecognized credit card type"))
        try:
            _cc.check_credit_card(cardnumber, cc_type)
        except _cc.CreditCardValidationException, e:
            raise Invalid(_msg(msg,
                               "credit_card.invalid",
                               "invalid credit card number"),
                          subexceptions=[e])
        else:
            return values
        
    return f
                               
_ip_pat='^%s$' % r'\.'.join(['|'.join([str(x) for x in range(256)]*4)])

ip=partial(regex, _ip_pat)
ip.__doc__="""

Returns a validator that tests whether an ip address is properly formed.

"""

def url(check_exists=False,
        schemas=('http', 'https'),
        default_schema='http',
        default_host='',
        msg=None):
    if check_exists and set(schemas).difference(set('http', 'https')):
        m="existence check not supported for schemas other than http and https"
        raise RuntimeError(m)
    def f(value):
        schema, netloc, path, params, query, fragment=urlparse.urlparse(value)
        if schema not in schemas:
            raise Invalid(_msg(msg,
                               "url.schema",
                               "schema not allowed"))
        if schema=='' and default_schema:
            schema=default_schema
        if netloc=='' and default_host:
            netloc=default_host


        url=urlparse.urlunparse(schema, netloc, path, params, query, fragment)
        if check_exists:
            newpath=urlparse.urlunparse('', '', path, params, query, fragment)
            if schema=='http':
                conn=httplib.HTTPConnection
            elif schema=='https':
                conn=httplib.HTTPSConnection
            else:
                assert False, "not reached"
            try:
                c=conn(netloc)
                c.request('HEAD', newpath)
                res=c.getresponse()
            except (httplib.HTTPException, socket.error), e:
                raise Invalid(_msg(msg,
                                   "url.http_error",
                                   "http error"))
            else:
                if 200 <= res.status < 400:
                    # this fudges on redirects.  
                    return url
                raise Invalid(_msg(msg,
                                   'url.not_exists',
                                   "url not OK"))
        return url
