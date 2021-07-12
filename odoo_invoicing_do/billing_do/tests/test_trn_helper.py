from odoo import exceptions, _
from odoo.tests import SingleTransactionCase, tagged

@tagged('-standard')
class TestTrnHelper(SingleTransactionCase):

    def test_is_valid_trn_do(self):
        _trn = 'A0100114'
        _trn_helper = self.env['billing.do.trn.helper']
        
        with self.assertRaises(exceptions.ValidationError) as ex:
            _trn_helper.is_valid_trn_do(_trn)