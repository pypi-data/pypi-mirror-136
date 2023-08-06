import pytest
from django.test import TestCase
from eth_utils import is_checksum_address

from ..factories import EthereumAccountFactory


@pytest.mark.django_db(transaction=True)
class BaseTestCase(TestCase):
    pass


class EthereumAccountTestCase(BaseTestCase):
    def setUp(self):
        self.account = EthereumAccountFactory()

    def test_account_address_is_checksummed(self):
        self.assertTrue(is_checksum_address(self.account.address))


__all__ = ["EthereumAccountTestCase"]
