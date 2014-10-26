from __future__ import unicode_literals
import argparse
import logging
import troposphere

__version__ = '1.0.0'

logger = logging.getLogger(__name__)



class AWSProvided(object):
    pass


class Parameter(object):
    type_cls = troposphere.Parameter

    @property
    def Description(self):
        return self.__doc__


class StringParameter(Parameter):
    Type = 'String'

    def __init__(self):
        super(StringParameter, self).__init__()
        name = self.__class__.__name__

        properties = {}
        # collect properties
        for property_name in self.type_cls.props.iterkeys():
            try:
                properties[property_name] = getattr(self, property_name)
            except AttributeError:
                pass

        self._x = self.type_cls(name, **properties)

    def JSONrepr(self):
        return self._x.JSONrepr()


class Mapping(object):
    pass

