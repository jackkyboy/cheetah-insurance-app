import requests
from datetime import datetime
from configs.api_endpoints import VMI_API_ENDPOINT
from utils.request_mapper import map_vmi_request
from utils.response_formatter import format_vmi_response

class VMIService:
    @staticmethod
    def get_quotation(payload):
        """
        Fetch the quotation for the vehicle insurance (VMI).
        :param payload: dict - Input data from the client
        :return: dict - Formatted response from the VMI API
        """
        # Map the request payload
        request_data = map_vmi_request(payload)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "sourceTransID": f"X10_12345_{int(datetime.now().timestamp())}",
            "clientId": "ec81d967-0192-4680-939e-8de81980d336",
            "clientSecret": "02f477ad-39b9-4cc5-a151-f98323dfd60b",
            "requestTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "languagePreference": "TH",
            "Authorization": f"Bearer {payload.get('authorization', '')}"
        }

        # Make the API call
        try:
            response = requests.post(
                VMI_API_ENDPOINT["quotation"], 
                json=request_data, 
                headers=headers
            )
            
            # Handle and format the response
            if response.status_code == 200:
                return format_vmi_response(response.json())
            else:
                return {
                    "status": "error",
                    "message": response.json().get("displayErrorMessage", "Unknown Error")
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"API request failed: {str(e)}"
            }
