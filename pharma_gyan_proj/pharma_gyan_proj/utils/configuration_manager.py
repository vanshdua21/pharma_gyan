import json
import application_config.bank as bank_conf
import application_config.verification_steps as verification_conf
import application_config.payment_config as payment_conf
import application_config.document_config as document_conf
import application_config.ui_conf as ui_conf
from pharma_gyan_proj.utils.secret_manager import SecretManager
from pharma_gyan_proj.utils.logging_utils import Logger
from application_config.bank import CONFIGMANAGER_SETTINGS
from pharma_gyan_proj.utils.database_utils import get_connection, execute_select
from pharma_gyan_proj.db_models.eth_cms_conf import EthCmsConf
from pharma_gyan_proj.utils.newrelic_helpers import push_error_to_newrelic
logger = Logger()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigurationManager(metaclass=Singleton):

    def __init__(self):
        self.bank_conf = bank_conf
        self.verification_conf = verification_conf
        self.payment_conf = payment_conf
        self.document_conf = document_conf
        self.ui_conf = ui_conf
        self.configs_from_db = {}
        self.db_eth_cms_conf = EthCmsConf()
        self.secret_manager_object = SecretManager()

    def get(self, config_name):
        logger.info(f'config_name : {config_name}')
        config_info = CONFIGMANAGER_SETTINGS.get(config_name, None)
        config_source = 'FILE'
        config_source_name = 'bank_conf'
        if config_info is not None:
            config_source = config_info.get('SOURCE')
            config_source_name = config_info.get('KEY')
        if config_source == 'SECRET_MANAGER':
            return self.get_secret_from_secretmanager(config_source_name, config_name)
        elif config_source == 'FILE':
            return self.get_secret_from_file(config_source_name, config_name)
        elif config_source == 'DB':
            if self.configs_from_db.get(config_name) is None:
                config = self.get_secret_from_db(config_source_name, config_name)
                if config is not None:
                    config_json = json.loads(config)
                    self.configs_from_db.update({config_name: config_json})
                    return config_json
            return self.configs_from_db.get(config_name)


    def get_secret_from_secretmanager(self, config_source_name, config_name):
        logger.info(f'config_source_name : {config_source_name}, config_name : {config_name} , key : get_secret_from_secretmanager' )
        secret_data = self.secret_manager_object.get_secret(config_source_name)
        secret_json = json.loads(secret_data)
        return secret_json.get(config_name)
    
    def get_secret_from_file(self, config_source_name, config_name):
        logger.info(f'config_source_name : {config_source_name}, config_name : {config_name}, key : get_secret_from_file')
        return eval(f"self.{config_source_name}.{config_name}")

    def get_secret_from_db(self, config_source_name, config_name):
        logger.info(f'config_source_name : {config_source_name}, config_name : {config_name}, key : get_secret_from_db')
        config = self.db_eth_cms_conf.get_conf_by_active_version({"config_key": config_name})
        if config is None:
            logger.errror(f"Exception : unable to fetch config {config_name} from db")
            push_error_to_newrelic({"get_secret_from_db": f"Exception : unable to fetch config {config_name} from db, key : get_secret_from_db"})
            return {}
        return config
