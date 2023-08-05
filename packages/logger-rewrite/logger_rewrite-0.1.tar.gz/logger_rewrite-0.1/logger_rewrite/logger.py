import json
import logging
import logging.config
from pathlib import Path
from collections import OrderedDict


def setup_logging(save_dir, log_config='logger_config.json', default_level=logging.INFO):
    log_config = Path(__file__).parent.joinpath(log_config)
    if log_config.is_file():
        config = read_json(log_config)
        for _, handler in config['handlers'].items():
            if 'filename' in handler:
                handler['filename'] = str(save_dir / handler['filename'])
        logging.config.dictConfig(config)
    else:
        print('Warning: logging configuration file is not found in {}'.format(log_config))
        logging.basicConfig(level=default_level)


def read_json(filename):
    filename = Path(filename)
    with filename.open('rt', encoding='utf-8') as handle:
        return json.load(handle, object_hook=OrderedDict)
