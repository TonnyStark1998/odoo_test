
import requests, re

class BillingDoUtils:
    __token_url = "https://login.microsoftonline.com/4e9b7883-1526-4764-abf5-619326b5f34a/oauth2/v2.0/token"
    __api_dgii_base_url = "https://api-dev.koalacreativesoftware.com/webapi"
    __token = ""
    
    @staticmethod
    def dgii_get_vat_info(vat):
        if not BillingDoUtils.__token:
            BillingDoUtils.__token = BillingDoUtils.__get_access_token_for_webapi()
        return requests.get("{0}/taxcontributor/{1}".format(BillingDoUtils.__api_dgii_base_url, vat), headers=BillingDoUtils.__get_request_headers())

    @staticmethod
    def dgii_validate_ncf(vat, ncf, vatBuyer):
        if not BillingDoUtils.__token:
            BillingDoUtils.__token = BillingDoUtils.__get_access_token_for_webapi()
        return requests.post("{0}/taxreceiptnumber/{1}/{2}/{3}".format(BillingDoUtils.__api_dgii_base_url, vat, ncf, vatBuyer), headers=BillingDoUtils.__get_request_headers(), data={})

    @staticmethod
    def __get_access_token_for_webapi():
        if not BillingDoUtils.__token:
            token_request = requests.post(BillingDoUtils.__token_url, data=BillingDoUtils.__get_token_api_data())
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
            if len(vat) == 11:
                return BillingDoUtils.__validate_do_id(vat)
            return 1

    @staticmethod
    def __get_token_api_data():
        return {
            'grant_type':'client_credentials', 
            'client_id':'2bc79f1d-78c8-414f-8c52-e6ad016f0e29', 
            'client_secret':'3wx_~.K1xH2rc.u~Uy02J1Tw6Kirdyg6zl', 
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
        validator_number = "1212121212"
        sum = 0
        for i in range(0,10):
            temp_number = int(vat[i]) * int(validator_number[i])
            if temp_number > 9:
                temp_number = (temp_number - 10) + 1
            sum += temp_number
        temp_number = sum % 10
        temp_number = (10 - temp_number) % 10
        if int(temp_number) == int(vat[10]):
            return 1
        return 2