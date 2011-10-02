# -*- coding: utf-8 -*-

from django.db import models
from django.utils import simplejson

from limited.utils import TreeNode


class JsonTreeField( models.TextField ):
    """
    A simple JSON filed. Store text in database and TreeNode in python.
    """
    __metaclass__ = models.SubfieldBase

    description = "Json Tree object"

    def get_db_prep_value(self, value):
        if value == '' or value == None:
            return None
        json = value.toDict()
        return simplejson.dumps(json)

    def to_python(self, value):
        if value == '' or value == None:
            return None
        if not isinstance(value, basestring):
            return value
        DictData = simplejson.loads(value)
        return TreeNode.build( DictData )