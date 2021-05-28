
import requests, re
import logging as log
from odoo import exceptions

class BillingDoUtils:
    __token_url = "https://login.microsoftonline.com/4e9b7883-1526-4764-abf5-619326b5f34a/oauth2/v2.0/token"
    __api_dgii_base_url = "https://api-dev.koalacreativesoftware.com/webapi"
    __token = ""
    
    @staticmethod
    def dgii_get_vat_info(model, vat):
        __api_services_tax_contributors_switch_temp = model.env['ir.config_parameter']\
                                                            .sudo()\
                                                            .get_param("billing_do.api_services_tax_contributors_switch")
        
        log.info("[KCS] Service Tax Contributors Switch: {0}".format(__api_services_tax_contributors_switch_temp))
        
        if __api_services_tax_contributors_switch_temp:
            __api_dgii_base_url_temp = model.env['ir.config_parameter']\
                                                .sudo()\
                                                .get_param("billing_do.api_services_base_url")
            
            log.info("[KCS] DGII Api Base URL: {0}".format(__api_dgii_base_url_temp))

            __api_services_tax_contributors_endpoint_temp = model.env['ir.config_parameter']\
                                                                    .sudo()\
                                                                    .get_param("billing_do.api_services_tax_contributors_endpoint")
            
            log.info("[KCS] Service Tax Contributors Endpoint: {0}".format(__api_services_tax_contributors_endpoint_temp))

            if __api_dgii_base_url_temp:
                BillingDoUtils.__api_dgii_base_url = __api_dgii_base_url_temp
            
            if not BillingDoUtils.__token:
                BillingDoUtils.__token = BillingDoUtils.__get_access_token_for_webapi(model)
            
            log.info("[KCS] Payload: ['vat': '{0}']".format(vat))
            log.info("[KCS] Token used: {0}".format(BillingDoUtils.__token))
            
            request = requests.get("{0}/{1}/{2}".format(BillingDoUtils.__api_dgii_base_url,
                                                            __api_services_tax_contributors_endpoint_temp,
                                                            vat),
                                                        headers=BillingDoUtils.__get_request_headers())
            
            log.info("[KCS] Request: {0}".format(request))
            log.info("[KCS] Request (Status Code): {0}".format(request.status_code))
            
            if request.status_code == 401:
                BillingDoUtils.__token = ""
                BillingDoUtils.__token = BillingDoUtils.__get_access_token_for_webapi(model)

                log.info("[KCS] Token new: {0}".format(BillingDoUtils.__token))

                request = requests.get("{0}/{1}/{2}".format(BillingDoUtils.__api_dgii_base_url,
                                                                __api_services_tax_contributors_endpoint_temp,
                                                                vat),
                                                            headers=BillingDoUtils.__get_request_headers())

                log.info("[KCS] Request: {0}".format(request))
                log.info("[KCS] Request (Status Code): {0}".format(request.status_code))
            return request
        return None

    @staticmethod
    def dgii_validate_ncf(model, vat, ncf, vatBuyer):
        __api_services_tax_receipts_switch_temp = model.env['ir.config_parameter']\
                                                        .sudo()\
                                                        .get_param("billing_do.api_services_tax_receipts_switch")
        
        log.info("[KCS] Service Tax Receipts Switch: {0}".format(__api_services_tax_receipts_switch_temp))

        if __api_services_tax_receipts_switch_temp:
            __api_dgii_base_url_temp = model.env['ir.config_parameter']\
                                                .sudo()\
                                                .get_param("billing_do.api_services_base_url")
            
            log.info("[KCS] DGII Api Base URL: {0}".format(__api_dgii_base_url_temp))
            
            __api_services_tax_receipts_endpoint_temp = model.env['ir.config_parameter']\
                                                                .sudo()\
                                                                .get_param("billing_do.api_services_tax_receipts_endpoint")
            
            log.info("[KCS] Service Tax Receipts Endpoint: {0}".format(__api_services_tax_receipts_endpoint_temp))
            
            if __api_dgii_base_url_temp:
                BillingDoUtils.__api_dgii_base_url = __api_dgii_base_url_temp
            
            if not BillingDoUtils.__token:
                BillingDoUtils.__token = BillingDoUtils.__get_access_token_for_webapi(model)
            
            log.info("[KCS] Payload: ['vat': '{0}', 'ncf': '{1}', 'vat_buyer': '{2}']".format(vat, ncf, vatBuyer))
            log.info("[KCS] Token used: {0}".format(BillingDoUtils.__token))

            request = requests.get("{0}/{3}/{1}/{2}".format(BillingDoUtils.__api_dgii_base_url,\
                                                                vat,\
                                                                ncf,\
                                                                __api_services_tax_receipts_endpoint_temp), 
                                                            headers=BillingDoUtils.__get_request_headers(),
                                                            data={})
            
            log.info("[KCS] Request: {0}".format(request))
            log.info("[KCS] Request (Status Code): {0}".format(request.status_code))
            
            if request.status_code == 401:
                BillingDoUtils.__token = ""
                BillingDoUtils.__token = BillingDoUtils.__get_access_token_for_webapi(model)

                log.info("[KCS] Token new: {0}".format(BillingDoUtils.__token))
                
                request = requests.get("{0}/{3}/{1}/{2}".format(BillingDoUtils.__api_dgii_base_url,
                                                                    vat,
                                                                    ncf,
                                                                    __api_services_tax_receipts_endpoint_temp),
                                                                headers=BillingDoUtils.__get_request_headers(),
                                                                data={})

                log.info("[KCS] Request: {0}".format(request))
                log.info("[KCS] Request (Status Code): {0}".format(request.status_code))
            return request
        return None

    @staticmethod
    def __get_access_token_for_webapi(model):
        __token_url_temp = model.env['ir.config_parameter'].sudo().get_param("billing_do.token_url")
        if __token_url_temp:
            BillingDoUtils.__token_url = __token_url_temp
        if not BillingDoUtils.__token:
            token_request = requests.post(BillingDoUtils.__token_url, data=BillingDoUtils.__get_token_api_data(model))
            if(token_request.status_code == 200):
                BillingDoUtils.__token = token_request.json()['access_token']
            elif(token_request.status_code == 500 or token_request.status_code == 404 or token_request.status_code == 400):
                raise exceptions.ValidationError("No se puedo obtener un token de acceso para conusltas del API.")
        return BillingDoUtils.__token

    @staticmethod
    def validate_vat(vat):
        if vat:
            regex = r"^[0-9]{9,11}$"
            match_vat = re.match(regex, vat)
            if not match_vat:
                return 3
            return BillingDoUtils.__validate_do_id(vat)

    @staticmethod
    def __get_token_api_data(model):
        __token_client_id_temp = model.env['ir.config_parameter'].sudo().get_param("billing_do.token_client_id")
        __token_client_secret_temp = model.env['ir.config_parameter'].sudo().get_param("billing_do.token_client_secret")
        return {
            'grant_type':'client_credentials', 
            'client_id':__token_client_id_temp, 
            'client_secret':__token_client_secret_temp, 
            'scope':'https://koalacreativesoftware.com/.default'
        }

    @staticmethod
    def __get_request_headers():
        return {
            "Authorization":"Bearer {0}" .format(BillingDoUtils.__token),
            "Cache-Control":"max-age=3600"
        }

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