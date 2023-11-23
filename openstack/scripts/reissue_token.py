import os
import time
import json

import luigi
import requests

from vk_config import config


# This is a file to get a new token from VK Cloud API and save it to config file
class GetNewTokenTask(luigi.Task):
    def output(self):
        return luigi.LocalTarget(config.jsons.vk_api_file)

    # Task isn't completed if token is older than 50 minutes
    def complete(self):
        if not os.path.exists(config.jsons.vk_api_file):
            return False
        return (time.time() - os.path.getmtime(config.jsons.vk_api_file)) < 3000

    def run(self):
        headers = {'Content-Type': 'application/json'}
        request = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "domain": {
                                "id": config.vk_credentials.user_domain_name
                            },
                            "name": config.vk_credentials.username,
                            "password": config.vk_credentials.password,
                        }
                    }
                },
                "scope": {
                    "project": {
                        "id": config.vk_credentials.project_id,
                        "region": config.vk_credentials.region_name,
                    }
                }
            }
        }
        auth_endpoint = f'{config.vk_credentials.auth_url}/auth/tokens'
        response = requests.post(auth_endpoint, headers=headers, data=json.dumps(request))

        # Remove previous API file
        if os.path.exists(config.jsons.vk_api_file):
            os.remove(config.jsons.vk_api_file)
        if response.status_code == 201:
            json.dump(
                {
                    'token': response.headers['X-Subject-Token'],
                    'projectId': config.vk_credentials.project_id,
                },
                open(config.jsons.vk_api_file, 'w')
            )
        else:
            raise Exception(f'ERROR: {response.status_code} {response.reason}')


if __name__ == '__main__':
    luigi.run()
