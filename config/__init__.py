import atexit
import config.nucleic_acid.storage

# ensure settings saves on exit and loads on entry
config.nucleic_acid.storage.load()
atexit.register(config.nucleic_acid.storage.dump)
