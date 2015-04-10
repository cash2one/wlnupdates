

from hashlib import md5
import re
from app import db
from app import app

import sys
if sys.version_info >= (3, 0):
	enable_search = False
else:
	enable_search = True
	import flask.ext.whooshalchemy as whooshalchemy


followers = db.Table(
	'followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class Series(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	title       = db.Column(db.Text())
	description = db.Column(db.Text())
	type        = db.Column(db.Text())
	origin_loc  = db.Column(db.Text())
	demographic = db.Column(db.Text())
	orig_lang   = db.Column(db.Text())
	__table_args__ = (
		db.UniqueConstraint('title'),
		)


class Tags(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	series      = db.Column(db.Integer, db.ForeignKey('series.id'))
	weight      = db.Column(db.Float, default=1)
	tag         = db.Column(db.Text(), nullable=False)
	__table_args__ = (
		db.UniqueConstraint('series', 'tag'),
		)

class Genres(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	series      = db.Column(db.Integer, db.ForeignKey('series.id'))
	genre       = db.Column(db.Text(), nullable=False)

	__table_args__ = (
		db.UniqueConstraint('series', 'genre'),
		)

class Author(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	series      = db.Column(db.Integer, db.ForeignKey('series.id'))
	author      = db.Column(db.Text(), nullable=False)

	__table_args__ = (
		db.UniqueConstraint('series', 'author'),
		)

class Illustrators(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	series      = db.Column(db.Integer, db.ForeignKey('series.id'))
	name        = db.Column(db.Text(), nullable=False)

	__table_args__ = (
		db.UniqueConstraint('series', 'name'),
		)

class Translators(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	group_name  = db.Column(db.Text(), nullable=False)
	group_site  = db.Column(db.Text())
	__table_args__ = (
		db.UniqueConstraint('group_name'),
		)

class Releases(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	series      = db.Column(db.Integer, db.ForeignKey('series.id'))
	volume      = db.Column(db.Float(), nullable=False)
	chapter     = db.Column(db.Float(), nullable=False)
	tlgroup     = db.Column(db.Integer, db.ForeignKey('translators.id'))



class Covers(db.Model):
	id          = db.Column(db.Integer, primary_key=True)
	series      = db.Column(db.Integer, db.ForeignKey('series.id'))
	volume      = db.Column(db.Float(), nullable=False)
	chapter     = db.Column(db.Float(), nullable=False)
	desc        = db.Column(db.Text)
	fsPath      = db.Column(db.Text)
	hash        = db.Column(db.Text, nullable=False)



class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	followed = db.relationship('User',
							   secondary=followers,
							   primaryjoin=(followers.c.follower_id == id),
							   secondaryjoin=(followers.c.followed_id == id),
							   backref=db.backref('followers', lazy='dynamic'),
							   lazy='dynamic')

	@staticmethod
	def make_valid_nickname(nickname):
		return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname=nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname=new_nickname).first() is None:
				break
			version += 1
		return new_nickname

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3

	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
			(md5(self.email.encode('utf-8')).hexdigest(), size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		return Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id).order_by(
					Post.timestamp.desc())

	def __repr__(self):  # pragma: no cover
		return '<User %r>' % (self.nickname)


class Post(db.Model):
	__searchable__ = ['body']

	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	language = db.Column(db.String(5))

	def __repr__(self):  # pragma: no cover
		return '<Post %r>' % (self.body)


if enable_search:
	whooshalchemy.whoosh_index(app, Post)


# DROP TABLE author;
# DROP TABLE genres;
# DROP TABLE illustrators;
# DROP TABLE migrate_version;
# DROP TABLE releases;
# DROP TABLE series;
# DROP TABLE tags;
# DROP TABLE translators;