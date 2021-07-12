from odoo import exceptions, _
from odoo.tests import SingleTransactionCase, tagged

@tagged('-standard')
class TestTrnHelper(SingleTransactionCase):

    def setUp(self):
        self._invalid_trn = 'A0100114'

    def test_is_valid_trn_do(self):
        _trn_helper = self.env['billing.do.trn.helper']
        
        with self.assertRaises(exceptions.ValidationError) as ex:
            _trn_helper.is_valid_trn_do(self._invalid_trn)
    
    def test_is_trn_from_journal_which_use_sequence(self):
        pass