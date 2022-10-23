import logging

from config.settings import *
import config.domains.storage
import config.nucleic_acid.storage

config.nucleic_acid.storage.load()
config.domains.storage.load()
logging.getLogger(__name__).info("Loaded the config.")
