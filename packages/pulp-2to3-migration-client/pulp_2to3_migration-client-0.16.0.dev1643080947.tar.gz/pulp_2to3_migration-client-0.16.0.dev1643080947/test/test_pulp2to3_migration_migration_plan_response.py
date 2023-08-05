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
import datetime

import pulpcore.client.pulp_2to3_migration
from pulpcore.client.pulp_2to3_migration.models.pulp2to3_migration_migration_plan_response import Pulp2to3MigrationMigrationPlanResponse  # noqa: E501
from pulpcore.client.pulp_2to3_migration.rest import ApiException

class TestPulp2to3MigrationMigrationPlanResponse(unittest.TestCase):
    """Pulp2to3MigrationMigrationPlanResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Pulp2to3MigrationMigrationPlanResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # model = pulpcore.client.pulp_2to3_migration.models.pulp2to3_migration_migration_plan_response.Pulp2to3MigrationMigrationPlanResponse()  # noqa: E501
        if include_optional :
            return Pulp2to3MigrationMigrationPlanResponse(
                pulp_href = '0', 
                pulp_created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                plan = pulpcore.client.pulp_2to3_migration.models.plan.plan()
            )
        else :
            return Pulp2to3MigrationMigrationPlanResponse(
                plan = pulpcore.client.pulp_2to3_migration.models.plan.plan(),
        )

    def testPulp2to3MigrationMigrationPlanResponse(self):
        """Test Pulp2to3MigrationMigrationPlanResponse"""
        inst_req_only = self.make_instance(include_optional=False)
        inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == '__main__':
    unittest.main()
