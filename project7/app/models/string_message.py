from protorpc import messages


class StringMessage(messages.Message):
    message = messages.StringField(1, required=True)

