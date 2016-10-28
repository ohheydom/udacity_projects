import farkle
from datetime import datetime
from google.appengine.ext import ndb
from protorpc import messages, message_types


class Game(ndb.Model):
    player_one = ndb.KeyProperty(required=True, kind='User')
    player_two = ndb.KeyProperty(required=True, kind='User')
    player_one_score = ndb.IntegerProperty(default=0)
    player_two_score = ndb.IntegerProperty(default=0)
    player_one_history = ndb.JsonProperty(default=[])
    player_two_history = ndb.JsonProperty(default=[])
    endgame = ndb.BooleanProperty(default=False)
    game_over = ndb.BooleanProperty(default=False)
    current_player = ndb.KeyProperty(required=True, kind='User')
    current_player_score = ndb.IntegerProperty(default=0)
    current_dice = ndb.IntegerProperty(repeated=True)
    saved_dice = ndb.IntegerProperty(repeated=True)
    winning_total = ndb.IntegerProperty(required=True)
    roll_count = ndb.IntegerProperty(default=0)
    completed = ndb.DateTimeProperty()
    hot_dice = ndb.BooleanProperty(default=False)
    winner = ndb.KeyProperty(kind='User')

    @classmethod
    def new_game(cls, player_one, player_two, winning_total=10000):
        game = Game(player_one=player_one, player_two=player_two,
                    winning_total=winning_total, current_player=player_one)
        game.put()

        return game

    def to_form(self, error=None, message=None):
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player_one_name = self.player_one.get().username
        form.player_one_score = self.player_one_score
        form.player_one_history = self.player_one_history
        form.player_two_name = self.player_two.get().username
        form.player_two_score = self.player_two_score
        form.player_two_history = self.player_two_history
        form.current_player = self.current_player.get().username
        form.current_player_score = self.current_player_score
        form.game_over = self.game_over
        form.winning_total = self.winning_total
        form.current_dice = self.current_dice
        form.saved_dice = self.saved_dice
        form.error = error
        form.message = message
        form.roll_count = self.roll_count
        form.hot_dice = self.hot_dice
        form.endgame = self.endgame
        form.completed = self.completed

        if self.winner:
            form.winner = self.winner.get().username

        return form

    def to_mini_form(self):
        form = SmallGameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player_one_name = self.player_one.get().username
        form.player_one_score = self.player_one_score
        form.player_two_name = self.player_two.get().username
        form.player_two_score = self.player_two_score
        form.winning_total = self.winning_total
        form.completed = self.completed

        if self.winner:
            form.winner = self.winner.get().username

        return form

    def end(self, farkle=False):
        if not farkle:
            self.tally_score()

        message = ''
        self.current_player_score = 0
        self.game_over = True
        self.current_dice = []
        self.saved_dice = []
        self.completed = datetime.now()

        if self.player_one_score > self.player_two_score:
            self.winner = self.player_one
            message += ' {} has won.'.format(self.player_one.get().username)
        elif self.player_two_score > self.player_one_score:
            self.winner = self.player_two
            message += ' {} has won.'.format(self.player_two.get().username)
        else:
            message += ' The game ended in a tie.'

        self.put()

        return message

    def delete_game(self):
        self.key.delete()

    def save_dice(self, indices):
        if not farkle.save_dice(self.current_dice, indices):
            return None

        current_dice = self.current_dice
        vs = [current_dice[i] for i in indices]
        score = farkle.score(vs)

        if self.current_player == self.player_one:
            self.player_one_history.append({'roll': vs,
                                            'score': score})
        else:
            self.player_two_history.append({'roll': vs,
                                            'score': score})

        self.saved_dice.extend(vs)
        self.current_player_score += score
        self.roll_count += 1
        self.put()

        return self

    def roll_dice(self, number):
        if self.current_dice and not self.saved_dice:
            return self

        dice = farkle.roll_dice(number)
        self.current_dice = dice
        self.put()

        return self

    def set_hot_dice(self):
        self.current_dice = []
        self.saved_dice = []
        self.hot_dice = True
        self.put()

        return self

    def switch_current_player(self):
        """ switch_current player switches the current player and wipes the
        current player score, current dice, saved dice, and roll count
        """
        if self.current_player == self.player_one:
            self.current_player = self.player_two
        else:
            self.current_player = self.player_one

        self.hot_dice = False
        self.current_player_score = 0
        self.current_dice = []
        self.saved_dice = []
        self.roll_count = 0
        self.put()

        return self

    def tally_score(self):
        if self.current_player == self.player_one:
            self.player_one_score += self.current_player_score
            if self.player_one_score >= self.winning_total:
                self.endgame = True
        else:
            self.player_two_score += self.current_player_score
            if self.player_two_score >= self.winning_total:
                self.endgame = True

        self.put()

        return self


class PlayerHistoryForm(messages.Message):
    roll = messages.IntegerField(1, repeated=True)
    score = messages.IntegerField(2)


class GameHistoryForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    player_one_name = messages.StringField(2, required=True)
    player_one_history = messages.MessageField(PlayerHistoryForm, 3,
                                               repeated=True)
    player_two_name = messages.StringField(4, required=True)
    player_two_history = messages.MessageField(PlayerHistoryForm, 5,
                                               repeated=True)


class NewGameForm(messages.Message):
    player_one_name = messages.StringField(1, required=True)
    player_two_name = messages.StringField(2, required=True)
    winning_total = messages.IntegerField(3, required=True)


class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    player_one_name = messages.StringField(2, required=True)
    player_one_score = messages.IntegerField(3, required=True)
    player_one_history = messages.MessageField(PlayerHistoryForm, 4,
                                               repeated=True)
    player_two_name = messages.StringField(5, required=True)
    player_two_score = messages.IntegerField(6, required=True)
    player_two_history = messages.MessageField(PlayerHistoryForm, 7,
                                               repeated=True)
    current_player = messages.StringField(8, required=True)
    current_player_score = messages.IntegerField(9, required=True)
    winning_total = messages.IntegerField(10, required=True)
    winner = messages.StringField(11)
    game_over = messages.BooleanField(12, required=True)
    current_dice = messages.IntegerField(13, repeated=True)
    saved_dice = messages.IntegerField(14, repeated=True)
    error = messages.StringField(15)
    message = messages.StringField(16)
    roll_count = messages.IntegerField(17)
    hot_dice = messages.BooleanField(18)
    endgame = messages.BooleanField(19)
    completed = message_types.DateTimeField(20)


class SmallGameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    player_one_name = messages.StringField(2, required=True)
    player_one_score = messages.IntegerField(3, required=True)
    player_two_name = messages.StringField(4, required=True)
    player_two_score = messages.IntegerField(5, required=True)
    winning_total = messages.IntegerField(6, required=True)
    winner = messages.StringField(7)
    completed = message_types.DateTimeField(8)


class GameForms(messages.Message):
    items = messages.MessageField(SmallGameForm, 1, repeated=True)

