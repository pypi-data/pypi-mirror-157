import logging

from python_sdk_client.libs.cropin_exceptions import UnauthorizedError

"""

Keycloak Client
----------------

A class for authenticating the user

"""


def internal_sdk_auth_check(tenant: str, username: str, password: str):
    import insights_python_client
    from insights_python_client.rest import ApiException

    api_instance = insights_python_client.AuthenticateApi(insights_python_client.ApiClient())
    body = insights_python_client.AccessTokenRequest(tenant=tenant, username=username,
                                                     password=password)  # AccessTokenRequest |
    try:
        # Generate access token
        logging.info("doing authentication for request: {}".format(body))
        api_response = api_instance.get_token(body)
        logging.info("auth api response: {0}".format(api_response))
        return api_response
    except ApiException as e:
        logging.error("Exception when calling AuthenticateApi->get_token: {}\n".format(e))
        raise Exception("failed to auth ", e)


class KeyCloakAPI:
    """
    Generates token given tenant, username and password as input
    """

    def authenticate(self, tenant: str, username: str, password: str) -> (str, str):
        logging.info("Starting authentication now")
        token = None
        refresh_token = None
        x_api_key = None
        response = internal_sdk_auth_check(tenant, username, password)
        if response is not None:
            token = response.to_dict().get('access_token')
            refresh_token = response.to_dict().get('refresh_token')
            x_api_key = response.to_dict().get('X-Api-Key')
        if token is None:
            raise UnauthorizedError("Authentication not successful token is None")
        if refresh_token is None:
            raise UnauthorizedError("Authentication not successful refresh_token is None")
        logging.info("Authentication successful! Ready to make function call.")
        return token, refresh_token, x_api_key

    """
    Get access token using the refresh token for authentication
    """

    def re_authenticate(self, refresh_token: str) -> (str, str):
        token = None
        refresh_token = None
        x_api_key = None
        # TODO: refresh token using SDK
        if token is None or refresh_token is None:
            raise UnauthorizedError("Authentication not successful")
        return token, refresh_token, x_api_key

    """
    Validating the returned token
    """

    def validate_token(self, token: str) -> bool:
        is_valid = True
        # TODO: check if token has expired
        return is_valid
