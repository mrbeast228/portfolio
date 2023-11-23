from playhouse.postgres_ext import *

from vk_config import config


db = PostgresqlExtDatabase(
    config.postgres_config.database,
    host=config.postgres_config.host,
    port=config.postgres_config.port,
    user=config.postgres_config.username,
    password=config.postgres_config.password,
)


class BaseModel(Model):
    class Meta:
        database = db
        schema = 'vm_data'


# Schemas must correspond to the db/schema.sql
class VMMetrics(BaseModel):
    id = PrimaryKeyField()
    date_time = DateTimeField()
    vm_id = CharField()
    vm_name = CharField()
    vm_state = IntegerField()
    vm_tags = JSONField()
    vm_metadata = JSONField()
    vm_resources = JSONField()
    vm_price_min = FloatField()

    class Meta:
        table_name = 'vm_metrics'


class VMChanges(BaseModel):
    id = PrimaryKeyField()
    date_time = DateTimeField()
    vm_id = CharField()
    vm_name = CharField()
    vm_state = IntegerField()
    vm_tags = JSONField()
    vm_metadata = JSONField()
    vm_price = FloatField()
    vm_config = JSONField()

    class Meta:
        table_name = 'vm_changes'


class VMPrices(BaseModel):
    id = PrimaryKeyField()
    resource = CharField()
    price = FloatField()

    class Meta:
        table_name = 'vm_prices'


class VMRaw(BaseModel):
    id = PrimaryKeyField()
    date_time = DateTimeField()
    vm_id = CharField()
    vm_name = CharField()
    vm_tags = JSONField()
    vm_metadata = JSONField()
    vm_state = IntegerField()
    vm_price = FloatField()
    vm_config = JSONField()

    class Meta:
        table_name = 'vm_raw'
