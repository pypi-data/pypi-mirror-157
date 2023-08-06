from pprint import pprint

import insights_python_client
from insights_python_client import Configuration, configuration
from insights_python_client.rest import ApiException

from python_sdk_client.libs.abstract_client import AbstractClient
from python_sdk_client.libs.client_cfg import InsightServiceCfg
from python_sdk_client.clients_enum import EnvType
from python_sdk_client.libs.cropin_exceptions import InvalidInputError

"""
Insights Service Client
-----------------------

class to validate the inputs and set the env, endpoint and other env specific details.
"""


class InsightServiceClient(AbstractClient):
    """
    Initialising the env and base url
    """

    def __init__(self, tenant: str, username: str, password: str, env: EnvType) -> None:
        super(InsightServiceClient, self).__init__(tenant, username, password, env)

        if env == EnvType.PROD:
            self.base_url = InsightServiceCfg.prod_base_url
        elif env == EnvType.QA:
            self.base_url = InsightServiceCfg.qa_base_url

        self.configuration = Configuration()
        # set base url
        self.configuration.host = self.base_url
        # set auth token
        self.configuration.api_key['Authorization'] = self.token

    """
    Validate input for fetching plot details
    """

    def get_plot_details(self, plot_ids: list, org_id):
        if plot_ids is not None and not isinstance(plot_ids, list):
            raise InvalidInputError("plot_ids must be list of String type")

        tenant_type = 'SMARTFARM_PLUS'  # str | TenantType
        x_api_key = self.x_api_key  # str | X-Api-Key
        org_id = org_id
        boundary_api = insights_python_client.BoundaryApi(insights_python_client.ApiClient(self.configuration))
        plot_details_list = boundary_api.list_all(tenant_type, x_api_key, org_id=org_id)

        return plot_details_list

    """
    Validate inputs for satellite details
    """

    def get_satellite_details(self, plot_ids: list):
        if plot_ids is not None and not isinstance(plot_ids, list):
            raise InvalidInputError("plot_ids should be list of String type")

        satellite_details_list = list()
        return satellite_details_list

    """
    Validate inputs for weather details
    """

    def get_weather_details(self, plot_ids: list):
        if plot_ids is None or not isinstance(plot_ids, list):
            raise InvalidInputError("plot_ids is required and must be list of String type")

        weather_details_list = list()
        return weather_details_list

    """
    Validate inputs for yield details
    """

    def get_yield_details(self, plot_ids: list):
        if plot_ids is None or not isinstance(plot_ids, list):
            raise InvalidInputError("plot_ids is required and must be list of String type")

        yield_details_list = list()
        return yield_details_list

    """
    Validate inputs for download plot image
    """

    def dowload_image(self, plot_id: str):
        if plot_id is None:
            raise InvalidInputError("plot_id is required")

        image = None
        return image
