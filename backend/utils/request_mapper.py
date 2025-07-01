def map_vmi_request(payload):
    """
    Maps the incoming payload to the format expected by the VMI API.
    :param payload: dict - Incoming payload from the client
    :return: dict - Formatted payload
    """
    return {
        "agentCode": payload.get("agentCode", "17423"),
        "energyType": payload.get("energyType", "C"),  # Default to combustion
        "saleMethod": payload.get("saleMethod", "offline"),
        "carBrand": payload.get("carBrand"),
        "carModel": payload.get("carModel"),
        "carSubModel": payload.get("carSubModel"),
        "registrationYear": payload.get("registrationYear"),
        "vehicleTypeCode": payload.get("vehicleTypeCode", ["110", "120", "210"]),
        "carCamera": payload.get("carCamera", False),
        "isCharger": payload.get("isCharger", False),
        "chargerInfo": payload.get("chargerInfo", {}),
        "isBattery": payload.get("isBattery", False),
        "batteryInfo": payload.get("batteryInfo", {}),
        "preference": {
            "periodType": payload.get("preference", {}).get("periodType", "Y"),
            "startDate": payload.get("preference", {}).get("startDate"),
            "endDate": payload.get("preference", {}).get("endDate"),
            "insuranceType": payload.get("preference", {}).get("insuranceType", ["1", "2"]),
            "repairType": payload.get("preference", {}).get("repairType", ["D", "G"])
        }
    }
