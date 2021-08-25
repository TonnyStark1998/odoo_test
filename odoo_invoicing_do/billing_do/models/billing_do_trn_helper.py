# -*- coding: utf-8 -*-

import re,\
        logging as log

from odoo import models,\
                    exceptions,\
                    _

class BillingDoTrnHelper(models.AbstractModel):
    _name = 'billing.do.trn.helper'
    _description = 'Billing DO - TRN Helper'

    def is_valid_trn_do(self, trn):
        if trn:
            _trn_types = self.env['billing.do.trn.type']\
                            .search([('active', '=', True)])

            _trn_type_found = False

            if _trn_types:
                for _trn_type in _trn_types:
                    if trn[:_trn_type.code_length] == _trn_type.code:
                        _trn_type_found = True

                        if not _trn_type.min_length <= len(trn) <= _trn_type.max_length:
                            raise exceptions.ValidationError(_("The TRN ({}) has some extra digits. Please verify.")
                                                                .format(trn.upper())) 

                        _match = re.match(_trn_type.regular_expression,
                                            trn.upper())

                        if not _match:
                            raise exceptions.ValidationError(_("The TRN ({0}) is invalid.")
                                                                .format(trn.upper()))

                        break

            if not _trn_type_found:
                raise exceptions.ValidationError(_("There isn't any TRN type for validate. Please check with your administrator."))

            return True
        else:
            raise exceptions.UserError(_("The TRN parameter must have a value. Nothing was given."))

    def is_trn_from_journal_which_use_sequence(self, trn):
        regex = r"(^(E)?(?=)(41|43)[0-9]{10}|^(B)(?:(11|13)[0-9]{8}))"
        match_ncf = re.match(regex, 
                                trn.upper())

        if match_ncf:
            raise exceptions.ValidationError(_("The TRNs which starts with B11 or B13 use a specific type of journal. Please use the appropiate journal for registering this vendor invoice.").format(trn.upper()))