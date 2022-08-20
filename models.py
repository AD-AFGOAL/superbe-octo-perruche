from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


# TODO: connect to a local postgresql database
def db_setup(app):
    db.app = app
    db.init_app(app)
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    description = db.Column(db.String(500))
    seeking_talent = db.Column(Boolean, default=False)
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    venue_shows = db.relationship("Show", backref="venue", lazy=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def long(self):
        print(self)
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
        }

    def detail(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'description': self.description,
            'image_link': self.image_link
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    artist_show = db.relationship("Show", backref="artist", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def short(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def details(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,

        }

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):

    __tablename__ = 'show'
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def detail(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': Venue.query.get(self.venue_id).name,
            'artist_id': self.artist_id,
            'artist_name': Artist.query.get(self.artist_id).name,
            'artist_image_link': Artist.query.get(self.artist_id).image_link,
            'start_time': self.start_time
        }

    def artists_details(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': Artist.query.get(self.artist_id).name,
            'artist_image_link': Artist.query.get(self.artist_id).image_link,
            'start_time': self.start_time

        }

    def venues_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': Venue.query.get(self.venue_id).name,
            'venue_image_link': Venue.query.get(self.venue_id).image_link,
            'start_time': self.start_time

        }
