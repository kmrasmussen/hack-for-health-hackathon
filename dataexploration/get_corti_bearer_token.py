import requests
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv("CORTI_CLIENT_ID")
CLIENT_SECRET = os.getenv("CORTI_CLIENT_SECRET")
ENV = os.getenv("CORTI_ENVIRONMENT")
TENANT = os.getenv("CORTI_TENANT_NAME")

if not all([CLIENT_ID, CLIENT_SECRET, ENV, TENANT]):
    raise ValueError("One or more Corti environment variables are not set in the .env file.")

URL = (
    f"https://keycloak.{ENV}.corti.app"
    f"/realms/{TENANT}/protocol/openid-connect/token"
)

def get_access_token():
    r = requests.post(
        URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": "openid"
        },
    )
    r.raise_for_status()
    return r.json()["access_token"]

if __name__ == "__main__":
    try:
        token = get_access_token()
        print(token)
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Error: {e}")