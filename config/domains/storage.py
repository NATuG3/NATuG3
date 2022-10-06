import plotting.datatypes
import logging


logger = logging.getLogger(__name__)


def load():
    global current
    current = [plotting.datatypes.domain(9, 0)] * 14
