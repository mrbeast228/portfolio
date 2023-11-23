import luigi

from vk_config import config
from models import VMPrices
from migration import PrepareDBTask

import utils


class LoadPricesToDBTask(luigi.Task):
    # Load prices to DB
    def requires(self):
        return [
            PrepareDBTask(),
        ]

    def run(self):
        # Load prices to DB
        for resource in config.prices:
            VMPrices.create(resource=resource, price=config.prices[resource])

        # Create success flag
        utils.create_flag_file(self.output().path)

    def output(self):
        return luigi.LocalTarget(config.flags_paths.prices_load_success_flag)


if __name__ == '__main__':
    luigi.run()
