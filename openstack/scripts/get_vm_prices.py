import os
import json

import luigi

from vk_config import config
from models import VMPrices
from migration import PrepareDBTask
from get_vm_data import GetVMDataTask
from load_res_price import LoadPricesToDBTask


MINUTES_IN_MONTH = 60 * 24 * 30


class PricesInjector:
    def __init__(self, pricelist):
        self.pricelist = pricelist

    def calculate_vm_price(self, vm):
        price = 0

        # Count price of each disk
        for disk in vm['disks']:
            price += self.pricelist[disk['type']] * disk['size']

        # Count CPU and RAM only for running VMs
        if vm['status'] == 'ACTIVE':
            price += self.pricelist['cpu'] * vm['cpus']
            price += self.pricelist['ram'] * vm['ram'] / 1024

        # Count white IPs
        price += self.pricelist['ip'] * (len(vm['ip']) - 1)

        # Count licenses
        for license in vm['licenses']:
            if license not in self.pricelist:
                continue

            # WARNING: MS Windows Server licenses are counted per 2 CPUs
            price_mult = (vm['cpus'] / 2 if license == 'mswinsrv' else 1)

            price += price_mult * self.pricelist[license]

        # Set price of month and minute
        return price / MINUTES_IN_MONTH

    def add_prices_to_list(self, vm_list):
        for vm in vm_list:
            vm['price'] = self.calculate_vm_price(vm)


class LoadPricesFromDBTask(luigi.Task):
    # Load prices from DB
    def requires(self):
        return [
            LoadPricesToDBTask(),
            PrepareDBTask()
        ]

    def output(self):
        return luigi.LocalTarget(config.jsons.current_prices)

    def run(self):
        pricelist = {}
        for price in VMPrices.select():
            pricelist[price.resource] = price.price

        # Save prices to file
        with open(config.jsons.current_prices, 'w') as f:
            json.dump(pricelist, f)


class CalculateVMPricesTask(luigi.Task):
    # Calculate prices for each VM
    def requires(self):
        return [
            LoadPricesFromDBTask(),
            GetVMDataTask()
        ]

    def output(self):
        return luigi.LocalTarget(config.jsons.vm_prices)

    def run(self):
        # Load prices from file
        pricelist = json.load(open(config.jsons.current_prices, 'r'))

        # Load VM list from file
        vm_list = json.load(open(config.jsons.vm_raw_file, 'r'))

        # Count prices
        prices = PricesInjector(pricelist)
        prices.add_prices_to_list(vm_list)

        # Save prices to file
        with open(self.output().path, 'w') as f:
            json.dump(vm_list, f)

        # Remove current prices file
        if os.path.exists(config.jsons.current_prices):
            os.remove(config.jsons.current_prices)

        # Remove raw list to allow get new data
        if os.path.exists(config.jsons.vm_raw_file):
            os.remove(config.jsons.vm_raw_file)


if __name__ == '__main__':
    luigi.run()
