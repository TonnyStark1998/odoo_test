# -*- coding: utf-8 -*-

import requests, re
import logging as log

from odoo import models, exceptions, _

class BillingDoTrnHelper(models.AbstractModel):
    _name = 'billing.do.trn.helper'
    _description = 'Billing DO - TRN Helper'

    def is_valid_trn_do(self, trn):
        if trn:
            regex = r"(^(E)?(?=)(31|32|33|34|41|43|44|45)[0-9]{10}|^(B)(?:(01|02|03|04|11|12|13|14|15|16|17)[0-9]{8}))"
            match_ncf = re.match(regex, trn.upper())

            if not match_ncf:
                raise exceptions.ValidationError(_("The TRN ({0}) is invalid.").format(trn.upper()))
            else:
                if int(len(trn)) != int(match_ncf.end()):
                    raise exceptions.ValidationError(_("The TRN ({0}) has some extra digits. Please verify.").format(trn.upper()))
            return True
        else:
            raise exceptions.UserError(_("The TRN parameter must have a value. Nothing was given."))

    def is_trn_from_journal_which_use_sequence(self, trn):
        regex = r"(^(E)?(?=)(41|43)[0-9]{10}|^(B)(?:(11|13)[0-9]{8}))"
        match_ncf = re.match(regex, trn.upper())

        if match_ncf:
            raise exceptions.ValidationError(_("The TRNs which starts with B11 or B13 use a specific type of journal. Please use the appropiate journal for registering this vendor invoice.").format(trn.upper()))