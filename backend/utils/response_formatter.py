def format_vmi_response(response):
    """
    Formats the VMI API response for the client.
    :param response: dict - Response from the VMI API
    :return: dict - Formatted response
    """
    data = response.get("data", [])
    return {
        "status": "success",
        "quotations": [
            {
                "quotationNumber": item.get("quotationNumber"),
                "carBrand": item.get("carBrand"),
                "carModel": item.get("carModel"),
                "carSubModel": item.get("carSubModel"),
                "registrationYear": item.get("registrationYear"),
                "vehicleTypeCode": item.get("vehicleTypeCode"),
                "insuranceType": item.get("insuranceType"),
                "repairType": item.get("repairType"),
                "netPremium": item.get("netPremium"),
                "stamp": item.get("stamp"),
                "vat": item.get("vat"),
                "totalPremium": item.get("totalPremium")
            } for item in data
        ]
    }
