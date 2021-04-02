import sys
from os import getcwd

from pynamotf.convert import model_to_resource


try:
    from chalicelib.models.db import NotificationModel
except ImportError:
    sys.path.append(getcwd())
    from chalicelib.models.db import NotificationModel


if __name__ == "__main__":
    print(str(model_to_resource(NotificationModel).format()))
