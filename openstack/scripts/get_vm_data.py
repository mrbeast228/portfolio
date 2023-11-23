import json

import luigi
import requests

from vk_config import config
from reissue_token import GetNewTokenTask

VM_ENDPOINT = 'https://infra.mail.ru:8774/v2.1'
DISKS_ENDPOINT = 'https://public.infra.mail.ru:8776/v3'
LICENSE_PREFIX = 'mcs:lic:'


# Class to work with cloud API
class VkCloud:
    def __init__(self, token, project_id):
        self.token = token
        self.project_id = project_id
        self.headers = {'X-Auth-Token': self.token, 'Accept': 'application/json'}

    def _request(self, url, *args, **kwargs):
        return requests.get(
            url,
            *args,
            **kwargs,
            headers=self.headers,
            timeout=60,
        ).json()

    def get_raw_vm_list(self):
        return self._request(f'{VM_ENDPOINT}/servers/detail')['servers']

    def get_disks_info(self):
        disk_list = self._request(f'{DISKS_ENDPOINT}/{self.project_id}/volumes/detail')
        return {disk['id']: disk for disk in disk_list["volumes"]}

    def get_flavors_info(self):
        flavors_list = self._request(f'{VM_ENDPOINT}/flavors/detail')['flavors']
        return {flavor['id']: flavor for flavor in flavors_list}

    def get_vm_list(self):
        vm_raw_list = self.get_raw_vm_list()
        disks_info = self.get_disks_info()
        flavors_info = self.get_flavors_info()

        vm_list = []
        for raw_vm in vm_raw_list:
            ips = []
            raw_addrs_list = list(raw_vm['addresses'].values())
            if raw_addrs_list:
                for addr in raw_addrs_list[0]:
                    ips.append(addr['addr'])

            # Get licensing info
            # Software licenses are stored in VM metadata,
            # OS licenses are stored in volume metadata
            licenses = []
            meta_list = list(raw_vm['metadata'].keys())
            for metadata in meta_list:
                if metadata.startswith(LICENSE_PREFIX):
                    licenses.append(metadata.removeprefix(LICENSE_PREFIX))

            # Get disks
            disks = []
            for disk in raw_vm['os-extended-volumes:volumes_attached']:
                disk_info = disks_info[disk['id']]
                disks.append({'type': disk_info['volume_type'], 'size': disk_info['size']})

                # Try to find OS licenses data
                for vol_metadata in disk_info['volume_image_metadata'].keys():
                    if vol_metadata.startswith(LICENSE_PREFIX):
                        licenses.append(vol_metadata.removeprefix(LICENSE_PREFIX))

            flavor = flavors_info[raw_vm['flavor']['id']]

            vm = {
                'id': raw_vm['id'],
                'name': raw_vm['name'],
                'status': raw_vm['status'],
                'metadata': raw_vm['metadata'],
                'ip': ips,
                'key': raw_vm['key_name'],
                'cpus': flavor['vcpus'],
                'ram': flavor['ram'],
                'licenses': licenses,
                'disks': disks,
            }

            vm_list.append(vm)
        return vm_list


class GetVMDataTask(luigi.Task):
    def requires(self):
        return GetNewTokenTask()

    def run(self):
        vk_config = json.load(open(self.input().path, 'r'))
        cloud = VkCloud(vk_config['token'], vk_config['projectId'])
        data = cloud.get_vm_list()
        json.dump(data, open(config.jsons.vm_raw_file, 'w'))

    def output(self):
        return luigi.LocalTarget(config.jsons.vm_raw_file)


if __name__ == '__main__':
    luigi.run()
