#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from msilib.schema import Class
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db_setup, Venue, Show, Artist
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = db_setup(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    form = VenueForm()
    current_time = datetime.now()
    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    venues_state_and_city = ''
    data = list()
    for venue in venues:
        upcoming_shows = Show.query.filter(
            Show.venue_id == venue.id, Show.start_time > current_time).count()
        if venues_state_and_city == venue.city + venue.state:
            data[len(data) - 1]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": upcoming_shows
            })
        else:
            venues_state_and_city = venue.city + venue.state
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming_shows
                }]
            })
    return render_template('pages/venues.html', areas=data, form=form)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    venue_query = Venue.query.filter(Venue.name.ilike(
        '%' + request.form['search_term'] + '%'))
    venue_list = list(map(Venue.short, venue_query))
    response = {
        "count": len(venue_list),
        "data": venue_list
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_query = Venue.query.get(venue_id)
    if venue_query:
        venues_details = Venue.detail(venue_query)
        current_time = datetime.now()
        new_shows_query = Show.query.join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
        new_show = list(map(Show.artists_details, new_shows_query))
        venues_details["upcoming_shows"] = new_show
        venues_details["upcoming_shows_count"] = len(new_show)
        past_shows_query = Show.query.join(Venue).filter(
            Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
        past_shows = list(map(Show.artists_details, past_shows_query))
        venues_details["past_shows"] = past_shows
        venues_details["past_shows_count"] = len(past_shows)

    return render_template('pages/show_venue.html', venue=venues_details)
#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    if form.validate_on_submit():
        data = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            genres=form.genres.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            description=form.seeking_description.data
        )
        db.session.add(data)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
        db.session.close()
        return render_template('pages/home.html')
    else:
        flash(form.errors)
        return render_template('forms/new_venue.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venues_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venues_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
        return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    form = ArtistForm()
    artist_query = Artist.query.all()
    return render_template('pages/artists.html', artists=artist_query, form=form)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    artists_query = Artist.query.filter(
        Artist.name.ilike('%' + request.form['search_term'] + '%'))
    artrist_list = list(map(Artist.short, artists_query))
    response = {
        "count": len(artrist_list),
        "data": artrist_list
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artists_query = Artist.query.get(artist_id)
    if artists_query:
        artists_details = Artist.details(artists_query)
        current_time = datetime.now()
        new_shows_query = Show.query.join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
        new_shows_list = list(map(Show.venues_details, new_shows_query))
        artists_details["upcoming_shows"] = new_shows_list
        artists_details["upcoming_shows_count"] = len(new_shows_list)
        past_shows_query = Show.query.join(Artist).filter(
            Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
        past_shows_list = list(map(Show.venues_details, past_shows_query))
        artists_details["past_shows"] = past_shows_list
        artists_details["past_shows_count"] = len(past_shows_list)
        return render_template('pages/show_artist.html', artist=artists_details)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    artists_data = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(obj=artists_data)
    return render_template('forms/edit_artist.html', form=form, artist=artists_data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    form = ArtistForm(request.form)
    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    if artist:
        if form.validate_on_submit():
            try:
                artist.name = form.name.data
                artist.city = form.city.data
                artist.state = form.state.data
                artist.phone = form.phone.data
                artist.genres = form.genres.data
                artist.image_link = form.image_link.data
                artist.facebook_link = form.facebook_link.data
                artist.website_link = form.website_link.data
                artist.looking_for_venues = form.seeking_venue.data
                artist.description = form.seeking_description.data
                Artist.update(artist)
                flash('Venue ' + artist.name + ' was successfully updated!')
                return redirect(url_for('show_artist', artist_id=artist_id))
            except:
                db.session.rollback()
                db.session.close()
                flash(
                    'An error occurred. Artist ' +
                    request.form.get("name") +
                    ' could not be updated.'
                )
        else:
            print(form.errors)
            return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    form = VenueForm(obj=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    if venue:
        if form.validate_on_submit():
            try:
                venue.name = form.name.data
                venue.city = form.city.data
                venue.state = form.state.data
                venue.address = form.address.data
                venue.phone = form.phone.data
                venue.image_link = form.image_link.data
                venue.facebook_link = form.facebook_link.data
                venue.genres = form.genres.data
                venue.website_link = form.website_link.data
                venue.seeking_talent = form.seeking_talent.data
                venue.description = form.seeking_description.data
                Venue.update(venue)
                flash('Venue ' + venue.name + ' was successfully updated!')
                db.session.close()
                return redirect(url_for('show_venue', venue_id=venue_id))
            except:
                db.session.rollback()
                db.session.close()
                flash(
                    'An error occurred. Venue ' +
                    request.form.get("name") +
                    ' could not be updated.'
                )
                return render_template('forms/edit_venue.html', form=form)
        else:
            flash(form.errors)
            return redirect(url_for('edit_venue', venue_id=venue_id))
    # TODO: populate form with values from venue with ID <venue_id>

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    if form.validate_on_submit():
        try:
            data = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                genres=form.genres.data,
                website=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(data)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
            db.session.close()
            return render_template('pages/home.html')
        except SQLAlchemyError:
            db.session.rollback()
            db.session.close()
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred. Artist ' +
                  data.name + ' could not be listed.')
            return render_template('forms/new_artist.html', form=form)
    else:
        flash(form.errors)
        return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = Show.query.join(Venue).join(Artist).all()
    data = list(map(Show.detail, data))
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    if form.validate_on_submit():
        try:
            data = Show(
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data
            )
            db.session.add(data)
            db.session.commit()
    # on successful db insert, flash success
            flash('Show' + request.form['venue_id'] +
                  'Show was successfully listed!')
            db.session.close()
            return render_template('pages/home.html')
        except SQLAlchemyError:
            db.session.rollback()
            db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred. Show ' +
                  data.venues_id + ' could not be listed.')
            return render_template('forms/new_show.html', form=form)
    else:
        flash(form.errors)
        return render_template('forms/new_show.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
