# coding: utf-8

"""
    Data Repository API

    <details><summary>This document defines the REST API for the Terra Data Repository.</summary> <p> **Status: design in progress** There are a few top-level endpoints (besides some used by swagger):  * / - generated by swagger: swagger API page that provides this documentation and a live UI for submitting REST requests  * /status - provides the operational status of the service  * /configuration - provides the basic configuration and information about the service  * /api - is the authenticated and authorized Data Repository API  * /ga4gh/drs/v1 - is a transcription of the Data Repository Service API  The API endpoints are organized by interface. Each interface is separately versioned. <p> **Notes on Naming** <p> All of the reference items are suffixed with \\\"Model\\\". Those names are used as the class names in the generated Java code. It is helpful to distinguish these model classes from other related classes, like the DAO classes and the operation classes. </details>   # noqa: E501

    The version of the OpenAPI document: 0.1.0
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

import unittest

import data_repo_client
from data_repo_client.api.snapshots_api import SnapshotsApi  # noqa: E501
from data_repo_client.rest import ApiException


class TestSnapshotsApi(unittest.TestCase):
    """SnapshotsApi unit test stubs"""

    def setUp(self):
        self.api = data_repo_client.api.snapshots_api.SnapshotsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_add_snapshot_policy_member(self):
        """Test case for add_snapshot_policy_member

        """
        pass

    def test_create_search_index(self):
        """Test case for create_search_index

        """
        pass

    def test_create_snapshot(self):
        """Test case for create_snapshot

        """
        pass

    def test_delete_snapshot(self):
        """Test case for delete_snapshot

        """
        pass

    def test_delete_snapshot_policy_member(self):
        """Test case for delete_snapshot_policy_member

        """
        pass

    def test_enumerate_snapshots(self):
        """Test case for enumerate_snapshots

        """
        pass

    def test_export_snapshot(self):
        """Test case for export_snapshot

        """
        pass

    def test_lookup_snapshot_file_by_id(self):
        """Test case for lookup_snapshot_file_by_id

        """
        pass

    def test_lookup_snapshot_file_by_path(self):
        """Test case for lookup_snapshot_file_by_path

        """
        pass

    def test_lookup_snapshot_preview_by_id(self):
        """Test case for lookup_snapshot_preview_by_id

        """
        pass

    def test_patch_snapshot(self):
        """Test case for patch_snapshot

        """
        pass

    def test_query_search_indices(self):
        """Test case for query_search_indices

        """
        pass

    def test_retrieve_snapshot(self):
        """Test case for retrieve_snapshot

        """
        pass

    def test_retrieve_snapshot_policies(self):
        """Test case for retrieve_snapshot_policies

        """
        pass

    def test_retrieve_user_snapshot_roles(self):
        """Test case for retrieve_user_snapshot_roles

        """
        pass


if __name__ == '__main__':
    unittest.main()
