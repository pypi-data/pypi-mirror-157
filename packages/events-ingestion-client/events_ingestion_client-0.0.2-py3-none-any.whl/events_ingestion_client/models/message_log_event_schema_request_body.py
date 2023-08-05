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

class MessageLogEventSchemaRequestBody(object):
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
        'event_timestamp': 'datetime',
        'log_level': 'str',
        'message': 'str',
        'metadata': 'object',
        'pipeline_name': 'str',
        'project_id': 'str',
        'run_tag': 'str',
        'task_name': 'str'
    }

    attribute_map = {
        'event_timestamp': 'event_timestamp',
        'log_level': 'log_level',
        'message': 'message',
        'metadata': 'metadata',
        'pipeline_name': 'pipeline_name',
        'project_id': 'project_id',
        'run_tag': 'run_tag',
        'task_name': 'task_name'
    }

    def __init__(self, event_timestamp=None, log_level=None, message=None, metadata=None, pipeline_name=None, project_id=None, run_tag=None, task_name=None):  # noqa: E501
        """MessageLogEventSchemaRequestBody - a model defined in Swagger"""  # noqa: E501
        self._event_timestamp = None
        self._log_level = None
        self._message = None
        self._metadata = None
        self._pipeline_name = None
        self._project_id = None
        self._run_tag = None
        self._task_name = None
        self.discriminator = None
        if event_timestamp is not None:
            self.event_timestamp = event_timestamp
        self.log_level = log_level
        self.message = message
        if metadata is not None:
            self.metadata = metadata
        self.pipeline_name = pipeline_name
        self.project_id = project_id
        if run_tag is not None:
            self.run_tag = run_tag
        if task_name is not None:
            self.task_name = task_name

    @property
    def event_timestamp(self):
        """Gets the event_timestamp of this MessageLogEventSchemaRequestBody.  # noqa: E501

        An ISO8601 timestamp that describes when the event occurred. If unset, the Events Ingestion API applies its current time to the field.  # noqa: E501

        :return: The event_timestamp of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: datetime
        """
        return self._event_timestamp

    @event_timestamp.setter
    def event_timestamp(self, event_timestamp):
        """Sets the event_timestamp of this MessageLogEventSchemaRequestBody.

        An ISO8601 timestamp that describes when the event occurred. If unset, the Events Ingestion API applies its current time to the field.  # noqa: E501

        :param event_timestamp: The event_timestamp of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: datetime
        """

        self._event_timestamp = event_timestamp

    @property
    def log_level(self):
        """Gets the log_level of this MessageLogEventSchemaRequestBody.  # noqa: E501

        Required. Log level for the associated message.  # noqa: E501

        :return: The log_level of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: str
        """
        return self._log_level

    @log_level.setter
    def log_level(self, log_level):
        """Sets the log_level of this MessageLogEventSchemaRequestBody.

        Required. Log level for the associated message.  # noqa: E501

        :param log_level: The log_level of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: str
        """
        if log_level is None:
            raise ValueError("Invalid value for `log_level`, must not be `None`")  # noqa: E501
        allowed_values = ["ERROR", "WARNING", "INFO"]  # noqa: E501
        if log_level not in allowed_values:
            raise ValueError(
                "Invalid value for `log_level` ({0}), must be one of {1}"  # noqa: E501
                .format(log_level, allowed_values)
            )

        self._log_level = log_level

    @property
    def message(self):
        """Gets the message of this MessageLogEventSchemaRequestBody.  # noqa: E501

        Required. Log message. Cannot be empty.  # noqa: E501

        :return: The message of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """Sets the message of this MessageLogEventSchemaRequestBody.

        Required. Log message. Cannot be empty.  # noqa: E501

        :param message: The message of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: str
        """
        if message is None:
            raise ValueError("Invalid value for `message`, must not be `None`")  # noqa: E501

        self._message = message

    @property
    def metadata(self):
        """Gets the metadata of this MessageLogEventSchemaRequestBody.  # noqa: E501

        Arbitrary key-value information, supplied by the user, to apply to the event.  # noqa: E501

        :return: The metadata of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: object
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this MessageLogEventSchemaRequestBody.

        Arbitrary key-value information, supplied by the user, to apply to the event.  # noqa: E501

        :param metadata: The metadata of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: object
        """

        self._metadata = metadata

    @property
    def pipeline_name(self):
        """Gets the pipeline_name of this MessageLogEventSchemaRequestBody.  # noqa: E501

        Required. The target pipeline for the event action..  # noqa: E501

        :return: The pipeline_name of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: str
        """
        return self._pipeline_name

    @pipeline_name.setter
    def pipeline_name(self, pipeline_name):
        """Sets the pipeline_name of this MessageLogEventSchemaRequestBody.

        Required. The target pipeline for the event action..  # noqa: E501

        :param pipeline_name: The pipeline_name of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: str
        """
        if pipeline_name is None:
            raise ValueError("Invalid value for `pipeline_name`, must not be `None`")  # noqa: E501

        self._pipeline_name = pipeline_name

    @property
    def project_id(self):
        """Gets the project_id of this MessageLogEventSchemaRequestBody.  # noqa: E501

        The project ID. Temporary until SA keys are supported.  # noqa: E501

        :return: The project_id of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this MessageLogEventSchemaRequestBody.

        The project ID. Temporary until SA keys are supported.  # noqa: E501

        :param project_id: The project_id of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: str
        """
        if project_id is None:
            raise ValueError("Invalid value for `project_id`, must not be `None`")  # noqa: E501

        self._project_id = project_id

    @property
    def run_tag(self):
        """Gets the run_tag of this MessageLogEventSchemaRequestBody.  # noqa: E501

        The tag of the target run for the event action. This identifier is created and managed by the user. If no run_tag is specified, the event applies to the default open run for the pipeline.  # noqa: E501

        :return: The run_tag of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: str
        """
        return self._run_tag

    @run_tag.setter
    def run_tag(self, run_tag):
        """Sets the run_tag of this MessageLogEventSchemaRequestBody.

        The tag of the target run for the event action. This identifier is created and managed by the user. If no run_tag is specified, the event applies to the default open run for the pipeline.  # noqa: E501

        :param run_tag: The run_tag of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: str
        """

        self._run_tag = run_tag

    @property
    def task_name(self):
        """Gets the task_name of this MessageLogEventSchemaRequestBody.  # noqa: E501

        Optional. The target task for the event action. Must be unique within a pipeline.  # noqa: E501

        :return: The task_name of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :rtype: str
        """
        return self._task_name

    @task_name.setter
    def task_name(self, task_name):
        """Sets the task_name of this MessageLogEventSchemaRequestBody.

        Optional. The target task for the event action. Must be unique within a pipeline.  # noqa: E501

        :param task_name: The task_name of this MessageLogEventSchemaRequestBody.  # noqa: E501
        :type: str
        """

        self._task_name = task_name

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
        if issubclass(MessageLogEventSchemaRequestBody, dict):
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
        if not isinstance(other, MessageLogEventSchemaRequestBody):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
