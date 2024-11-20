import requests
from requests.auth import HTTPBasicAuth


def func_(new_email):
    cpanel_url = "https://in-mum-cpl28.main-hosting.eu:2083"

    # cPanel login credentials (replace with your actual credentials)
    username = "invo5679"
    password = "Admin@000"

    # Email account details
    email_user = new_email
    email_domain = "idsbanao.com"
    email_password = "Admin@000"
    email_quota = 100

    # API Endpoint
    api_endpoint = "/json-api/cpanel"

    # Payload with required parameters
    params = {
        'cpanel_jsonapi_user': username,
        'cpanel_jsonapi_apiversion': '2',
        'cpanel_jsonapi_module': 'Email',
        'cpanel_jsonapi_func': 'addpop',
        'email': email_user,
        'domain': email_domain,
        'password': email_password,
        'quota': email_quota,
    }

    try:
        # Make the API request
        response = requests.get(
            f"{cpanel_url}{api_endpoint}",
            params=params,
            auth=HTTPBasicAuth(username, password),
            verify=False  # Disable SSL verification for testing; enable in production
        )

        # Handle response
        if response.status_code == 200:
            result = response.json()
            if 'cpanelresult' in result and 'error' in result['cpanelresult']:
                # return False
                return f"Error: {result['cpanelresult']['error']}"
            else:
                return f"Email account {email_user}@{email_domain} created successfully!"
                # return True
        else:
            return f"Failed to create email account. Status Code: {response.status_code}, Response: {response.text}"
            # return False

    except requests.exceptions.RequestException as e:
        # return f"An error occurred: {e}"
        return False
