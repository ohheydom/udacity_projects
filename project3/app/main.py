import os
import webapp2

from google.appengine.ext import ndb
from jinja_helper import jinja_env, render_str
from login_helper import build_secure_val, check_secure_val
from models import User, Post, Comment, Like
from validation_helper import check_errors, validate_subject_and_content


# Main Handler class all other handlers will inherit from
class Handler(webapp2.RequestHandler):
    def get_secure_cookie(self, cookie_name):
        cookie = self.request.cookies.get(cookie_name)
        return cookie and check_secure_val(cookie)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        username = self.get_secure_cookie('username')
        self.user = username and User.by_username(username)

    def logged_in(self):
        return self.user

    def login(self, username):
        self.set_secure_cookie('username', username)

    def logout(self):
        self.response.delete_cookie('username')

    def render(self, template, **params):
        self.write(render_str(template, **params))

    def set_secure_cookie(self, cookie_name, val):
        cookie_val = build_secure_val(val)
        self.response.set_cookie(cookie_name, cookie_val)

    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)


# Handles the dashboard for logged in users
class DashboardHandler(Handler):
    def get(self):
        if self.user:
            posts = Post.query(ancestor=self.user.key).order(-Post.created).fetch()
            self.render('dashboard.html', current_user=self.user, posts=posts)
        else:
            self.redirect('/login')


# Handles deleting comments
class DeleteCommentHandler(Handler):
    def post(self, username, post_slug, comment_id):
        if not self.logged_in():
            return self.redirect('/login')

        post = Post.find_by_user_and_slug(username, post_slug)
        comment = Comment.get_by_id(int(comment_id), parent=post.key)
        author_username = comment.author.get().username

        if author_username != self.user.username:
            return self.redirect('/dashboard')

        comment.key.delete()
        self.redirect(post.post_link())


# Handles deleting posts
class DeleteUserPostHandler(Handler):
    def post(self, username, post_slug):
        if not self.logged_in() or username != self.user.username:
            return self.redirect('/login')

        if self.user.username != username:
            return self.redirect('/dashboard')

        post = Post.find_by_user_and_slug(username, post_slug)

        if post:
            ndb.delete_multi([post.key] + Comment.query(ancestor=post.key)
                .fetch(keys_only=True))
            self.redirect('/dashboard')


# Handles editing comments
class EditCommentHandler(Handler):
    def get(self, username, post_slug, comment_id):
        if not self.logged_in():
            return self.redirect('/login')

        post = Post.find_by_user_and_slug(username, post_slug)
        comment = Comment.get_by_id(int(comment_id), parent=post.key)
        author_username = comment.author.get().username

        if author_username != self.user.username:
            return self.redirect('/dashboard')

        self.render('editcomment.html', comment=comment)

    def post(self, username, post_slug, comment_id):
        if not self.logged_in():
            return self.redirect('/login')

        post = Post.find_by_user_and_slug(username, post_slug)
        if not post:
            return self.render("404.html")

        comment = Comment.get_by_id(int(comment_id), parent=post.key)
        if not comment:
            return self.redirect('/dashboard')

        author_username = comment.author.get().username

        if not (author_username == self.user.username):
            return self.redirect('/dashboard')

        content = self.request.get('content')
        comment.content = content
        comment.put()
        self.redirect(post.post_link())


# Handles editing posts
class EditUserPostHandler(Handler):
    def get(self, username, post_slug):
        if not self.logged_in() or username != self.user.username:
            return self.redirect('/login')

        post = Post.find_by_user_and_slug(username, post_slug)

        if post:
            self.render('editpost.html', post=post, current_user=self.user)

    def post(self, username, post_slug):
        if not self.logged_in() or username != self.user.username:
            return self.redirect('/login')

        post = Post.find_by_user_and_slug(username, post_slug)
        if not post:
            return self.render("404.html")

        subject = self.request.get('subject')
        content = self.request.get('content')

        errors = validate_subject_and_content(subject, content)

        if errors:
            self.render('editpost.html', post=post, current_user=self.user,
                        errors=errors)
        else:
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/user/{}/{}'.format(username, post_slug))


# Handles main Index
class IndexHandler(Handler):
    def get(self):
        posts = Post.query().order(-Post.created).fetch(10)
        self.render('index.html', posts=posts, current_user=self.user)


