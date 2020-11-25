class Enum(object):
    @classmethod
    def get_fields(cls):
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("__") and not callable(v)
        }


class Status(Enum):
    doing = "doing"
    error = "error"
    done = "done"


REQUIRED_COLUMNS = set(
    [
        "total",
        "name",
        "status",
        "value",
        "start_timestamp",
        "update_timestamp",
        "timerange",
        "elapsed_sec",
    ]
)
REQUIRED_STATUS_OPTIONS = set(Status.get_fields())

POST_INTERVAL_SEC = 3