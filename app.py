#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import json
import dateutil.parser
import babel
from flask_moment import Moment
from sqlalchemy import func, distinct
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
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

# real venues data.
@app.route('/venues')
def venues():
    data = []
    cities = db.session.query(City).all()
    for city in cities:
        venues = db.session.query(Venue).filter(Venue.city_id == city.id).order_by('id').all()
        venue_list= []
        for venue in venues:
            venue_list.append({
                "state":venue.state,
                "id": venue.id,
                "name":venue.name
            })
        if len(venue_list) != 0:
            data.append({"city":city.name, "state": venue_list[0]["state"] ,"venues": venue_list})

    return render_template('pages/venues.html', areas=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    cities = City.query.all()

    return render_template('forms/new_venue.html', form=form, cities=cities)



@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue()
        city_name = request.form.get('city')
        city = City.query.filter_by(name=city_name).first()
        venue.name = request.form.get('name')
        venue.city_id = city.id
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        list_genres = request.form.getlist('genres')
        venue.genres = ','.join(list_genres)
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.website = request.form.get('website')
        if request.form.get('venue_seeking') == 'y':
            print("its truuuuuuuuuuuuuuuuuuue")
            venue.talent_seeking = True
            venue.seeking_description = request.form.get('seeking_description')
        else:
            print("its fauuuuuult")
            venue.talent_seeking = False
            venue.seeking_description = request.form.get('seeking_description')
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue: ' +
            request.form['name'] + ' could not be listed.')
        else:
             flash('Venue: ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


# implementing search on venues with case-insensitive partial string search.
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_results = Venue.query.with_entities(Venue.id, Venue.name)\
    .filter(Venue.name.ilike(f"%{search_term}%")).all()
    data_list = []
    for result in search_results:
        data_list.append({
            "id": result.id,
            "name": result.name
        })
    response = {
        "count": len(search_results),
        "data": data_list
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


# showing the venue page with real venue data for a given venue_id
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    city = db.session.query(City).filter_by(id = venue.city_id).first()
    past_shows = []
    upcoming_shows = []
    shows = Show.query.filter_by(venue_id=venue_id)
    time_now = datetime.now()
    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        if show.play_time < time_now:
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.play_time
            })
        elif show.play_time > time_now:
             upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": show.play_time
            })
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(","),
        "address": venue.address,
        "city": city.name,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "talent_seeking": venue.talent_seeking,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    return render_template('pages/show_venue.html', venue=data)

# populating form with values from venue with ID <venue_id>
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    cities = City.query.all()
    city = db.session.query(City).filter_by(id = venue.city_id).first() # retrieve a city object for the given venue_id 
    form.name.data = venue.name
    form.city.data = city.name
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website
    form.talent_seeking.data = venue.talent_seeking
    form.seeking_description.data = venue.seeking_description
   
    return render_template('forms/edit_venue.html', form=form, venue=venue, cities=cities)

# take values from the form submitted, and update existing venue record with ID <venue_id> using the new attributes
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        city = db.session.query(City).filter_by(id = venue.city_id).first()
        venue.name = request.form.get('name')
        venue.city_id = city.id
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        list_genres = request.form.getlist('genres')
        venue.genres = ','.join(list_genres)
        venue.facebook_link = request.form.get('facebook_link')
        venue.image_link = request.form.get('image_link')
        venue.website = request.form.get('website_link')
        if (request.form.get('talent_seeking')) == 'y':
            venue.talent_seeking = True
            venue.seeking_description = request.form.get('seeking_description')
        else:
            venue.talent_seeking = False
            venue.seeking_description = request.form.get('seeking_description')

        db.session.add(venue)
        db.session.commit()
    except Exception as e:
        print(e.message)  
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue: ' +
            request.form['name'] + ' could not be edited.')
        else:
             flash('Venue: ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))


# delete a venue record with a given venue_id
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    name = Venue.query.with_entities(Venue.id, Venue.name).filter_by(id = venue_id).name
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue: ' + name + ' could not be deleted.')
        else:
            flash('Venue: ' + name + ' was successfully deleted!')
    return render_template('pages/home.html')



#  Artists
#  ----------------------------------------------------------------
# real artists data.
@app.route('/artists')
def artists():
    artists = Artist.query.with_entities(Artist.id, Artist.name).all()
    data = []
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        }) 
    return render_template('pages/artists.html', artists=data)


    #  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    cities = City.query.all()
    return render_template('forms/new_artist.html', form=form, cities=cities)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False 
    city_name = request.form.get('city')
    city = City.query.filter_by(name=city_name).first()
    try:
        artist = Artist()
        artist.name = request.form.get('name')
        artist.city_id = city.id
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        list_genres = request.form.getlist('genres')
        artist.genres = ','.join(list_genres)
        artist.facebook_link = request.form.get('facebook_link')
        artist.image_link = request.form.get('image_link')
        artist.website = request.form.get('website_link')
        if request.form.get('venue_seeking') == 'y':
            artist.venue_seeking = True
            artist.seeking_description = request.form.get('seeking_description')
        else:
            artist.venue_seeking = False
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist: ' +
            request.form['name'] + ' could not be listed.')
        else:
             flash('Artist: ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')



