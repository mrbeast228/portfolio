import datetime

import luigi

from migration import PrepareDBTask
from models import VMRaw, VMMetrics
from vk_config import config


class CleanUpOldRowsTask(luigi.Task):
    def requires(self):
        return PrepareDBTask()

    def run(self):
        current_time = datetime.datetime.utcnow()

        old_metrics_cutoff = current_time - datetime.timedelta(days=config.general.metrics_store_period_days)
        old_raw_data_cutoff = current_time - datetime.timedelta(days=config.general.raw_store_period_days)

        VMRaw.delete() \
            .where(VMRaw.date_time < old_raw_data_cutoff) \
            .execute()

        VMMetrics.delete() \
            .where(VMMetrics.date_time < old_metrics_cutoff) \
            .execute()


if __name__ == '__main__':
    luigi.run()
