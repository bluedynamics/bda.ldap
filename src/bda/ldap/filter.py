from ldap.filter import filter_format

class LDAPFilter(object):
    def __init__(self, queryFilter=None):
        # We expect queryFilter to be correctly escaped
        if queryFilter is not None and not isinstance(queryFilter, basestring) and not isinstance(queryFilter, LDAPFilter):
            raise TypeError('Query filter must be string')

        self._filter = queryFilter
        if isinstance(queryFilter, LDAPFilter):
            self._filter = queryFilter.__str__()

    def __and__(self, other):
        if other is None:
            return self
        res = ''
        if isinstance(other, LDAPFilter):
            other = other.__str__()
        elif not isinstance(other, basestring):
            raise TypeError(u"unsupported operand type")
        us = self.__str__()
        if us and other:
            res = '(&%s%s)' % (us, other)
        elif us:
            res = us
        elif other:
            res = other
        return LDAPFilter(res)

    def __or__(self, other):
        if other is None:
            return self
        res = ''
        if isinstance(other, LDAPFilter):
            other = other.__str__()
        elif not isinstance(other, basestring):
            raise TypeError(u"unsupported operand type")
        us = self.__str__()
        if us and other:
            res = '(|%s%s)' % (us, other)
        return LDAPFilter(res)

    def __contains__(self, attr):
        attr = '(%s=' % (attr,)
        return attr in self._filter

    def __str__(self):
        return self._filter and self._filter or ''

    def __repr__(self):
        return "LDAPFilter('%s')" % (self._filter,)


class LDAPDictFilter(LDAPFilter):
    def __init__(self, criteria, or_search=False):
        self.criteria = criteria
        self.or_search = or_search

    def __str__(self):
        return self.criteria and dict_to_filter(criteria=self.criteria, or_search=self.or_search).__str__() or ''

    def __repr__(self):
        return "LDAPDictFilter(criteria=%r)" (self.criteria,)

class FooNode(object):
    def __init__(self, attrs):
        self.attrs = attrs

class LDAPRelationFilter(LDAPFilter):
    def __init__(self, node, relation):
	self.relation = relation
        self.gattrs = node.attrs


    def __str__(self):
        """turn relation string into ldap filter string
        """
        _filter = LDAPFilter()
        dictionary = dict()

        parsedRelation = dict((k,v) for (k,_,v) in (pair.partition(':') for
            pair in self.relation.split('|'))) 

        for k,v in parsedRelation.items():
            if str(v) == '' or str(k) == '' or str(k) not in self.gattrs:
                #might be inefficient, wip
                continue
            dictionary[v.__str__()] = self.gattrs[k.__str__()]

        self.dictionary = dictionary

        if len(dictionary) is 1:
            _filter = LDAPFilter(self.relation)
        else:
            _filter = dict_to_filter(parsedRelation, True)

	return self.dictionary and dict_to_filter(criteria=self.dictionary,
                or_search=True ).__str__() or ''

def dict_to_filter(criteria, or_search):
    """Turn dictionary criteria into ldap queryFilter string
    """
    _filter = None
    for attr, values in criteria.items():
        if not isinstance(values, list):
            values = [values]
	if ( or_search ):
		for value in values:
		    if _filter is None:
                        _filter = LDAPFilter( '(%s=%s)' % (attr, value))
                    else:
                        _filter |= '(%s=%s)' % (attr, value)
	else:
		for value in values:
                    if _filter is None:
                        _filter = LDAPFilter( '(%s=%s)' % (attr, value))
                    else:
			_filter &= '(%s=%s)' % (attr, value)
        if _filter is None:
            _filter = LDAPFilter()

    return _filter
