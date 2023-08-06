import logging
import logging.config
from logger_rewrite.utils import Cfg


def setup_logging(save_dir, default_level=logging.INFO):
    config = Cfg.load_config_from_name()
    for _, handler in config['handlers'].items():
        if 'filename' in handler:
            handler['filename'] = str(save_dir / handler['filename'])
    logging.config.dictConfig(config)

