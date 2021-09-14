#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys
from datetime import date, datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True, default="")
    image_link = db.Column(db.String(500), nullable=True, default="Please check out our website")
    facebook_link = db.Column(db.String(120), nullable=True, default="Please check out our website")
    website = db.Column(db.String(120), nullable=True, default="Coming Soon")
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable=True, default="")
    artists = db.relationship('Show')

    def __repr__(self):
      return f'< id: {self.id}, name: {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=True, default="Please check out our website")
    website = db.Column(db.String(120), nullable=True, default="Coming Soon")
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable=True, default="")
    venues = db.relationship('Show')
    
    def __repr__(self):
      return f'< id: {self.id}, name: {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False, onupdate='Cascade')
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False, onupdate='Cascade')
  show_time = db.Column(db.DateTime, nullable=False)
  artist = db.relationship('Artist', backref=db.backref('venue'))
  venues = db.relationship('Venue', backref=db.backref('artist'))

  def __repr__(self):
    return f'<id: {self.id}, venue_id: {self.venue_id}, artist_id {self.artist_id}, show_time: {self.show_time}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

def formatting_genres(genres):
  chars_to_remove = ['}','{']
  for chars in chars_to_remove:
    genres = genres.replace(chars, '')
  new_genres = genres.split(',')
  return new_genres

def phonecheck(phone_num):
  valid_num = ['0','1','2','3','4','5','6','7','8','9']
  if len(phone_num) == 10:
    for i in phone_num:
      if i in valid_num:
        print(i)
      else:
        return 'bad request', 400
  else:
    return 'bad request', 400
  return phone_num

