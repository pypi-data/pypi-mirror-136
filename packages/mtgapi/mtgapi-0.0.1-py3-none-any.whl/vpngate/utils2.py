import os
import pynotify


class Utils:
    """Utility library where we abstract code"""

    @staticmethod
    def create_directory_path(filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))


    @staticmethod
    def send_message(title, message):
        pynotify.init("Test")
        notice = pynotify.Notification(title, message)
        notice.show()
        return
