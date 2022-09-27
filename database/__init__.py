import atexit
import database.settings

# ensure settings saves on exit and loads on entry
database.settings.load()
atexit.register(database.settings.dump)
