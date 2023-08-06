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
from Avalara.SDK.model.shipping_verify_result_lines import ShippingVerifyResultLines
globals()['ShippingVerifyResultLines'] = ShippingVerifyResultLines
from Avalara.SDK.model.shipping_verify_result import ShippingVerifyResult


class TestShippingVerifyResult(unittest.TestCase):
    """ShippingVerifyResult unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testShippingVerifyResult(self):
        """Test ShippingVerifyResult"""
        # FIXME: construct object with mandatory attributes with example values
        # model = ShippingVerifyResult()  # noqa: E501
        pass


if __name__ == '__main__':
    unittest.main()
