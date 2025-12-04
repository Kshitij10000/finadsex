# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from user import client_id, secret_key, redirect_uri
response_type = "code" 
grant_type = "authorization_code"  

# The authorization code received from Fyers after the user grants access
auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIzOVRaUVlJRlRHIiwidXVpZCI6IjNhMDViYWM0NmM1ODRiNDE5MTAxOGQ4MGU0NzIzYWUwIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhLMDMwNjEiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJlZTNkM2I0YmI1NWRjODcxMzQ2MzAxNzA0MWM0ZDhmNzBjZTRjMzU0M2VlZjU4YWY5NWJkMzgyMSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzY0ODUwNzQxLCJpYXQiOjE3NjQ4MjA3NDEsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc2NDgyMDc0MSwic3ViIjoiYXV0aF9jb2RlIn0.OfPm9kZecgCtbRAtN-5ze0L0wKOKGOrwMKvBVjchKAg"

# Create a session object to handle the Fyers API authentication and token generation
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)