def seekingtalent(x):
  if x == 'y':
    return True
  else: 
    return False
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
  newData = []
  query = Venue.query.with_entities(Venue.city, Venue.state).distinct()
  result =  query.all()
  for val, val2 in result:
    venue = {}
    venue['city'] = val 
    venue['state'] = val2
    venue['venues'] = []
    for value in Venue.query.all():
      if val == value.city:
        if val2 == value.state:
          v_ = {}
          v_['id'] = value.id
          v_['name'] = value.name 
          venue['venues'].append(v_)
    newData.append(venue) 
  print(newData)
  return render_template('pages/venues.html', areas=newData)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  var = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike('%'+ var + '%')).all()
  response = {}
  response['count'] = len(result)
  response['data'] = []
  for r in result:
    venues = {}
    venues['id'] = r.id
    venues['name'] = r.name 
    venues['num_upcoming_shows'] = db.session.query(Show).filter(Show.id == r.id, Show.show_time > datetime.utcnow()).count()
    response['data'].append(venues)
  db.session.close()

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venues = {}
  venue_query = Venue.query.filter(Venue.id == venue_id).all()
  for i in venue_query:
    venues['id'] = i.id  
    venues['names'] = i.name
    venues["genres"] = formatting_genres(i.genres)
    venues["address"] = i.address
    venues["city"] = i.city
    venues["state"] = i.state
    venues["phone"] = i.phone
    venues["website"] = i.website
    venues["facebook_link"] = i.facebook_link
    venues["seeking_talent"] = i.seeking_talent
    venues["seeking_description"] = i.seeking_description
    venues["image_link"] = i.image_link
    venues["past_shows_count"] = Show.query.filter(Show.venue_id == i.id, Show.show_time < datetime.utcnow()).count()
    venues["upcoming_shows_count"] = Show.query.filter(Show.venue_id == i.id, Show.show_time > datetime.utcnow()).count()
    past_shows = Show.query.with_entities(Show.artist_id, Artist.name, Artist.image_link, Show.show_time).join(Artist).filter(Show.venue_id == i.id, Show.show_time < datetime.utcnow()).all()
    upcoming_shows = Show.query.with_entities(Show.artist_id, Artist.name, Artist.image_link, Show.show_time).join(Artist).filter(Show.venue_id == i.id, Show.show_time > datetime.utcnow()).all()
    venues['past_shows'] = []
    venues['upcoming_shows'] = []
    for x in past_shows:
      dateobj = x.show_time
      datestring = dateobj.strftime('%m %d %Y %H:%M:%S')
      print(datestring)
      show = {
        'artist_name': x.name,
        'artist_id': x.artist_id,
        'artist_image_link': x.image_link,
        'show_time': datestring
      }
      venues['past_shows'].append(show)
    for v in upcoming_shows:
      dateobj = v.show_time
      datestring = dateobj.strftime('%m %d %Y %H:%M:%S')
      show = {
        'artist_name': v.name,
        'artist_id': v.artist_id,
        'artist_image_link': v.image_link,
        'show_time': datestring
      }
      venues['upcoming_shows'].append(show)

  data = venues
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = phonecheck(request.form.get('phone'))
  image = request.form.get('image_link')
  genres = request.form.getlist('genres')
  facebook = request.form.get('facebook_link')
  website = request.form.get('website')
  seeking_description = request.form.get('seeking_description')
  seeking_talent = request.form.get('seeking_talent')

  try:
    # TODO: modify data to be the data object returned from db insertion
    add_venue = Venue(
      name = name,
      city = city,
      state = state,
      address = address,
      phone = phone,
      image_link = image,
      genres = genres,
      facebook_link = facebook,
      website = website,
      seeking_talent = seekingtalent(seeking_talent),
      seeking_description = seeking_description
      )
    db.session.add(add_venue)
    db.session.commit()
    print(add_venue)
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
   abort(400)
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(Venue.id == venue_id).delete()
    value = Venue.query.filter_by(Venue.id == venue_id).first()
    print(value)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  query = Artist.query.with_entities(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=query)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  var = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike('%' + var + '%')).all()
  response = {}
  response['count'] = len(result)
  response['data'] = []
  for r in result:
    p = {}
    p['id'] = r.id 
    p['name'] = r.name
    p['num_upcoming_shows'] = db.session.query(Show).filter(Show.artist_id == r.id, Show.show_time > datetime.utcnow()).count()
    response['data'].append(p)
  
  data = response
  db.session.close()

  return render_template('pages/search_artists.html', results=data, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given artist_id
  # TODO: replace with real venue data from the venues table, using artist_id
  artists = {}
  artist_query = Artist.query.filter(Artist.id == artist_id).all()
  for i in artist_query:
    array = i.genres
    chars_to_remove = ['}', '{']
    for char in chars_to_remove:
      array = array.replace(char, '')
    new_genres = array.split(',')
    print(new_genres)
    artists['id'] = i.id
    artists['name'] = i.name
    artists['genres'] = new_genres
    artists['city'] =  i.city
    artists['state'] = i.state
    artists['phone'] = i.phone
    artists['website'] = i.website
    artists['facebook_link'] = i.facebook_link
    artists['seeking_venue'] = i.seeking_venue
    artists['seeking_description'] = i.seeking_description
    artists['image_link'] = i.image_link
    artists["past_shows_count"] = Show.query.filter(Show.artist_id == artist_id, Show.show_time < datetime.utcnow()).count()
    artists["upcoming_shows_count"] = Show.query.filter(Show.artist_id == artist_id, Show.show_time > datetime.utcnow()).count()
    artists['past_shows'] = []
    artists['upcoming_shows'] = []
    past_shows = Show.query.with_entities(Show.venue_id, Venue.name, Venue.image_link, Show.show_time).join(Venue).filter(Show.artist_id == artist_id, Show.show_time < datetime.utcnow()).all()
    upcoming_shows = Show.query.with_entities(Show.venue_id, Venue.name, Venue.image_link, Show.show_time).join(Venue).filter(Show.artist_id == artist_id, Show.show_time > datetime.utcnow()).all()
    for x in past_shows:
      dateobj = x.show_time
      datestring = dateobj.strftime('%m %d %Y %H:%M:%S')
      print(datestring)
      show = {
        'venue_id': x.venue_id,
        'venue_name': x.name,
        'venue_image_link': x.image_link,
        'show_time': datestring
      }
      artists['past_shows'].append(show)
    for v in upcoming_shows:
      dateobj = v.show_time
      datestring = dateobj.strftime('%m %d %Y %H:%M:%S')
      print(datestring)
      show = {
        'venue_id': v.venue_id,
        'venue_name': v.name,
        'venue_image_link': v.image_link,
        'show_time': datestring
      }
      artists['upcoming_shows'].append(show)
 
  return render_template('pages/show_artist.html', artist=artists)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm(
    name = artist.name,
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    image_link = artist.image_link,
    facebook_link = artist.facebook_link,
    website = artist.website,
    seeking_venue = artist.seeking_venue, 
    seeking_description = artist.seeking_description
  )
  form.genres.data = artist.genres
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = phonecheck(request.form.get('phone'))
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.seeking_venue = seekingtalent(request.form.get('seeking_venue'))
    artist.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + 'could not be updated!')
    abort(400)
  else:
    flash('Arist' + request.form['name'] + 'was successfully updated!')
  artist_mod = Artist.query.get(artist_id)
  return redirect(url_for('show_artist', artist_id=artist_mod.id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue= Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  print(venue.genres)
  form = VenueForm(name=venue.name,
                   city=venue.city,
                   state=venue.state,
                   address=venue.address,
                   phone=venue.phone,
                   image_link=venue.image_link,
                   facebook_link=venue.facebook_link,
                   website=venue.website,
                   seeking_talent=venue.seeking_talent,
                   seeking_description=venue.seeking_description)
  form.genres.data = venue.genres
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = phonecheck(request.form.get('phone'))
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.seeking_talent = seekingtalent(request.form.get('seeking_talent')) 
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except: 
    db.session.rollback()
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    abort(400)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  
  venue_mod = Venue.query.get(venue_id)
  return redirect(url_for('show_venue', venue_id=venue_mod.id))

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
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = phonecheck(request.form.get('phone')) 
  image_link = request.form.get('image_link', 'No image at the moment')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  website = request.form.get('website')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description = request.form.get('seeking_description')
  phonecheck(phone)
  error = False
  # TODO: modify data to be the data object returned from db insertion
  try:
    new_artist = Artist(
      name = name,
      city = city,
      state = state,
      phone = phone,
      image_link = image_link,
      genres = genres,
      facebook_link = facebook_link,
      website = website,
      seeking_venue = seekingtalent(seeking_venue),
      seeking_description = seeking_description
    )
    db.session.add(new_artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    abort(400)
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.with_entities(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.show_time).\
          join(Artist).filter(Show.artist_id == Artist.id, Show.venue_id ==Venue.id).all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  form.artist_id.choices =[(Artist.id, Artist.name) for artist in Artist.query.all()]
  form.venue_id.choices = [(Venue.id, Venue.name) for venue in Venue.query.all()]
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  obj = {}
  obj['venue_id'] =  request.form.get('venue_id')
  obj['artist_id'] = request.form.get('artist_id')
  obj['show_time'] =  request.form.get('start_time')
  arist_name = db.session.query(Artist.name).filter_by(id = obj['artist_id'])
  venue_name = db.session.query(Venue.name).filter_by(id = obj['venue_id'])
  obj['venue_name'] = venue_name
  obj['arist_name'] = arist_name
  error = False
  try:
    newShow = Show(
      artist_id = obj['artist_id'],
      venue_id = obj['venue_id'],
      show_time = obj['show_time'],
      artist = arist_name,
      venues = venue_name
    )
    db.session.add(newShow)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Show could not be listed.')
      abort(400)
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
