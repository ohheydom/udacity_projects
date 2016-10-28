import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb


class SendReminderEmailHandler(webapp2.RequestHandler):
    """ SendRemdinerEmailHandler e-mails a user when it is his/her turn
    in a game of Farkle. Currently, I'm only printing the information
    to the standard output because the application is not deployed and
    doesn't have real users.
    """
    def post(self):
        app_id = app_identity.get_application_id()
        player = self.request.get('player')
        previous_player = self.request.get('previous_player')
        email = self.request.get('email')
        game_id = self.request.get('game_id')
        subject = 'Farkle Reminder: It is your turn!'
        body = 'Hello {}, it is currently your turn against {} in game {}.' \
            .format(player, previous_player, game_id)

        # mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
        #               email, subject, body)

        print 'Subject: {}'.format(subject)
        print 'Body: {}'.format(body)


app = webapp2.WSGIApplication([
    ('/send_reminder_email', SendReminderEmailHandler)], debug=True)

