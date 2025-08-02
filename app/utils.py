import json
import uuid
from datetime import datetime

class UUIDEncoder(json.JSONEncoder):
    """
    A custom JSON encoder to handle UUID objects, which are not
    natively serializable by the standard `json` library.
    """
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return super().default(obj)
