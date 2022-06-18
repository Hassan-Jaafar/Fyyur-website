from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Association Object
class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    venues = db.relationship('Venue', backref='city')
    artists = db.relationship('Artist', backref='city')
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    play_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    venue_id = db.Column( db.Integer, db.ForeignKey('venue.id'),nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
    venue = db.relationship("Venue", back_populates="artists")
    artist = db.relationship("Artist", back_populates="venues")


class Artist(db.Model):
    __tablename__ = 'artist'

    venues = db.relationship('Show', back_populates="artist")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    venue_seeking = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(2000))
    city_id = db.Column( db.Integer, db.ForeignKey('city.id'))

class Venue(db.Model):
    __tablename__ = 'venue'
    artists = db.relationship('Show', back_populates="venue")
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    talent_seeking = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(2000), nullable=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
