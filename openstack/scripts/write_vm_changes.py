import luigi

from migration import PrepareDBTask
from models import VMRaw, VMChanges
from vk_config import config
from load_vm_data import WriteVMRawTask
import utils


# Write VM changes to DB
class WriteVMChangesTask(luigi.Task):
    def requires(self):
        return [
            WriteVMRawTask(),
            PrepareDBTask(),
        ]

    def output(self):
        return luigi.LocalTarget(config.flags_paths.load_metrics_flag)

    def run(self):
        # Get list of unique IDs from vm_raw table
        vm_ids = [vm.vm_id for vm in VMRaw.select().distinct(VMRaw.vm_id)]

        # For each ID read last row from vm_raw table
        for vm_id in vm_ids:
            # Select rows with vm_id = vmId, order by date_time desc, get first row
            vm = VMRaw.select().where(VMRaw.vm_id == vm_id).order_by(VMRaw.date_time.desc())[0].__dict__['__data__']
            vm.pop('id')  # Remove id field

            # Get VM row with this vm_id from vm_changes table
            vm_changes = VMChanges.select().where(VMChanges.vm_id == vm_id).order_by(VMChanges.date_time.desc())

            # If there is no such row, or previous row has different price or metadata from current, write new row to vm_changes table
            # for heatbeats add condition that previous row is older than 1 hour
            if not vm_changes or vm_changes[0].__dict__['__data__']['vm_price'] != vm['vm_price'] or vm_changes[0].__dict__['__data__']['vm_metadata'] != vm['vm_metadata']:
                VMChanges.create(**vm)

        # Remove write changes flag to allow get new data
        utils.remove_flag_file(config.flags_paths.load_changes_flag)

        # Create load metrics flag
        utils.create_flag_file(config.flags_paths.load_metrics_flag)


if __name__ == '__main__':
    luigi.run()
