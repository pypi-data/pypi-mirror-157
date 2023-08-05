# coding: utf-8

"""
    Events Ingestion API

    The Observation platform's Events Ingestion API  # noqa: E501

    OpenAPI spec version: 1.0.0
    Contact: support@datakitchen.io
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class HTTPErrorSchema(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'details': 'object',
        'error': 'str'
    }

    attribute_map = {
        'details': 'details',
        'error': 'error'
    }

    def __init__(self, details=None, error=None):  # noqa: E501
        """HTTPErrorSchema - a model defined in Swagger"""  # noqa: E501
        self._details = None
        self._error = None
        self.discriminator = None
        if details is not None:
            self.details = details
        if error is not None:
            self.error = error

    @property
    def details(self):
        """Gets the details of this HTTPErrorSchema.  # noqa: E501


        :return: The details of this HTTPErrorSchema.  # noqa: E501
        :rtype: object
        """
        return self._details

    @details.setter
    def details(self, details):
        """Sets the details of this HTTPErrorSchema.


        :param details: The details of this HTTPErrorSchema.  # noqa: E501
        :type: object
        """

        self._details = details

    @property
    def error(self):
        """Gets the error of this HTTPErrorSchema.  # noqa: E501


        :return: The error of this HTTPErrorSchema.  # noqa: E501
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error):
        """Sets the error of this HTTPErrorSchema.


        :param error: The error of this HTTPErrorSchema.  # noqa: E501
        :type: str
        """

        self._error = error

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(HTTPErrorSchema, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, HTTPErrorSchema):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
