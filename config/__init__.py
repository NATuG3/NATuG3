import logging

import config.domains.storage
import config.nucleic_acid.storage
from config.settings import *

config.nucleic_acid.storage.load()
config.domains.storage.load()
logging.getLogger(__name__).info("Loaded the config.")