# Handles liking and disliking posts
class LikeUserPostHandler(Handler):
    def post(self, username, post_slug):
        if not self.logged_in():
            return self.redirect('/login')

        value = self.request.get('like')
        post = Post.find_by_user_and_slug(username, post_slug)
        same_user = self.user.username == username

        if same_user or not (value in ['Like', 'Dislike'] or post):
            return self.redirect('/dashboard')

        bool_val = True if value == 'Like' else False
        like_exist = post.find_like_by_user(self.user)

        if like_exist:
            if like_exist.value != bool_val:
                like_exist.value = like_exist.value != True #Swap T/F values
                if like_exist.put():
                    post.likes += 1 if bool_val else -1
                    post.dislikes -= 1 if bool_val else -1
                    post.put()
            else:
                like_exist.key.delete()
                if bool_val:
                    post.likes -= 1
                else:
                    post.dislikes -= 1
                post.put()
        else:
            like = Like(value=bool_val, parent=post.key, author=self.user.key)
            if like.put():
                if bool_val:
                    post.likes += 1
                else:
                    post.dislikes += 1
                post.put()
        self.write(post.render_likes(self.user))


# Handles logging in
class LoginHandler(Handler):
    def get(self):
        if self.get_secure_cookie('username'):
            self.redirect('/dashboard')
        else:
            self.render('login.html', errors=None)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        if User.login(username, password):
            self.login(username)
            self.redirect('/dashboard')
        else:
            self.render('login.html', errors=True, username=username)


# Handles logging out
class LogoutHandler(Handler):
    def get(self):
        self.logout()
        self.redirect('/')


# Handles creating new posts
class NewUserPostHandler(Handler):
    def render_new_post(self, **kwargs):
        self.render('newpost.html', **kwargs)

    def get(self):
        if not self.logged_in():
            return self.redirect('/login')

        self.render_new_post(current_user=self.user)

    def post(self):
        if not self.logged_in():
            return self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')
        errors = validate_subject_and_content(subject, content)

        if errors:
            self.render_new_post(subject=subject, content=content,
                                 errors=errors, current_user=self.user)
        else:
            slug = Post.slugify(subject)
            post = Post(subject=subject, content=content,
                            slug=slug,
                            parent=self.user.key)
            post.put()
            self.redirect('/user/{}/{}'.format(self.user.username, slug))


# Handles creating new comments
class NewCommentHandler(Handler):
    def post(self, username, post_slug):
        if not self.logged_in():
            return self.redirect('/login')

        post = Post.find_by_user_and_slug(username, post_slug)
        if not post:
            return self.render("404.html")

        content = self.request.get('content')
        if not content:
            comment_error = 'Comment field must not be empty.'
            comments = post.get_comments()
            self.render('permalink.html', post=post,
                        current_user=self.user,
                        comments=comments,
                        comment_error = comment_error)
            return
        comment = Comment(content=content, author=self.user.key, parent=post.key)
        comment.put()
        self.redirect('/user/{}/{}'.format(username, post_slug))


# Handles creating new users
class NewUserHandler(Handler):
    def get(self):
        self.render('signup.html', errors={}, params={'username': '', 'email': ''})

    def post(self):
        params = {}
        params['username'] = self.request.get('username')
        params['password'] = self.request.get('password')
        params['verify'] = self.request.get('verify')
        params['email'] = self.request.get('email')
        errors = check_errors(params)

        if len(errors) == 0:
            if User.by_username(params['username']):
                errors['username'] = 'Username already exists.'
                self.render('signup.html', errors=errors, params=params)
            else:
                user = User.register(params['username'],
                                     params['password'],
                                     params['email'])
                if user.put():
                    self.login(params['username'])
                    self.redirect('/dashboard')
        else:
            self.render('signup.html', errors=errors, params=params)


# Handles viewing individual posts
class UserPostHandler(Handler):
    def get(self, username, post_slug):
        post = Post.find_by_user_and_slug(username, post_slug)
        if not post:
            return self.render("404.html")

        comments = post.get_comments()
        self.render('permalink.html', post=post,
                    current_user=self.user, comments=comments)


post_regex = '/user/([a-zA-Z\d_-]+)/([a-zA-Z\d_-]+)'
routes = [('/', IndexHandler),
          ('/dashboard/newpost/?$', NewUserPostHandler),
          ('{}/newcomment/?$'.format(post_regex), NewCommentHandler),
          ('{}/comment/(\d+)/delete/?$'.format(post_regex), DeleteCommentHandler),
          ('{}/comment/(\d+)/edit/?$'.format(post_regex), EditCommentHandler),
          ('{}/edit/?$'.format(post_regex), EditUserPostHandler),
          ('{}/delete/?$'.format(post_regex), DeleteUserPostHandler),
          ('{}/like/?$'.format(post_regex), LikeUserPostHandler),
          ('{}/?$'.format(post_regex), UserPostHandler),
          ('/signup/?$', NewUserHandler),
          ('/dashboard/?$', DashboardHandler),
          ('/login/?$', LoginHandler),
          ('/logout', LogoutHandler)]

app = webapp2.WSGIApplication(routes, debug=True)
