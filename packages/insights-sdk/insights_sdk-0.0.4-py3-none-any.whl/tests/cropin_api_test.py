import logging

from python_sdk_client.clients_enum import EnvType
from python_sdk_client.cropin_api import CropinAPI

"""Example on how to use CropAPI.  
"""
if __name__ == '__main__':
    logging.info(">>>>>>>>>>>> starting")
    cropin_api = CropinAPI("test", "12121212", "password", EnvType.QA)

    print(cropin_api)
    api_response = cropin_api.get_plot_details(plot_ids=None, org_id='test')

    print(api_response)
