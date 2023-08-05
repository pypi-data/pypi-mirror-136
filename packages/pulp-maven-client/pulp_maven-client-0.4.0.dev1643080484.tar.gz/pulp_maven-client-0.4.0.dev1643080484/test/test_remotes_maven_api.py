# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import pulpcore.client.pulp_maven
from pulpcore.client.pulp_maven.api.remotes_maven_api import RemotesMavenApi  # noqa: E501
from pulpcore.client.pulp_maven.rest import ApiException


class TestRemotesMavenApi(unittest.TestCase):
    """RemotesMavenApi unit test stubs"""

    def setUp(self):
        self.api = pulpcore.client.pulp_maven.api.remotes_maven_api.RemotesMavenApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create(self):
        """Test case for create

        Create a maven remote  # noqa: E501
        """
        pass

    def test_delete(self):
        """Test case for delete

        Delete a maven remote  # noqa: E501
        """
        pass

    def test_list(self):
        """Test case for list

        List maven remotes  # noqa: E501
        """
        pass

    def test_partial_update(self):
        """Test case for partial_update

        Update a maven remote  # noqa: E501
        """
        pass

    def test_read(self):
        """Test case for read

        Inspect a maven remote  # noqa: E501
        """
        pass

    def test_update(self):
        """Test case for update

        Update a maven remote  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
