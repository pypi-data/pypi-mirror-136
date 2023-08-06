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
from Avalara.SDK.model.error_details_error import ErrorDetailsError
globals()['ErrorDetailsError'] = ErrorDetailsError
from Avalara.SDK.model.error_details import ErrorDetails


class TestErrorDetails(unittest.TestCase):
    """ErrorDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testErrorDetails(self):
        """Test ErrorDetails"""
        # FIXME: construct object with mandatory attributes with example values
        # model = ErrorDetails()  # noqa: E501
        pass


if __name__ == '__main__':
    unittest.main()
