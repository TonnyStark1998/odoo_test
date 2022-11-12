from odoo import exceptions, _
from odoo.tests import SingleTransactionCase, tagged

@tagged('-standard')
class TestTrnHelper(SingleTransactionCase):

    def setUp(self):
        self._invalid_trn = 'A0100114'
        self._valid_e_trn = 'E310000000001'
        self._valid_b_trn = 'B0100000001'
        self._valid_b11_trn = 'B1100000001'
        self._valid_b13_trn = 'B1300000001'
        self._trn_helper = self.env['billing.do.trn.helper']

    def test_is_valid_trn_do_with_invalid_trn(self):
        with self.assertRaises(exceptions.ValidationError) as ex:
            self._trn_helper.is_valid_trn_do(self._invalid_trn)

    def test_is_valid_trn_do_with_valid_b_trn(self):
        self.assertTrue(self._trn_helper.is_valid_trn_do(self._valid_b_trn))

    def test_is_valid_trn_do_with_valid_e_trn(self):
        self.assertTrue(self._trn_helper.is_valid_trn_do(self._valid_e_trn))

    def test_b11_trn_is_trn_from_journal_which_use_sequence(self):
        with self.assertRaises(exceptions.ValidationError) as ex:
            self._trn_helper.is_trn_from_journal_which_use_sequence(self._valid_b11_trn)
    
    def test_b13_trn_is_trn_from_journal_which_use_sequence(self):
        with self.assertRaises(exceptions.ValidationError) as ex:
            self._trn_helper.is_trn_from_journal_which_use_sequence(self._valid_b13_trn)