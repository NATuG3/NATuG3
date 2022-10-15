import config.nucleic_acid.storage
import config.domains.storage
import logging

config.nucleic_acid.storage.load()
config.domains.storage.load()
logging.getLogger(__name__).info("Loaded the config.")
