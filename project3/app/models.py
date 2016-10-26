import os
import re
import unicodedata

from google.appengine.ext import ndb
from login_helper import build_password_hash, valid_password
from jinja_helper import jinja_env, render_str

class Comment(ndb.Model):
    """ Comment stores the comments for each blog post.

    Parents - Post, User
    Columns - author, content, created
    """

    author = ndb.KeyProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)

    def comment_link(self):
        blogpost = self.key.parent().get()
        username = blogpost.key.parent().get().username
        slug = blogpost.slug
        return '/user/{}/{}/comment/{}'.format(username, slug, self.key.id())

    def render(self, current_user):
        return render_str('comment.html', comment=self, current_user=current_user)

class Like(ndb.Model):
    """ Like stores the likes/dislikes for each blog post.

    Parents - Post, User
    Columns - author, created, value (True = Like, False = Dislike)
    """

    author = ndb.KeyProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    value = ndb.BooleanProperty()

class Post(ndb.Model):
    """ Post stores all the blog posts.

    Parents - User
    Children - Like, Comment
    Columns - subject, content, created, likes, dislikes, slug, last_modified
    """

    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    dislikes = ndb.IntegerProperty(default=0)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    likes = ndb.IntegerProperty(default=0)
    subject = ndb.StringProperty(required=True)
    slug = ndb.StringProperty(required=True)

    @classmethod
    def find_by_user_and_slug(cls, username, slug):
        user = User.by_username(username)
        if user:
            return Post.query(ancestor=user.key).filter(Post.slug == slug).get()

    # Snippet borrowed from Django codebase
    @classmethod
    def slugify(cls, value):
        value = unicodedata.normalize('NFKD', unicode(value)) \
                .encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value).strip().lower()
        return re.sub(r'[-\s]+', '-', value)

    def find_like_by_user(self, user):
        return Like.query(ancestor=self.key).filter(Like.author == user.key).get()

    def post_link(self):
        return '/user/{}/{}'.format(self.key.parent().get().username, self.slug)

    def get_comments(self):
        return Comment.query(ancestor=self.key).order(-Comment.created).fetch()

    def render(self, render_link=True, render_snippet=False, current_user=None):
        self.render_text_ = self.content.replace('\n', '<br>')
        idx_more = self.render_text_.find('{{more}}')
        username = self.key.parent().get().username
        more_html = '<a href="/user/{}/{}">More...</a>'.format(username, self.slug)
        if idx_more >= 0:
            if render_snippet == True:
                self.render_text_ = self.render_text_[:idx_more] + more_html
            else:
                self.render_text_ = self.render_text_.replace('{{more}}', '')

        return render_str('post.html', post=self, render_link=render_link,
                          current_user=current_user)

    def render_likes(self, current_user=None):
        like_class = ''
        dislike_class= ''
        if current_user:
            likes = self.find_like_by_user(current_user)
            if likes != None:
                if likes.value:
                    like_class = 'button-muted'
                else:
                    dislike_class = 'button-muted'
        return render_str('likes.html', post=self, current_user=current_user,
                          like_class=like_class, dislike_class=dislike_class)

class User(ndb.Model):
    """ User contains all the user information.

    Parents - None
    Children - Post, Like, Comment
    Columns - email, username, password_hash
    """

    email = ndb.StringProperty(required=True)
    password_hash = ndb.StringProperty(required=True)
    username = ndb.StringProperty(required=True)

    @classmethod
    def by_username(cls, username):
        return cls.query(User.username == username).get()

    @classmethod
    def login(cls, username, password):
        user = cls.by_username(username)
        if user and valid_password(username, password, user.password_hash):
            return user

    @classmethod
    def register(cls, username, password, email):
        password_hash = build_password_hash(username, password)
        return cls(username=username,
                   email=email,
                   password_hash=password_hash)
