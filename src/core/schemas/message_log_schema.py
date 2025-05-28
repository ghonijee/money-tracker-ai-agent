class CreateMessageLogSchema:
    datetime: str
    message: dict
    model: str
    status: bool

    def __init__(self, datetime, message, model, status=True):
        self.datetime = datetime
        self.message = message
        self.model = model
        self.status = status

    def to_dict(self):
        return {
            "datetime": self.datetime,
            "message": self.message,
            "model": self.model,
            "status": self.status
        }