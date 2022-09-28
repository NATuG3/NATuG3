import atexit
import config.workers

# ensure settings saves on exit and loads on entry
config.workers.load()
atexit.register(config.workers.dump)