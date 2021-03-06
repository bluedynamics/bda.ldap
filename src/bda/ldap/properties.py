# Copyright 2008-2009, BlueDynamics Alliance, Austria - http://bluedynamics.com
# GNU General Public Licence Version 2 or later

from zope.interface import implements
from bda.ldap.interfaces import ILDAPProps

class LDAPServerProperties(object):
    """Wrapper Class for LDAP Server connection properties.
    """
    implements(ILDAPProps)
    
    def __init__(self,
                 server=None,
                 port=None,
                 user='',
                 password='',
                 cache=True,
                 timeout=43200,
                 uri=None,
                 #start_tls=1,
                 #tls_cacertfile=None,
                 #tls_cacertdir=None,
                 #tls_clcertfile=None,
                 #tls_clkeyfile=None,
                 retry_max=1,
                 retry_delay=10.0,
                 ):
        """Take the connection properties as arguments.
        
	 SSL/TLS still unsupported

        @param server: DEPRECATED use uri! servername, defaults to 'localhost'
        @param port: DEPRECATED uss uri! server port, defaults to 389
        @param user: username to bind, defaults to ''
        @param password: password to bind, defaults to ''
        @param cache: Bool wether to enable caching or not, defaults to True
        @param timeout: Cache timeout in seconds. only takes affect if cache
                        is enabled.
        @param uri: overrides server/port, forget about server and port, use
        this to specify how to access the ldap server, eg:
            - ldapi:///path/to/socket
            - ldap://<server>:<port> (will try start_tls, which you can
              enforce, see start_tls)
            - ldaps://<server>:<port>
        @param start_tls: Determines if StartTLS extended operation is tried on
        a LDAPv3 server, iff the LDAP URL scheme is ldap:. If LDAP URL scheme
        is not ldap: (e.g. ldaps: or ldapi:) this parameter is ignored.
            0       Don't use StartTLS ext op
            1       Try StartTLS ext op but proceed when unavailable
            2       Try StartTLS ext op and re-raise exception if it fails
        @param tls_cacertfile:
        @param tls_cacertdir:
        @param tls_clcertfile:
        @param tls_clkeyfile:
        @param retry_max: Maximum count of reconnect trials
        @param retry_delay: Time span to wait between two reconnect trials
        """
        if uri is None:
            # old school
            self.server = server or 'localhost'
            self.port = port or 389
            uri = "ldap://%s:%d/" % (self.server, self.port)
        self.uri = uri
        self.user = user
        self.password = password
        self.cache = cache
        self.timeout = timeout
        #self.start_tls = start_tls
        #self.tls_cacertfile = tls_cacertfile
        #self.tls_cacertdir = tls_cacertdir
        #self.tls_clcertfile = tls_clcertfile
        #self.tls_clkeyfile = tls_clkeyfile
        self.retry_max = retry_max
        self.retry_delay = retry_delay

LDAPProps = LDAPServerProperties
