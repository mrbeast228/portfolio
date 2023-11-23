import datetime

import luigi

from models import VMMetrics, VMChanges
from migration import PrepareDBTask
from write_vm_changes import WriteVMChangesTask
from vk_config import config

import utils


# Generate time-series data in vm_metrics table.
# Time-series should have data for each VM for each minute.
# Use vm_changes table to generate data. use last change before minute.
class GenerateVMMetricsTask(luigi.Task):
    def requires(self):
        return [
            WriteVMChangesTask(),
            PrepareDBTask(),
        ]

    def run(self):
        # Get list of IDs from vm_changes table
        vm_ids = [vm.vm_id for vm in VMChanges.select().distinct(VMChanges.vm_id)]

        # Prepare list for insert_many
        to_write = []

        # For each ID read last row from vm_changes and vm_metrics table,
        # generate new row for this VM if it exists now (not orphaned)
        # and to big list for insert_many
        for id in vm_ids:
            # Export now time
            now = datetime.datetime.utcnow()

            # Get last VM metric
            vm_metrics = VMMetrics.select().where(VMMetrics.vm_id == id).order_by(VMMetrics.date_time.desc())
            # Get last change time
            vm_change_time = VMChanges.select().where(VMChanges.vm_id == id).order_by(VMChanges.date_time.desc())[0].date_time

            # If no metrics for this VM, use last change as start time
            if not vm_metrics:
                vm_time = vm_change_time
            else:  # Use last metric as start time
                vm_time = vm_metrics[0].date_time + datetime.timedelta(minutes=1)  # NEXT MINUTE ALWAYS

            # If VM exists in metrics and have state -1, it does not exist anymore, skip it
            if vm_metrics and vm_metrics[0].vm_state == -1:
                continue

            # Fill every minute from last change to now.
            # Keep previous last VM data for optimization.
            last_change = []
            while now - vm_time > datetime.timedelta(0):
                # Get last change before vmTime
                if not last_change or last_change[-1].date_time > vm_time:
                    # Synchronize only if last change is newer than vmTime
                    last_change.append(VMChanges.select().where(VMChanges.vm_id == id, VMChanges.date_time <= vm_time).order_by(VMChanges.date_time.desc())[0])
                data = {
                    'date_time': vm_time,
                    'vm_id': last_change[-1].vm_id,
                    'vm_name': last_change[-1].vm_name,
                    'vm_tags': last_change[-1].vm_tags,
                    'vm_metadata': last_change[-1].vm_metadata,
                    'vm_state': last_change[-1].vm_state,
                    'vm_price_min': last_change[-1].vm_price,
                    'vm_resources': last_change[-1].__dict__['__data__']['vm_config']
                }
                to_write.append(data)
                # Increase vmTime by 1 minute
                vm_time += datetime.timedelta(minutes=1)

        # Insert all metrics for all VMs
        VMMetrics.insert_many(to_write).execute()

        # Remove load metrics flag to allow get new data
        utils.remove_flag_file(config.flags_paths.load_metrics_flag)


if __name__ == '__main__':
    luigi.run()
