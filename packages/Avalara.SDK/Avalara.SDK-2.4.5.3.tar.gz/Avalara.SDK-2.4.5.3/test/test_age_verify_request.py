/*
 Avalara API Client Library
 * Avalara Shipping Verification for Beverage Alcohol
 *
 * API for evaluating transactions against direct-to-consumer Beverage Alcohol shipping regulations.  This API is currently in beta. 
 *
 * The version of SDK  : 22.1.0
 */


import sys
import unittest

import Avalara.SDK
from Avalara.SDK.model.age_verify_request_address import AgeVerifyRequestAddress
globals()['AgeVerifyRequestAddress'] = AgeVerifyRequestAddress
from Avalara.SDK.model.age_verify_request import AgeVerifyRequest


class TestAgeVerifyRequest(unittest.TestCase):
    """AgeVerifyRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAgeVerifyRequest(self):
        """Test AgeVerifyRequest"""
        # FIXME: construct object with mandatory attributes with example values
        # model = AgeVerifyRequest()  # noqa: E501
        pass


if __name__ == '__main__':
    unittest.main()
