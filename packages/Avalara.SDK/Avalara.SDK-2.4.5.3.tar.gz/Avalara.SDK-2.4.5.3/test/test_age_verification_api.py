/*
 Avalara API Client Library
 * Avalara Shipping Verification for Beverage Alcohol
 *
 * API for evaluating transactions against direct-to-consumer Beverage Alcohol shipping regulations.  This API is currently in beta. 
 *
 * The version of SDK  : 22.1.0
 */


import unittest

import Avalara.SDK
from Avalara.SDK.api.age_verification_api import AgeVerificationApi  # noqa: E501


class TestAgeVerificationApi(unittest.TestCase):
    """AgeVerificationApi unit test stubs"""

    def setUp(self):
        self.api = AgeVerificationApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_verify_age(self):
        """Test case for verify_age

        Determines whether an individual meets or exceeds the minimum legal drinking age.  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
