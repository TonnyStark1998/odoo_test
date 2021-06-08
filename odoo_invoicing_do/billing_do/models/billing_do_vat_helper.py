import requests, re
import logging as log

from odoo import models, exceptions, _

class BillingDoVatHelper(models.AbstractModel):
    _name = "billing.do.vat.helper"
    _description = """
    
    """

    def validate_vat(self, vat):
        if vat:
            regex = r"^[0-9]{9,11}$"
            match_vat = re.match(regex, vat)

            _result = 0
            if not match_vat:
                _result = 3
            
            if _result == 3:
                raise exceptions.ValidationError(_("The Identity Number ({0}) entered is invalid. Does not meet the correct format. Please verify the value entered.")
                                                .format(self.partner_id.vat))

            _result = BillingDoVatHelper.__validate_do_id(vat)

            if _result == 2:
                raise exceptions.ValidationError(_("The format is not compatible with the format of a Dominican Republic Id nor a Tax Payer Id ({0}).")
                                                .format(self.partner_id.vat))

            return _result

    @staticmethod
    def __validate_do_id(vat):
        is_vat_valid = True

        if len(vat) == 11:
            base_number = "1212121212"
            sum = 0

            for i in range(0,10):
                temp_number = int(vat[i]) * int(base_number[i])
                if temp_number > 9:
                    temp_number = (temp_number - 10) + 1
                sum += temp_number
            temp_number = sum % 10
            temp_number = (10 - temp_number) % 10

            if int(temp_number) != int(vat[10]):
                is_vat_valid = False

        elif len(vat) == 9:
            base_number = "79865432"
            sum = 0

            for i in range(0,8):
                sum += int(vat[i]) * int(base_number[i])
            temp_number = sum - (int(sum / 11) * 11)

            if temp_number == 0:
                temp_number = 2
            elif temp_number == 1:
                temp_number = 1
            else:
                temp_number = 11 - temp_number

            if int(temp_number) != int(vat[8]):
                is_vat_valid = False
        else:
            is_vat_valid = False

        if is_vat_valid:
            return 1
        return 2