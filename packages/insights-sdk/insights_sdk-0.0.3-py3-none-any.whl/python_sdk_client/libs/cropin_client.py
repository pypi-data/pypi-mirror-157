import logging

from python_sdk_client.clients_enum import EnvType
from python_sdk_client.libs.insight_service_client import InsightServiceClient


class CropinClient:

    def __init__(self, tenant: str, username: str, password: str, env: EnvType):
        logging.info("Initializing Cropin Client")
        self.insight_service_client = InsightServiceClient(tenant, username, password, env)
        logging.info("Initialized Cropin Client")

    def get_plot_details(self, plot_ids: list, org_id):
        return self.insight_service_client.get_plot_details(plot_ids, org_id)

    def get_satellite_details(self, plot_ids: list):
        return self.insight_service_client.get_satellite_details(plot_ids)

    def get_weather_details(self, plot_ids: list):
        return self.insight_service_client.get_weather_details(plot_ids)

    def get_yield_details(self, plot_ids: list):
        return self.insight_service_client.get_yield_details(plot_ids)

    def dowload_image(self, plot_id: str):
        return self.insight_service_client.dowload_image(plot_id)
