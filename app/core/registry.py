_REGISTRY: dict = {}


class RegisteredHandler:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "name"):
            _REGISTRY[cls.name] = cls

    def execute(self):
        raise NotImplementedError


class EmailHandler(RegisteredHandler):
    name = "email"

    def execute(self):
        print("Sending email notification...")


class SlackAlertHandler(RegisteredHandler):
    name = "slack"

    def execute(self):
        print("Posting alert to Slack...")


def get_handler(name: str) -> RegisteredHandler:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"No handler registered for: {name}")
    return cls()
