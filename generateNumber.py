import requests


def create_5sim_phone(api_key, country='india', operator='any', product='flipkart'):

    base_url = "https://5sim.net/v1/user"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        # Endpoint to order a phone number
        url = f"{base_url}/buy/activation/{country}/{operator}/{product}"

        # Make the API request
        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            # Successfully created phone number
            return {
                "status": "success",
                "phone": response_data.get("phone"),
                "id": response_data.get("id"),
                "cost": response_data.get("price"),
                "expiration": response_data.get("time"),
            }
        else:
            # Handle errors
            return {
                "status": "error",
                "message": response_data.get("message", "Unknown error occurred.")
            }
    except requests.RequestException as e:
        return {
            "status": "error",
            "message": str(e)
        }


