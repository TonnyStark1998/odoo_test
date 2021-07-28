import logging as log

from odoo\
    import models, exceptions

class BillingDoAuthenticationHttpServiceHelper(models.AbstractModel):
    _name = "billing.do.authentication.http.service.helper"
    _inherit = "billing.do.http.service.helper"
    _description = """
    
    """

    __token_url = "https://login.microsoftonline.com/4e9b7883-1526-4764-abf5-619326b5f34a/oauth2/v2.0/token"
    __api_dgii_base_url = "https://api-dev.koalacreativesoftware.com/webapi"
    __token = ""

    def get_access_token_for_webapi(self):
        config = self.env['ir.config_parameter'].sudo()

        response = self.send_request("{0}/resources/".format(config.get_param('billing_do.api_services_base_url')),
                                        http_method=self.HTTP_METHODS['get'],
                                        headers=self.get_request_headers())

        if not self.__token or (response and response.status_code == 401):
            response = self.send_request(config.get_param('billing_do.token_url'), 
                                            http_method=self.HTTP_METHODS['post'],
                                            data=self.get_token_api_data())
            
            if(response.status_code == 200):
                self.__token = response.json()['access_token']
            
            elif(response.status_code == 500 
                    or response.status_code == 404 
                    or response.status_code == 400):
                
                raise exceptions.ValidationError("No se puedo obtener un token de acceso para conusltas del API.")

        return self.__token

    def get_request_headers(self):
        return {
            "Authorization":"Bearer {0}".format(self.__token),
            "Cache-Control":"max-age=3600"
        }

    def get_token_api_data(self):
        config = self.env['ir.config_parameter'].sudo()

        return {
            'grant_type':'client_credentials', 
            'client_id': config.get_param('billing_do.token_client_id'), 
            'client_secret':config.get_param('billing_do.token_client_secret'), 
            'scope':'https://koalacreativesoftware.com/.default'
        }