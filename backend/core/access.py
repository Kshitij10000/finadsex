# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from user import client_id, secret_key, redirect_uri
response_type = "code" 
grant_type = "authorization_code"  

# The authorization code received from Fyers after the user grants access
auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIzOVRaUVlJRlRHIiwidXVpZCI6IjE3NGIxNDUyNzExNDQ3NDU4ZjI0Y2ZhMDdhOGU1MmZjIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhLMDMwNjEiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJlNTI5ZmRlY2IxNTQzNDcxYTZhMzQ3ZjdjYzg1ZTczMGQzNDZmNWE5ZjFjYzM4ZWUyZWRmZDQwMSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzY0NzYzNjY5LCJpYXQiOjE3NjQ3MzM2NjksImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc2NDczMzY2OSwic3ViIjoiYXV0aF9jb2RlIn0.ZT7DpP2KtMdU0l6V2fVB5kfA0GYDfsfUcOoCqmAa1EM"

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
