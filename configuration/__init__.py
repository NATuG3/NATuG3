import configuration.nucleic_acid.storage
import configuration.domains.storage
import logging


configuration.nucleic_acid.storage.load()
configuration.domains.storage.load()
logging.getLogger(__name__).info("Loaded the configuration.")
