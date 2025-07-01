# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/soap/tip_insure_routes.py

# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/soap/tip_insure_routes.py

from flask import Blueprint, request, jsonify
import xml.etree.ElementTree as ET

# Define the blueprint for TIP Insure SOAP API routes
tip_insure_routes = Blueprint('tip_insure_routes', __name__)

# Mock credentials and endpoint (Replace with actual credentials and endpoint)
SOAP_ENDPOINT = "https://apidev.tipinsure.com/MotorMasterData/Service1.svc"
USERNAME = "username"
PASSWORD = "password"

# Helper function to create XML payload
def create_soap_payload(action, params):
    envelope = ET.Element('soap:Envelope', {
        'xmlns:soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'xmlns:web': 'http://tempuri.org/'
    })
    body = ET.SubElement(envelope, 'soap:Body')
    action_elem = ET.SubElement(body, f'web:{action}')

    for key, value in params.items():
        param_elem = ET.SubElement(action_elem, key)
        param_elem.text = str(value)

    return ET.tostring(envelope, encoding='utf-8', method='xml')

# Endpoint to GetBrand
@tip_insure_routes.route('/get-brand', methods=['POST'])
def get_brand():
    try:
        data = request.json
        params = {
            'username': USERNAME,
            'password': PASSWORD,
            'CarGroup': data['CarGroup'],
            'CarYear': data['CarYear'],
            'MotorType': data['MotorType'],
            'VoluntaryCode': data.get('VoluntaryCode', '')
        }
        payload = create_soap_payload('RequestGetBrandDataGateway', params)
        # Mock response (replace with actual HTTP POST)
        response = """
        <BrandList>
            <Brand>
                <BrandId>8</BrandId>
                <BrandName>FORD</BrandName>
            </Brand>
        </BrandList>
        """
        # Parse response and return as JSON
        brands = []
        root = ET.fromstring(response)
        for brand in root.findall('.//Brand'):
            brands.append({
                'BrandId': brand.find('BrandId').text,
                'BrandName': brand.find('BrandName').text
            })
        return jsonify({'ResultCode': '00', 'ResultDescription': 'SUCCESS', 'BrandList': brands})
    except Exception as e:
        return jsonify({'ResultCode': '99', 'ResultDescription': str(e)})

# Similarly, add endpoints for GetModel, GetSpec, GetSuminsured, GetPackage, and Issue Policy

# Placeholder for GetModel
@tip_insure_routes.route('/get-model', methods=['POST'])
def get_model():
    # Implementation goes here
    pass

# Placeholder for GetSpec
@tip_insure_routes.route('/get-spec', methods=['POST'])
def get_spec():
    # Implementation goes here
    pass

# Placeholder for GetSumInsured
@tip_insure_routes.route('/get-suminsured', methods=['POST'])
def get_suminsured():
    # Implementation goes here
    pass

# Placeholder for GetPackage
@tip_insure_routes.route('/get-package', methods=['POST'])
def get_package():
    # Implementation goes here
    pass

# Placeholder for Issue Policy
@tip_insure_routes.route('/issue-policy', methods=['POST'])
def issue_policy():
    # Implementation goes here
    pass

# Add this blueprint to your main Flask application:
# app.register_blueprint(tip_insure_routes, url_prefix='/soap/tip-insure')