# implementing search on artists with case-insensitive partial string search.
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_results = Artist.query.with_entities(Artist.id, Artist.name)\
    .filter(Artist.name.ilike(f"%{search_term}%")).all()
    data_list = []
    for result in search_results:
        data_list.append({
            "id": result.id,
            "name": result.name
        })
    response = {
        "count": len(data_list),
        "data": data_list
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

# showing the artist page with real artist data for a given artist_id
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    city = City.query.filter_by(id=artist.city_id).first()
    past_shows = []
    upcoming_shows = []
    shows = Show.query.filter_by(artist_id=artist_id)
    time_now = datetime.now()
    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)
        if show.play_time < time_now:
            past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.play_time
            })
        elif show.play_time > time_now:
             upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.play_time
            })
    data = {
        "id": artist_id,
        "name": artist.name,
        "genres": artist.genres.split(","),
        "city": city.name,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "venue_seeking": artist.venue_seeking,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,

        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

# populating form with values from artist with ID <venue_id>
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    cities = City.query.all()
    artist = Artist.query.get(artist_id)
    city = City.query.filter_by(id = artist.city_id).first()
    form.name.data = artist.name
    form.city.data = city.name
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.venue_seeking.data = artist.venue_seeking
    form.seeking_description.data = artist.seeking_description


    return render_template('forms/edit_artist.html', form=form, artist=artist, cities=cities)

# take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        city_name = request.form.get('city')
        city = City.query.filter_by(name=city_name).first()
        artist.name = request.form.get('name')
        artist.city_id = city.id
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        list_genres = request.form.getlist('genres')
        artist.genres = ','.join(list_genres)
        artist.facebook_link = request.form.get('facebook_link')
        artist.image_link = request.form.get('image_link')
        artist.website = request.form.get('website_link')
        if request.form.get('venue_seeking') == 'y':
            artist.venue_seeking = True
            artist.seeking_description = request.form.get('seeking_description')
        else:
            artist.venue_seeking = False
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Artist: ' +
            request.form['name'] + ' could not be edited.')
        else:
             flash('Artist: ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------
# displays list of real shows data 
@app.route('/shows')
def shows():
    data = []
    shows = Show.query.all()
    for show in shows:
        artist = Artist.query.filter_by(id=show.artist_id).with_entities(Artist.name, Artist.image_link).first()
        venue = Venue.query.filter_by(id=show.venue_id).with_entities(Venue.name).first()
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.play_time
        }
        data.append(show_data)
    
    return  render_template('pages/shows.html', shows=data)


# renders form.
@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

# creating new shows in the db, upon submitting new show listing form
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show()
        show.artist_id = request.form.get('artist_id') 
        show.venue_id = request.form.get('venue_id') 
        show.play_time =  request.form.get('start_time')
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Show could not be listed.')
        else:
            flash('Show was successfully listed!')
    return render_template('pages/home.html')

# Search about shows for a given artist or venue id 
@app.route('/shows/search', methods=['POST'])
def search_shows():
    search_term_artist_id = request.form.get('search_term_artist', '')
    search_term_venue_id = request.form.get('search_term_venue', '')
    artist_list = []
    venue_list = []
    if search_term_artist_id.isnumeric():
        search_results = db.session.query(Show).join(Venue).join(Artist)\
        .filter(Show.artist_id == search_term_artist_id)\
        .with_entities(Venue.id.label('venue_id') , Venue.name.label('venue_name') , Artist.id.label('artist_id') , Artist.name.label('artist_name') , Artist.image_link.label('artist_image_link') , Show.play_time.label('play_time')).distinct()
        for res in search_results:
            print(res.play_time)
            artist_list.append({
                "venue_id": res.venue_id,
                "venue_name": res.venue_name,
                "artist_id": res.artist_id,
                "artist_name": res.artist_name,
                "artist_image_link": res.artist_image_link,
                "start_time": res.play_time
            })
        response = {
            "count": len(artist_list),
            "data": artist_list
        }
        return render_template('pages/search_shows.html', results=response, search_term=search_term_artist_id)

    elif search_term_venue_id.isnumeric():
        search_results = db.session.query(Show).join(Venue).join(Artist)\
        .filter(Show.artist_id == search_term_venue_id)\
        .with_entities(Venue.id.label('venue_id'), Venue.name.label('venue_name'), Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.play_time.label('play_time')).distinct()
        for res in search_results:
            print(res.play_time)
            venue_list.append({
                "venue_id": res.venue_id,
                "venue_name": res.venue_name,
                "artist_id": res.artist_id,
                "artist_name": res.artist_name,
                "artist_image_link": res.artist_image_link,
                "start_time": res.play_time
            })
        response = {
            "count": len(venue_list),
            "data": venue_list
        }
        return render_template('pages/search_shows.html', results=response, search_term=search_term_venue_id)

    else:
        flash('please enter a valid ID')
        return not_found_error(404)

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
