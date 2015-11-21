LDAP convenience library
========================

This Package provides objects for LDAP communication. 

LDAP Session
------------

You can work with the ``LDAPSession`` object.
::

    >>> from bda.ldap import ONELEVEL
    >>> from bda.ldap import LDAPSession
    >>> from bda.ldap import LDAPProps
    
    >>> props = LDAPProps('localhost',
    ...                   389,
    ...                   'cn=user,dc=example,dc=com',
    ...                   'secret'
    ...                   cache=True,
    ...                   timeout=12345)
    >>> session = LDAPSession(props)
    >>> res = session.search('(uid=*)', ONELEVEL)
    
LDAP Node
---------

You can build and edit LDAP data trees with the ``LDAPNode`` which is based on 
``zodict.Node``. 

The root Node expects the base DN and the server properties to initialize.
::

    >>> from bda.ldap import LDAPNode
    >>> root = LDAPNode('dc=my-domain,dc=com', props=props)
    >>> root.keys()
    ['ou=customers']

You can create and add new LDAP entries.
::

    >>> person = LDAPNode()
    >>> person.attributes['objectClass'] = ['top', 'person']
    >>> person.attributes['sn'] = 'Mustermann'
    >>> person.attributes['cn'] = 'Max'
    >>> person.attributes['description'] = 'Description'
    >>> customers['cn=max'] = person
    >>> customers.keys()
    ['cn=max']

On ``__call__`` the modifications of the tree are written to the directory.
::

    >>> customers()

Modification of entry attributes.
::

    >>> person.attributes['description'] = 'Another description'
    >>> person()
    
    >>> del person.attributes['description']
    >>> person()

Deleting of entries.
::

    >>> del customers['cn=max']
    >>> customers()

For more details see the corresponding source and test files.


Character Encoding
------------------

LDAP (v3 at least, `RFC 2251`_) uses utf8 string encoding. Since 1.5.1,
LDAPSession and LDAPNode translate these to unicodes for you. Consider it a
bug, if you receive anything else than unicode from LDAPSession or LDAPNode.
Everything below that LDAPConnector and LDAPCommunicator give you the real ldap
experience. - Should we change that, too?

Unicode strings you pass to nodes or sessions are automatically encoded to uft8
for LDAP. If you feed them normal strings they are decoded as utf8 and
reencoded as utf8 to make sure they are utf8 or compatible, e.g. ascii.

If decoding as utf8 fails, the value is assumed to be in binary and left as a
string (see TODO).

If you have an LDAP server that does not use utf8, monkey-patch
bda.ldap.strcodec.LDAP_CHARACTER_ENCODING.

If you are confused by all that encoding/decoding: python knows in what
encoding it stores its unicodes, however, it cannot know for normal strs.
Therefore, you should only use unicodes. In order to get a unicode for a str, a
string is decoded according to a given encoding schema (eg utf8). And encoding
a unicode produces a str in a specific encoding (eg utf8).

.. _`RFC 2251`: http://www.ietf.org/rfc/rfc2251.txt


Caching Support
---------------

``bda.ldap`` caches LDAP searches using the lightweight ``bda.cache``. You need 
to provide a utility in you application in order to make caching work. If you
dont, ``bda.ldap`` falls back to use the NullCache, which does not cache 
anything. 

To provide an cache based on ``Memcached`` install the memcached server,  
configure and start it. I suppose its started on localhost port 11211 (which is 
a common default). Then you need to provide a utility acting as a factory.  
::
    
    >>> from bda.ldap.cache import MemcachedProviderFactory
    >>> providerfactory = MemcachedProviderFactory()
    >>> from zope.component import provideUtility
    >>> provideUtility(providerfactory)
    
In the case you have more than one memcached server running or hav it running on 
another maschine, you need to initialize the factory different::    

    >>> providerfactory = MemcachedProviderFactory(servers=[10.0.0.10:22122,
    ...                                                     10.0.0.11:22322])
    >>> provideUtility(providerfactory)


Dependencies
============

- python-ldap

- zodict

- bda.cache


Notes on python-ldap
====================

There are different compile issues on different platforms. If you experience
problems with ``python-ldap``, make sure it is available in the python
environment you run buildout in, so it won't be fetched and build by buildout
itself.


TODO
====

- increase test coverage

- changed info and __call__ on user object

- adding ldap nodes, users, groups

- finish pas plugin

- figure out how and whether to merge attribute access into the basic node

