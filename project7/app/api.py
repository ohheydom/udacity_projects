import endpoints
import farkle
from google.appengine.ext import ndb
from models import (User, NewUserForm, NewGameForm, UserRankingsForms,
                    GameForm, Game, GameForms, GameHistoryForm, StringMessage)
from operator import itemgetter
from protorpc import remote, messages, message_types
from utilities import get_game_by_urlsafe, add_to_email_queue


SAVE_DICE_REQUEST = endpoints.ResourceContainer(
    urlsafe_key=messages.StringField(1),
    saved_dice=messages.IntegerField(2, repeated=True),
    bank=messages.BooleanField(3, required=True))
GET_USER_REQUEST = endpoints.ResourceContainer(
    username=messages.StringField(1))
URLSAFE_REQ = endpoints.ResourceContainer(urlsafe_key=messages.StringField(1))


@endpoints.api(name='farkle', version='v1')
class FarkleApi(remote.Service):
    @endpoints.method(request_message=NewUserForm,
                      response_message=StringMessage,
                      path='new_user',
                      name='new_user',
                      http_method='POST')
    def new_user(self, request):
        """Creates a new unique user."""
        if User.query(User.username == request.username).get():
            raise endpoints.ConflictException('User already exists.')

        user = User(username=request.username, email=request.email,
                    email_me=request.email_me)
        user.put()
        message = 'User {} has been created.'.format(request.username)

        return StringMessage(message=message)

    @endpoints.method(request_message=NewGameForm,
                      response_message=GameForm,
                      path='new_game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates a new game between two users."""
        user_1 = User.query(User.username == request.player_one_name).get()
        user_2 = User.query(User.username == request.player_two_name).get()
        if not user_1:
            raise endpoints.NotFoundException('Player One was not found.')

        if not user_2:
            raise endpoints.NotFoundException('Player Two was not found.')

        if user_1 == user_2:
            message = 'You cannot play against yourself.'
            raise endpoints.BadRequestException(message)

        game = Game.new_game(player_one=user_1.key,
                             player_two=user_2.key,
                             winning_total=request.winning_total)

        return game.to_form()

    @endpoints.method(request_message=URLSAFE_REQ,
                      response_message=GameForm,
                      path='game/{urlsafe_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Retrieves an existing game."""
        game = get_game_by_urlsafe(request.urlsafe_key)

        return game.to_form()

    @endpoints.method(request_message=URLSAFE_REQ,
                      response_message=StringMessage,
                      path='game/{urlsafe_key}/delete',
                      name='delete_game',
                      http_method='DELETE')
    def delete_game(self, request):
        """Deletes an unfinished game."""
        game = get_game_by_urlsafe(request.urlsafe_key)
        if not game:
            raise endpoints.NotFoundException('Game was not found.')

        if game.game_over:
            message = 'You cannot delete a completed game.'
            raise endpoints.BadRequestException(message)

        game.delete_game()

        return StringMessage(message='Game has been deleted.')

    @endpoints.method(request_message=SAVE_DICE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_key}/save_dice',
                      name='save_dice',
                      http_method='PUT')
    def save_dice(self, request):
        """Saves the selected dice to the user's game history and counts the
        score towards the current player's cumulative total. The total will
        only be added to the corresponding player's score once he/she banks
        the value. If he/she farkles, all points are lost.
        """
        game = get_game_by_urlsafe(request.urlsafe_key)
        if not game:
            raise endpoints.NotFoundException('Game was not found.')

        if game.game_over:
            message = 'The game is over.'
            return game.to_form(message=message)

        message = None
        saved_dice = request.saved_dice
        current_username = game.current_player.get().username

        if not game.save_dice(saved_dice):
            error = 'You must save at least one die and cannot save less'
            error += ' than three 2s, 3s, 4s, or 6s.'
            return game.to_form(error=error)

        if request.bank:
            message = '{} has banked {} on {} roll(s).'.format(
                current_username,
                game.current_player_score,
                game.roll_count)
            if game.endgame:
                message += game.end()
            else:
                game.tally_score()
                game.switch_current_player()
                add_to_email_queue(game, game.current_player.get().email_me)
        else:
            rem = 6 - len(game.saved_dice)
            if rem == 0:
                game.set_hot_dice()
                message = '{} has hot dice.'.format(current_username)
            else:
                game.roll_dice(rem)
                if farkle.score(game.current_dice) == 0:
                    message = '{} has farkled with the roll {}.'.format(
                        current_username,
                        game.current_dice)
                    if game.endgame:
                        message += game.end(farkle=True)
                    else:
                        game.switch_current_player()
                        add_to_email_queue(game,
                                           game.current_player.get().email_me)
                else:
                    message = '{} is continuing his/her roll.'.format(
                        current_username)

        return game.to_form(message=message)

    @endpoints.method(request_message=URLSAFE_REQ,
                      response_message=GameForm,
                      path='game/{urlsafe_key}/roll_dice',
                      name='roll_dice',
                      http_method='PUT')
    def roll_dice(self, request):
        """ Rolls the remaining available dice."""
        game = get_game_by_urlsafe(request.urlsafe_key)
        if not game:
            raise endpoints.NotFoundException('Game was not found.')

        if game.game_over:
            message = 'The game is over.'
            return game.to_form(message=message)

        rem = 6
        if game.saved_dice:
            rem -= len(game.saved_dice)

        game.roll_dice(rem)
        message = None

        if farkle.score(game.current_dice) == 0:
            message = '{} has farkled with the roll {}.'.format(
                game.current_player.get().username, game.current_dice)
            game.switch_current_player()

        return game.to_form(message=message)

    @endpoints.method(request_message=GET_USER_REQUEST,
                      response_message=GameForms,
                      path='user/{username}/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Gets all of a user's game based on username."""
        user = User.query(User.username == request.username).get()
        if not user:
            raise endpoints.NotFoundException('User was not found.')

        games = Game.query(ndb.AND(Game.game_over == False,
                                   ndb.OR(Game.player_one == user.key,
                                          Game.player_two == user.key)))

        return GameForms(items=[game.to_mini_form() for game in games])

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=UserRankingsForms,
                      path='user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Calculates all the users' rankings and returns them in
        descending order.
        """
        users = {}
        for u in User.query():
            users[u.username] = {'wins': 0, 'total': 0}

        for g in Game.query():
            if g.winner:
                player_1 = g.player_one.get().username
                player_2 = g.player_two.get().username
                if player_1 == g.winner:
                    users[player_1]['wins'] += 1
                else:
                    users[player_2]['wins'] += 1
                users[player_1]['total'] += 1
                users[player_2]['total'] += 1
        l = []
        for k, v in users.iteritems():
            w_p = 0
            if v['total'] > 0:
                w_p = float(v['wins']) / v['total']
                l.append({'username': k, 'wins': v['wins'],
                          'total': v['total'], 'win_percentage': w_p})
        items = []
        ranking = 1
        for i in sorted(l, key=itemgetter('win_percentage'), reverse=True):
            i['ranking'] = ranking
            ranking += 1
            items.append(i)

        return UserRankingsForms(items=items)

    @endpoints.method(request_message=URLSAFE_REQ,
                      response_message=GameHistoryForm,
                      path='game/{urlsafe_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns all the moves that the two players made during a game."""
        game = get_game_by_urlsafe(request.urlsafe_key)
        if not game:
            raise endpoints.NotFoundException('Game was not found.')

        return GameHistoryForm(urlsafe_key=request.urlsafe_key,
                               player_one_name=game.player_one.get().username,
                               player_two_name=game.player_two.get().username,
                               player_one_history=game.player_one_history,
                               player_two_history=game.player_two_history)


api = endpoints.api_server([FarkleApi])

