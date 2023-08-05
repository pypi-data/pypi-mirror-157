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

class TestReport(object):
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
        'description': 'str',
        'name': 'str',
        'status': 'str'
    }

    attribute_map = {
        'description': 'description',
        'name': 'name',
        'status': 'status'
    }

    def __init__(self, description=None, name=None, status=None):  # noqa: E501
        """TestReport - a model defined in Swagger"""  # noqa: E501
        self._description = None
        self._name = None
        self._status = None
        self.discriminator = None
        if description is not None:
            self.description = description
        self.name = name
        self.status = status

    @property
    def description(self):
        """Gets the description of this TestReport.  # noqa: E501

        Optional description of the test results.  # noqa: E501

        :return: The description of this TestReport.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this TestReport.

        Optional description of the test results.  # noqa: E501

        :param description: The description of this TestReport.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def name(self):
        """Gets the name of this TestReport.  # noqa: E501

        The name of the test.  # noqa: E501

        :return: The name of this TestReport.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this TestReport.

        The name of the test.  # noqa: E501

        :param name: The name of this TestReport.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def status(self):
        """Gets the status of this TestReport.  # noqa: E501

        The reported state of the named test.  # noqa: E501

        :return: The status of this TestReport.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this TestReport.

        The reported state of the named test.  # noqa: E501

        :param status: The status of this TestReport.  # noqa: E501
        :type: str
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501
        allowed_values = ["PASSED", "FAILED", "WARNING"]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"  # noqa: E501
                .format(status, allowed_values)
            )

        self._status = status

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
        if issubclass(TestReport, dict):
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
        if not isinstance(other, TestReport):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