- plone integration: bda.ploneldap
  - views for LDAPUsersConfig, LDAPGroupsConfig for the plone-control-panel
    working directly on the ones in bda.pasldap's multiplugin
  - nothing else, everything else -> bda.pasldap or better bda.ldap

- test with plone4

- figure out how to store config and when to create the users and groups
  folders

- control panel beautification: fieldsets, three tabs: server, users, groups

- config presets for common setups in bda.ldap, with loading/choosing support
  in bda.plone.ldap

- TLS/SSL Support. in LDAPConnector
  could be useful: python-ldap's class SmartLDAPObject(ReconnectLDAPObject) -
  Mainly the __init__() method does some smarter things like negotiating the
  LDAP protocol version and calling LDAPObject.start_tls_s().
  XXX: SmartLDAPObject has been removed from the most recent python-ldap,
  because of being too buggy.

- define how our retry logic should look like, rethink job of session,
  communicator and connector. (check ldap.ldapobject.ReconnectLDAPObject)
  ideas: more complex retry logic with fallback servers, eg. try immediately
  again, if fails use backup server, start to test other server after
  timespan, report status of ldap servers, preferred server, equal servers,
  load balance; Are there ldap load balancers to recommend?

- consider search_st with timeout.

- investigate ``ReconnectLDAPObject.set_cache_options``

- check/implement silent sort on only the keys LDAPNode.sortonkeys()

- binary attributes: 1. introduce Binary: ``node['cn=foo'].attrs['image']
  = Binary(stream)``, 2. parse ldap schema to identify binary attributes, also
  further types like BOOL

- improve test framework to support running of single tests, currently the
  setUp and tearDown are tests themselves run at the very beginning and end.
  Having them as setUp and tearDown for DocFileSuite is one way, but then they
  are run for every test, maybe even good. Nice would be an LDAPTestLayer, but
  I don't see how to achieve that without Testing.ZopeTestCase, which would
  mean to pull in the complete Zope2 for testing.
  It works by running prepareslapd.txt, then the single test(s), then
  stopslapd.txt.

- bda.ldap.filter unicode/utf-8 and tests

- unicode decorator

- auto-detection of rdn attribute

- interactive configuration showing life how many users/groups are found with
  the current config and how a selected user/group would look like

- test with plone3

Changes
=======

2.0 (unreleased)
----------------

- console support for starting/stopping a slapd using the test layers and data
  presets as desired in a temporary environment for application testing.
  (rnix, 2010-11-10)

- test layers with data presets
  (chaoflow, 2010-11-09)

- hidden support for _search_filter/_search_scope, see node.txt
  (chaoflow, 2010-07-20)

- hidden support for non-rdn key, see node.txt
  (chaoflow, 2010-07-20)

- parent caches child dns, ``__parent__.child_dn(key)``
  (chaoflow, 2010-07-20)

- dont unset parent's changed flag, if parent's attributes are changed
  (chaoflow, 2010-07-19)

- enable loading/modifying of root node's attributes
  (chaoflow, 2010-07-19)

- fixed _set_changed to properly protect parents changed flag, if the parent
  has other changed childs
  (chaoflow, 2010-07-19)

1.5.2
-----

- assume strings that fail to decode to be binary and leave them as-is
  (chaoflow, 2010-07-19)

- session.search, default filter ``'(objectClass=*)'`` and scope ``BASE``, i.e.
  just calling search returns the basedn entry. Further it is possible to call
  session.search(scope=ONELEVEL) to get all entries one level below the basedn.
  (chaoflow, 2010-07-19)

1.5.1
-----

- character encoding: LDAPSession and LDAPNode only return unicode and
  enforces utf8 or compatible encoding on all strings they receive,
  see ``Character Encoding``.
  (chaoflow, 2010-07-17)

- introduced strcodec module for unicode->str->unicode translation
  (chaoflow, 2010-07-17)

- add LDAPNode.get to use LDAPNode.__getitem__ instead of odict's
  (chaoflow, 2010-07-16)

- more tests, explode_dn for dn handling (with spaces and escaped commas)
  (chaoflow, 2010-07-16)

- ignore results with dn=None. ActiveDirectory produces them
  (chaoflow, 2010-07-15)

- default filter for session.search, if you pass '', u'' or None as filter
  (chaoflow, 2010-07-15)

- tests for attrlist and attrsonly
  (chaoflow, 2010-07-15)

- adopt for latest zodict.
  (rnix, 2010-07-15)

