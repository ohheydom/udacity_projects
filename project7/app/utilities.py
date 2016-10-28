import endpoints
from google.appengine.ext import ndb
from google.appengine.api import taskqueue


def get_game_by_urlsafe(urlsafe):
    """Returns the game key if it exists in the database."""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except:
        raise endpoints.BadRequestException('Invalid Game Key')

    game = key.get()
    return game if game else None


def add_to_email_queue(game, email_me=True):
    """Adds a task to the e-mail queue."""
    if not email_me:
        return None

    current_player = game.current_player.get()
    previous_player = game.player_one.get()
    if game.current_player == game.player_one:
        previous_player = game.player_two.get()

    taskqueue.add(url='/send_reminder_email', target='worker',
                  params={'player': current_player.username,
                          'email': current_player.email,
                          'previous_player': previous_player.username,
                          'game_id': game.key.urlsafe()})

