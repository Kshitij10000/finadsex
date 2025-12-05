# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from user import client_id, secret_key, redirect_uri
response_type = "code" 
grant_type = "authorization_code"  

# The authorization code received from Fyers after the user grants access
auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIzOVRaUVlJRlRHIiwidXVpZCI6IjZlODk4YjBkZjZlYzRiNWVhNDZmY2Y4YzNmN2E2OTQwIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhLMDMwNjEiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiI4ODdiMDhmOGQ1MzFlZmYwYTg1YTlkOGNmOWY2NDUxN2JjMmJmZTkzZDE4YWQ3MmE0MjcyMGY0OCIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzY0OTMzNzk4LCJpYXQiOjE3NjQ5MDM3OTgsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc2NDkwMzc5OCwic3ViIjoiYXV0aF9jb2RlIn0.Z6y0ox6m_gkRqd60pZxTAJu6GOvt_ebvKs_k5PUr4CE"

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
