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
from Avalara.SDK.api.shipping_verification_api import ShippingVerificationApi  # noqa: E501


class TestShippingVerificationApi(unittest.TestCase):
    """ShippingVerificationApi unit test stubs"""

    def setUp(self):
        self.api = ShippingVerificationApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_deregister_shipment(self):
        """Test case for deregister_shipment

        Removes the transaction from consideration when evaluating regulations that span multiple transactions.  # noqa: E501
        """
        pass

    def test_register_shipment(self):
        """Test case for register_shipment

        Registers the transaction so that it may be included when evaluating regulations that span multiple transactions.  # noqa: E501
        """
        pass

    def test_register_shipment_if_compliant(self):
        """Test case for register_shipment_if_compliant

        Evaluates a transaction against a set of direct-to-consumer shipping regulations and, if compliant, registers the transaction so that it may be included when evaluating regulations that span multiple transactions.  # noqa: E501
        """
        pass

    def test_verify_shipment(self):
        """Test case for verify_shipment

        Evaluates a transaction against a set of direct-to-consumer shipping regulations.  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