- added support for sort to node. Note: This wakes up all children of Node.
  (jensens, 2010-04-16) 

- added support for "items() to Node".
  (jensens, 2010-04-16) 

- BBB compatibility for zope2.9
  (rnix, jensens, 2010-02-17)

- If a Node was added and no child added __iter__ failed. Fixed now.
  (jensens, 2010-01-19) 

- If a Node was added we cant load its attributes. Takes this into account now.
  (jensens, 2010-01-17) 

1.5.0
-----

- Made ``MemcachedProviderFactory`` configurable. Defaults behave like in prior
  versions. New: We can pass ``server=`` keyword argument to the 
  constructor expecting a list of servers, each in the form *server:port*.
  (jensens, 2009-12-30)

- Dont provide any cache provider factory by default. Added a 
  ``nullCacheProviderFactory`` which  provides a non-caching behaviour. Use this
  as fallback if no utility was registered.   
  (jensens, 2009-12-30)

- Add read property ``ldap_session`` to ``LDAPNode``. This way its clean to take  
  the session of ``LDAPNode`` in an application i.e. for searching. Be careful 
  while using the session directly to manipulate the LDAP; responsibility to 
  invalidate the ``LDAPNode`` instances is on the application developer.
  (jensens, 2009-12-30)

1.4.0
-----

- Add ``LDAPProps`` object. Its points to ``LDAPServerProperties`` class. The
  latter one will be renamed to ``LDAPProps`` in version 1.5. Too long class
  name. (rnix, 2009-12-23)

- Add ``LDAPSession.unbind`` function. (rnix, 2009-12-23)

- Add some tests for ``LDAPSession``. (rnix, 2009-12-23)

- Remove deprecated ``cache`` kwarg from ``LDAPSession.__init__.``. Cache
  timeout and flag if cache is enabled is done due to ``LDAPServerProperties``.
  (rnix, 2009-12-23)

- Deprecate Signature of ``LDAPConnector.__init__``. (rnix, 2009-12-23)

- Deprecate ``LDAPConnector.setProtocol``, ``LDAPCommunicator.setBaseDN``,
  ``LDAPCommunicator.getBaseDN``, ``LDAPSession.setBaseDN``. (rnix, 2009-12-23)
  
- Refactor the whole ``LDAPNode`` to use ``zodict.LifecycleNode``. Clean up of
  the ``LDAPNode`` code. (jensens, rnix, 2009-12-22)

- improved stop mechanism of ldap server in tests (jensens, 2009-12-16)

- remove deprecation warning: use `hashlib` for md5 and fallback to `md5`  
  with python2.4. (jensens, 2009-12-16)

1.3.2
-----

- handle timeout of cache, workaround atm (rnix, 2009-09-02)

1.3.1
-----

- add ``cache`` property to ``LDAPProperties``. (rnix, 2009-05-08)

- modify session to fit this new cache property. (rnix, 2009-05-07)

- add ``queryNode`` function. (rnix, 2009-05-07)

- add ``get`` function to node, this failed due LDAP read logic.
  (rnix, 2009-05-07)

1.3
---

- support ``attrlist`` and ``attrsonly`` for search functions.
  (rnix, 2009-04-16)

- add LDAPEntry object. (rnix, 2009-04-16)

- add search base to cache key. (rnix, 2009-04-16)

1.2.3
-----

- bugfix in ``LDAPSession``. Pass ``force_reload`` to relevant execution
  function. (rnix, 2009-02-11)

1.2.2
-----

- add buildout for standalone testing. (rnix, jensens - 2009-02-11)

- add tests. (rnix, jensens - 2009-02-11)

- provide relevant objects via package ``__init__``.
  (rnix, jensens - 2009-02-11)

1.2.1
-----

- provide same ``search()`` signature in ``LDAPSession`` as
  in ``LDAPCommunicator``. (rnix - 2009-02-10)
  
- log only on debug. (rnix - 2009-02-10)

<= 1.2
------

- make it work. 
  (all contributors)

Copyright
=========

Copyright (c) 2006-2009: BlueDynamics Alliance, Austria

Contributors
============

- Florian Friesdorf <flo@chaoflow.net>

- Robert Niederreiter <rnix@squarewave.at>

- Jens Klein <jens@bluedynamics.com>

- Georg Bernhard <g.bernhard@akbild.ac.at>

- Johannes Raggam <johannes@bluedynamics.com>
