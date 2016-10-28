from protorpc import messages


class UserRankingsForm(messages.Message):
    username = messages.StringField(1, required=True)
    wins = messages.IntegerField(2, required=True)
    total = messages.IntegerField(3, required=True)
    win_percentage = messages.FloatField(4, required=True)
    ranking = messages.IntegerField(5, required=True)


class UserRankingsForms(messages.Message):
    items = messages.MessageField(UserRankingsForm, 1, repeated=True)

