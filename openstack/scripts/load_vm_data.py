import os
import json
import datetime

import luigi

from vk_config import config
from models import VMRaw
from migration import PrepareDBTask
from get_vm_prices import CalculateVMPricesTask

import utils


# Write vm_raw table
class WriteVMRawTask(luigi.Task):
    def requires(self):
        return [
            CalculateVMPricesTask(),
            PrepareDBTask()
        ]

    def output(self):
        return luigi.LocalTarget(config.flags_paths.load_changes_flag)

    def run(self):
        vm_data = json.load(open(config.jsons.vm_prices, 'r'))

        # Get list of unique IDs from vm_raw table
        vm_ids = {vm.vm_id for vm in VMRaw.select().distinct(VMRaw.vm_id)}

        # Generate list
        to_write = []
        for vm in vm_data:
            vm_ids.discard(vm['id'])

            # HOOK: if VM doesn't contain any IP, it's in creating process
            # and it's current price is 0
            # also suppress any negative prices
            vm_price_raw = vm.pop('price')
            vm_price = 0 if not vm['ip'] or vm_price_raw < 0 else vm_price_raw
            to_write.append({
                'date_time': datetime.datetime.utcnow(),
                'vm_id': vm.pop('id'),
                'vm_name': vm.pop('name'),
                'vm_tags': {"not": "implemented yet"}, # tags currently can't be obtained from Opensatck API
                'vm_metadata': vm.pop('metadata'),
                'vm_state': int(vm.pop('status') == 'ACTIVE'),
                'vm_price': vm_price,
                'vm_config': vm,
            })

        # If ID is in known IDs list, it's orphaned and VM does not exist anymore
        # Write orphaned VMs to DB with state = -1 and price = 0
        for vm_id in vm_ids:
            deleted_vm = VMRaw.select().where(VMRaw.vm_id == vm_id).order_by(VMRaw.date_time.desc())[0]
            if deleted_vm.vm_state == -1:
                continue  # This VM is already marked as deleted

            to_write.append({
                'date_time': datetime.datetime.utcnow(),
                'vm_id': vm_id,
                # Get data from last row in raw with this ID to get name
                'vm_name': deleted_vm.vm_name,
                'vm_tags': {"not": "implemented yet"},
                'vm_metadata': {},
                'vm_state': -1,
                'vm_price': 0,
                'vm_config': {},
            })

        VMRaw.insert_many(to_write).execute()

        # Remove prices file to allow get new data
        if os.path.exists(config.jsons.vm_prices):
            os.remove(config.jsons.vm_prices)

        # Create success flag
        utils.create_flag_file(config.flags_paths.load_changes_flag)


if __name__ == '__main__':
    luigi.run()
