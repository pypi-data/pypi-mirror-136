# coding: utf-8

"""
    Anyscale API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from anyscale_client.configuration import Configuration


class JobsQuery(object):
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
        'name': 'TextQuery',
        'runtime_environment_id': 'str',
        'cluster_id': 'str',
        'creator_id': 'str',
        'ray_job_id': 'str',
        'project_id': 'str',
        'include_child_jobs': 'bool',
        'ha_job_id': 'str',
        'show_ray_client_runs_only': 'bool',
        'paging': 'PageQuery',
        'state_filter': 'list[BaseJobStatus]',
        'type_filter': 'list[JobRunType]'
    }

    attribute_map = {
        'name': 'name',
        'runtime_environment_id': 'runtime_environment_id',
        'cluster_id': 'cluster_id',
        'creator_id': 'creator_id',
        'ray_job_id': 'ray_job_id',
        'project_id': 'project_id',
        'include_child_jobs': 'include_child_jobs',
        'ha_job_id': 'ha_job_id',
        'show_ray_client_runs_only': 'show_ray_client_runs_only',
        'paging': 'paging',
        'state_filter': 'state_filter',
        'type_filter': 'type_filter'
    }

    def __init__(self, name=None, runtime_environment_id=None, cluster_id=None, creator_id=None, ray_job_id=None, project_id=None, include_child_jobs=False, ha_job_id=None, show_ray_client_runs_only=True, paging=None, state_filter=[], type_filter=[], local_vars_configuration=None):  # noqa: E501
        """JobsQuery - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._runtime_environment_id = None
        self._cluster_id = None
        self._creator_id = None
        self._ray_job_id = None
        self._project_id = None
        self._include_child_jobs = None
        self._ha_job_id = None
        self._show_ray_client_runs_only = None
        self._paging = None
        self._state_filter = None
        self._type_filter = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if runtime_environment_id is not None:
            self.runtime_environment_id = runtime_environment_id
        if cluster_id is not None:
            self.cluster_id = cluster_id
        if creator_id is not None:
            self.creator_id = creator_id
        if ray_job_id is not None:
            self.ray_job_id = ray_job_id
        if project_id is not None:
            self.project_id = project_id
        if include_child_jobs is not None:
            self.include_child_jobs = include_child_jobs
        if ha_job_id is not None:
            self.ha_job_id = ha_job_id
        if show_ray_client_runs_only is not None:
            self.show_ray_client_runs_only = show_ray_client_runs_only
        if paging is not None:
            self.paging = paging
        if state_filter is not None:
            self.state_filter = state_filter
        if type_filter is not None:
            self.type_filter = type_filter

    @property
    def name(self):
        """Gets the name of this JobsQuery.  # noqa: E501

        Filters Jobs by name. If this field is absent, no filtering is done.  # noqa: E501

        :return: The name of this JobsQuery.  # noqa: E501
        :rtype: TextQuery
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this JobsQuery.

        Filters Jobs by name. If this field is absent, no filtering is done.  # noqa: E501

        :param name: The name of this JobsQuery.  # noqa: E501
        :type: TextQuery
        """

        self._name = name

    @property
    def runtime_environment_id(self):
        """Gets the runtime_environment_id of this JobsQuery.  # noqa: E501

        Filters Jobs by runtime enviornment id. If this field is absent, no filtering is done.  # noqa: E501

        :return: The runtime_environment_id of this JobsQuery.  # noqa: E501
        :rtype: str
        """
        return self._runtime_environment_id

    @runtime_environment_id.setter
    def runtime_environment_id(self, runtime_environment_id):
        """Sets the runtime_environment_id of this JobsQuery.

        Filters Jobs by runtime enviornment id. If this field is absent, no filtering is done.  # noqa: E501

        :param runtime_environment_id: The runtime_environment_id of this JobsQuery.  # noqa: E501
        :type: str
        """

        self._runtime_environment_id = runtime_environment_id

    @property
    def cluster_id(self):
        """Gets the cluster_id of this JobsQuery.  # noqa: E501

        Filters Jobs by cluster id. If this field is absent, no filtering is done.  # noqa: E501

        :return: The cluster_id of this JobsQuery.  # noqa: E501
        :rtype: str
        """
        return self._cluster_id

    @cluster_id.setter
    def cluster_id(self, cluster_id):
        """Sets the cluster_id of this JobsQuery.

        Filters Jobs by cluster id. If this field is absent, no filtering is done.  # noqa: E501

        :param cluster_id: The cluster_id of this JobsQuery.  # noqa: E501
        :type: str
        """

        self._cluster_id = cluster_id

    @property
    def creator_id(self):
        """Gets the creator_id of this JobsQuery.  # noqa: E501

        Filters Jobs by creator_id. If this field is absent, no filtering is done.  # noqa: E501

        :return: The creator_id of this JobsQuery.  # noqa: E501
        :rtype: str
        """
        return self._creator_id

    @creator_id.setter
    def creator_id(self, creator_id):
        """Sets the creator_id of this JobsQuery.

        Filters Jobs by creator_id. If this field is absent, no filtering is done.  # noqa: E501

        :param creator_id: The creator_id of this JobsQuery.  # noqa: E501
        :type: str
        """

        self._creator_id = creator_id

    @property
    def ray_job_id(self):
        """Gets the ray_job_id of this JobsQuery.  # noqa: E501

        Filters Jobs by ray_job_id. If this field is absent, no filtering is done. Note: the ray_job_id is only unique for one cluster.  # noqa: E501

        :return: The ray_job_id of this JobsQuery.  # noqa: E501
        :rtype: str
        """
        return self._ray_job_id

    @ray_job_id.setter
    def ray_job_id(self, ray_job_id):
        """Sets the ray_job_id of this JobsQuery.

        Filters Jobs by ray_job_id. If this field is absent, no filtering is done. Note: the ray_job_id is only unique for one cluster.  # noqa: E501

        :param ray_job_id: The ray_job_id of this JobsQuery.  # noqa: E501
        :type: str
        """

        self._ray_job_id = ray_job_id

    @property
    def project_id(self):
        """Gets the project_id of this JobsQuery.  # noqa: E501

        Filters Jobs by project_id. If this field is absent, no filtering is done.  # noqa: E501

        :return: The project_id of this JobsQuery.  # noqa: E501
        :rtype: str
        """
        return self._project_id

    @project_id.setter
    def project_id(self, project_id):
        """Sets the project_id of this JobsQuery.

        Filters Jobs by project_id. If this field is absent, no filtering is done.  # noqa: E501

        :param project_id: The project_id of this JobsQuery.  # noqa: E501
        :type: str
        """

        self._project_id = project_id

    @property
    def include_child_jobs(self):
        """Gets the include_child_jobs of this JobsQuery.  # noqa: E501

        Include jobs that have parents  # noqa: E501

        :return: The include_child_jobs of this JobsQuery.  # noqa: E501
        :rtype: bool
        """
        return self._include_child_jobs

    @include_child_jobs.setter
    def include_child_jobs(self, include_child_jobs):
        """Sets the include_child_jobs of this JobsQuery.

        Include jobs that have parents  # noqa: E501

        :param include_child_jobs: The include_child_jobs of this JobsQuery.  # noqa: E501
        :type: bool
        """

        self._include_child_jobs = include_child_jobs

    @property
    def ha_job_id(self):
        """Gets the ha_job_id of this JobsQuery.  # noqa: E501

        Filter by the anyscale job  # noqa: E501

        :return: The ha_job_id of this JobsQuery.  # noqa: E501
        :rtype: str
        """
        return self._ha_job_id

    @ha_job_id.setter
    def ha_job_id(self, ha_job_id):
        """Sets the ha_job_id of this JobsQuery.

        Filter by the anyscale job  # noqa: E501

        :param ha_job_id: The ha_job_id of this JobsQuery.  # noqa: E501
        :type: str
        """

        self._ha_job_id = ha_job_id

    @property
    def show_ray_client_runs_only(self):
        """Gets the show_ray_client_runs_only of this JobsQuery.  # noqa: E501

        DEPRECATED: use type_filter. Shows only ray client runs. Orthogonal to passing ha_job_id  # noqa: E501

        :return: The show_ray_client_runs_only of this JobsQuery.  # noqa: E501
        :rtype: bool
        """
        return self._show_ray_client_runs_only

    @show_ray_client_runs_only.setter
    def show_ray_client_runs_only(self, show_ray_client_runs_only):
        """Sets the show_ray_client_runs_only of this JobsQuery.

        DEPRECATED: use type_filter. Shows only ray client runs. Orthogonal to passing ha_job_id  # noqa: E501

        :param show_ray_client_runs_only: The show_ray_client_runs_only of this JobsQuery.  # noqa: E501
        :type: bool
        """

        self._show_ray_client_runs_only = show_ray_client_runs_only

    @property
    def paging(self):
        """Gets the paging of this JobsQuery.  # noqa: E501

        Pagination information.  # noqa: E501

        :return: The paging of this JobsQuery.  # noqa: E501
        :rtype: PageQuery
        """
        return self._paging

    @paging.setter
    def paging(self, paging):
        """Sets the paging of this JobsQuery.

        Pagination information.  # noqa: E501

        :param paging: The paging of this JobsQuery.  # noqa: E501
        :type: PageQuery
        """

        self._paging = paging

    @property
    def state_filter(self):
        """Gets the state_filter of this JobsQuery.  # noqa: E501

        Filter Jobs by Job Status. If this field is an empty set, no filtering is done.  # noqa: E501

        :return: The state_filter of this JobsQuery.  # noqa: E501
        :rtype: list[BaseJobStatus]
        """
        return self._state_filter

    @state_filter.setter
    def state_filter(self, state_filter):
        """Sets the state_filter of this JobsQuery.

        Filter Jobs by Job Status. If this field is an empty set, no filtering is done.  # noqa: E501

        :param state_filter: The state_filter of this JobsQuery.  # noqa: E501
        :type: list[BaseJobStatus]
        """

        self._state_filter = state_filter

    @property
    def type_filter(self):
        """Gets the type_filter of this JobsQuery.  # noqa: E501

        Filter Jobs by their type. Their type is determined by their usage within the product e.g. Interactive sessions, job runs  # noqa: E501

        :return: The type_filter of this JobsQuery.  # noqa: E501
        :rtype: list[JobRunType]
        """
        return self._type_filter

    @type_filter.setter
    def type_filter(self, type_filter):
        """Sets the type_filter of this JobsQuery.

        Filter Jobs by their type. Their type is determined by their usage within the product e.g. Interactive sessions, job runs  # noqa: E501

        :param type_filter: The type_filter of this JobsQuery.  # noqa: E501
        :type: list[JobRunType]
        """

        self._type_filter = type_filter

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
        if not isinstance(other, JobsQuery):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, JobsQuery):
            return True

        return self.to_dict() != other.to_dict()
