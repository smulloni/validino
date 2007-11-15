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
            raise Invalid(_msg(f.msg,
                               'email.format',
                               'invalid format'))
        if not _usernameRE.match(username):
            raise Invalid(_msg(f.msg,
                               'email.username',
                               'invalid username'))
        if not _domainRE.match(domain):
            raise Invalid(_msg(f.msg,
                               'email.domain',
                               'invalid domain'))
        
        if f.check_dns:
            try:
                a=DNS.DnsRequest(domain, qtype='mx').req().answers
                if not a:
                    a=DNS.DnsRequest(domain, qtype='a').req().answers
                dnsdomains=[x['data'] for x in a]
	    except (socket.error, DNS.DNSError), e:
		raise Invalid(_msg(f.msg,
                                   'email.socket_error',
                                   'socket error'))
            if not dnsdomains:
                raise Invalid(_msg(f.msg,
                                   'email.domain_error',
                                   'no such domain'))
        return value
    f.check_dns=check_dns
    f.msg=msg
    return f


def credit_card(types=None,
                require_type=False,
                msg=None,
                cc_field='cc_number',
                cc_type_field='cc_type'):
    if types is None:
        types=_cc.cards
    def f(values):
        if isinstance(values, (list, tuple)):
            cardnumber, cc_type=values
        else:
            cardnumber, cc_type=values, None

        exc=Invalid()
        
        type_ok=not f.require_type
        
        if f.require_type and cc_type is None:
            m=_msg(f.msg,
                   "credit_card.require_type",
                   "no credit card type specified")
            exc.add_error_message(f.cc_type_field, m)

            
        elif not (cc_type is None) and cc_type not in f.types:
            m=_msg(f.msg,
                   "credit_card.type_check",
                   "unrecognized credit card type")
            exc.add_error_message(f.cc_type_field, m)

        else:
            type_ok=True

        try:
            if type_ok:
                _cc.check_credit_card(cardnumber, cc_type)
            else:
                _cc.check_credit_card(cardnumber)
        except _cc.CreditCardValidationException:
            m=_msg(f.msg,
                   "credit_card.invalid",
                   "invalid credit card number")
            exc.add_error_message(f.cc_field, m)

        if exc.errors:
            raise exc
        else:
            return values
    f.types=types
    f.require_type=require_type
    f.msg=msg
    f.cc_field=cc_field
    f.cc_type_field=cc_type_field
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

    def f(value):
        if f.check_exists and set(f.schemas).difference(set(('http', 'https'))):
            m="existence check not supported for schemas other than http and https"
            raise RuntimeError(m)        
        schema, netloc, path, params, query, fragment=urlparse.urlparse(value)
        if schema not in f.schemas:
            raise Invalid(_msg(f.msg,
                               "url.schema",
                               "schema not allowed"))
        if schema=='' and f.default_schema:
            schema=f.default_schema
        if netloc=='' and f.default_host:
            netloc=f.default_host


        url=urlparse.urlunparse((schema, netloc, path, params, query, fragment))
        if f.check_exists:
            newpath=urlparse.urlunparse(('', '', path, params, query, fragment))
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
                raise Invalid(_msg(f.msg,
                                   "url.http_error",
                                   "http error"))
            else:
                if 200 <= res.status < 400:
                    # this fudges on redirects.  
                    return url
                raise Invalid(_msg(f.msg,
                                   'url.not_exists',
                                   "url not OK"))
        return url
    f.default_schema=default_schema
    f.default_host=default_host
    f.check_exists=check_exists
    f.schemas=schemas
    f.msg=msg
    return f
