import sys
from time import time
import logging


def main():
    import storage
    import configuration.domains
    import configuration.nucleic_acid

    from computers.top_view import TopView
    from computers.side_view import SideView

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QIcon

    # initialize PyQt6 application
    storage.application = QApplication(sys.argv)
    storage.application.setStyle("Fusion")
    storage.application.setWindowIcon(QIcon("resources/icon.ico"))

    # store widget in class for easier direct access
    storage.top_view = TopView(
        configuration.domains.storage.current.domains,
        configuration.nucleic_acid.storage.current.D,
        configuration.nucleic_acid.storage.current.theta_c,
        configuration.nucleic_acid.storage.current.theta_s,
    )

    # store widget in class for easier direct access
    storage.side_view = SideView(
        configuration.domains.storage.current.domains,
        configuration.nucleic_acid.storage.current.Z_b,
        configuration.nucleic_acid.storage.current.Z_s,
        configuration.nucleic_acid.storage.current.theta_s,
        configuration.nucleic_acid.storage.current.theta_b,
        configuration.nucleic_acid.storage.current.theta_c,
    )

    import windows.constructor.main
    storage.windows.constructor = windows.constructor.main.Window()
    storage.windows.constructor.show()
    storage.windows.constructor.resizeEvent(None)  # trigger initial resize event

    # begin app event loop
    sys.exit(storage.application.exec())


if __name__ == "__main__":
    global logger

    logging.basicConfig(
        level=logging.DEBUG,
    )

    # log boot statement
    logging.debug(f"Booting @ {time()}")

    # mute pyqt logs
    logging.getLogger("PyQt6").setLevel(logging.INFO)

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    main()
