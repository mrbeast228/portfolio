import os

import luigi

from vk_config import config
from models import db, VMMetrics, VMChanges, VMPrices, VMRaw
import utils


def create_tables():
    db.execute_sql('CREATE SCHEMA IF NOT EXISTS vm_data;')
    db.create_tables([VMMetrics, VMChanges, VMPrices, VMRaw])


def drop_tables():
    db.execute_sql('DROP SCHEMA IF EXISTS vm_data CASCADE;')


class PrepareDBTask(luigi.Task):
    completed = False
    db_success_flag = config.flags_paths.db_success_flag

    def run(self):
        create_tables()
        if not db.is_closed():
            utils.create_flag_file(self.db_success_flag)
            self.completed = True

    def complete(self):
        return self.completed

    def output(self):
        return luigi.LocalTarget(self.db_success_flag)


class DropDataTask(luigi.Task):
    def run(self):
        drop_tables()

        # Remove files related to the DB
        utils.remove_flag_file(config.flags_paths.db_success_flag)
        utils.remove_flag_file(config.flags_paths.prices_load_success_flag)

        if os.path.exists(config.jsons.current_prices):
            os.remove(config.jsons.current_prices)


if __name__ == '__main__':
    luigi.run()
