import os
from dataclasses import dataclass
from pathlib import Path
import configparser


STATES_DIR = (Path(__file__).parent / '..' / 'states').resolve()
# if states directory doesn't exist, create it
if not os.path.exists(STATES_DIR):
    os.mkdir(STATES_DIR)

MAIN_CONFIG = (Path(__file__).parent / '..' / 'vkmon.ini').resolve()


def snake_to_env_vars(s):
    return s.upper().replace('-', '_')


@dataclass
class PostgresConfig:
    host: str
    database: str
    username: str
    password: str
    port: int = 5432


@dataclass
class VkCredentials:
    user_domain_name: str
    username: str
    password: str
    project_id: str
    region_name: str
    auth_url: str = "https://infra.mail.ru:35357/v3"


@dataclass
class FlagsPaths:
    load_metrics_flag: Path = STATES_DIR / ".metrics"
    load_changes_flag: Path = STATES_DIR / ".changes"
    db_success_flag: Path = STATES_DIR / ".db_success"
    prices_load_success_flag: Path = STATES_DIR / ".price_load_success"


@dataclass
class JsonsTempData:
    vm_raw_file: Path = STATES_DIR / "vm_raw.json"
    vk_api_file: Path = STATES_DIR / "vk_api.json"
    current_prices: Path = STATES_DIR / "tmp_current_prices.json"
    vm_prices: Path = STATES_DIR / "vm_prices.json"


@dataclass
class GeneralConfig:
    raw_store_period_days: int = 7
    metrics_store_period_days: int = 30


@dataclass
class Config:
    general: GeneralConfig
    postgres_config: PostgresConfig
    vk_credentials: VkCredentials
    flags_paths: FlagsPaths
    jsons: JsonsTempData
    prices: dict

    @classmethod
    def from_file(cls):
        raw_config = configparser.ConfigParser()
        with open(MAIN_CONFIG) as f:
            raw_config.read_file(f)

        subconfigs = {}
        for section, section_type in cls.__dict__['__annotations__'].items():
            section_dict = cls.__dict__['__annotations__'][section].__dict__
            if '__annotations__' in section_dict:
                # We have normal data class
                list_of_fields = section_dict['__annotations__'].keys()
            else:
                # We have dict, get list of fields from config
                list_of_fields = raw_config[section].keys()
            class_default_fields = [f for f in section_dict.keys() if not f.startswith('__')]

            fileds = {}
            for field in list_of_fields:
                env_var = snake_to_env_vars(section + '_' + field)

                # Firstly try to get value from env
                if env_var in os.environ:
                    fileds[field] = os.environ[env_var]

                # Than try to get value from config
                elif section in raw_config and field in raw_config[section]:
                    fileds[field] = raw_config[section][field]

                # If there's no value in env or config, set default value
                elif field in class_default_fields:
                    fileds[field] = section_dict[field]

                # If there's no default, raise exception
                else:
                    raise Exception(f"Missing value for {section}.{field}")

            # write received data from env/config to subconfig
            subconfigs[section] = section_type(**fileds)

        return cls(**subconfigs)


config: Config = Config.from_file()
