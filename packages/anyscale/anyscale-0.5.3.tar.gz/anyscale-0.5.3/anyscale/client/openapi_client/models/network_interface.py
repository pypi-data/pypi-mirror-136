# coding: utf-8

"""
    Managed Ray API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from openapi_client.configuration import Configuration


class NetworkInterface(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'subnet_id': 'str',
        'groups': 'list[str]',
        'associate_public_ip_address': 'bool'
    }

    attribute_map = {
        'subnet_id': 'SubnetId',
        'groups': 'Groups',
        'associate_public_ip_address': 'AssociatePublicIpAddress'
    }

    def __init__(self, subnet_id=None, groups=None, associate_public_ip_address=True, local_vars_configuration=None):  # noqa: E501
        """NetworkInterface - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._subnet_id = None
        self._groups = None
        self._associate_public_ip_address = None
        self.discriminator = None

        self.subnet_id = subnet_id
        self.groups = groups
        if associate_public_ip_address is not None:
            self.associate_public_ip_address = associate_public_ip_address

    @property
    def subnet_id(self):
        """Gets the subnet_id of this NetworkInterface.  # noqa: E501


        :return: The subnet_id of this NetworkInterface.  # noqa: E501
        :rtype: str
        """
        return self._subnet_id

    @subnet_id.setter
    def subnet_id(self, subnet_id):
        """Sets the subnet_id of this NetworkInterface.


        :param subnet_id: The subnet_id of this NetworkInterface.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and subnet_id is None:  # noqa: E501
            raise ValueError("Invalid value for `subnet_id`, must not be `None`")  # noqa: E501

        self._subnet_id = subnet_id

    @property
    def groups(self):
        """Gets the groups of this NetworkInterface.  # noqa: E501


        :return: The groups of this NetworkInterface.  # noqa: E501
        :rtype: list[str]
        """
        return self._groups

    @groups.setter
    def groups(self, groups):
        """Sets the groups of this NetworkInterface.


        :param groups: The groups of this NetworkInterface.  # noqa: E501
        :type: list[str]
        """
        if self.local_vars_configuration.client_side_validation and groups is None:  # noqa: E501
            raise ValueError("Invalid value for `groups`, must not be `None`")  # noqa: E501

        self._groups = groups

    @property
    def associate_public_ip_address(self):
        """Gets the associate_public_ip_address of this NetworkInterface.  # noqa: E501


        :return: The associate_public_ip_address of this NetworkInterface.  # noqa: E501
        :rtype: bool
        """
        return self._associate_public_ip_address

    @associate_public_ip_address.setter
    def associate_public_ip_address(self, associate_public_ip_address):
        """Sets the associate_public_ip_address of this NetworkInterface.


        :param associate_public_ip_address: The associate_public_ip_address of this NetworkInterface.  # noqa: E501
        :type: bool
        """

        self._associate_public_ip_address = associate_public_ip_address

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
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

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, NetworkInterface):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, NetworkInterface):
            return True

        return self.to_dict() != other.to_dict()
