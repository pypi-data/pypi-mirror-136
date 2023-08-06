
import unittest

from trytond.tests.test_tryton import activate_module
from trytond.tests.test_tryton import with_transaction

import trytond_factories


class TrytondFactoriesTestCase(unittest.TestCase):
    'Test Trytond Factories'

    MODULES = [
        'account_invoice',
        'company',
    ]

    @classmethod
    def setUpClass(cls):
        activate_module(cls.MODULES)

    @with_transaction()
    def test_company(self):
        """Test Company factory"""
        company = trytond_factories.Company.create(party__name='A')
        self.assertEqual(company.party.name, 'A')
