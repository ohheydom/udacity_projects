import sys
sys.path.extend(['database/', 'helpers/'])

import httplib2
import json
import requests
import sqlalchemy.exc

from flask import (Flask, flash, render_template, jsonify,
                   request, redirect, url_for, session as login_session)
from database_helpers import create_session
from schema import City, Startup, User
from helpers import slugify, secret_key_generator
from template_helpers import datetimeformat, make_json_response
from oauth2client import client
from validation_helpers import check_errors

session = create_session('sqlite:///database/startup.db')

app = Flask(__name__)
app.jinja_env.filters['datetimeformat'] = datetimeformat


def logged_in():
    return login_session.get('username')


def create_user(login_session):
    new_user = User(username=login_session['username'],
                    email=login_session['email'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def get_user_by_id(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def get_user_id_by_email(email):
    user = session.query(User).filter_by(email=email).first()
    return user.id if user else None


@app.route('/')
@app.route('/city/')
@app.route('/index/')
def index():
    cities = session.query(City).order_by(City.name).all()
    latest_startups = session.query(Startup).order_by(Startup.created.desc()) \
            .limit(10)
    return render_template('index.html', cities=cities,
                           latest_startups=latest_startups,
                           logged_in=logged_in())


@app.route('/city/<string:city_slug>/')
def show_city(city_slug):
    city = session.query(City).filter_by(slug=city_slug).first()
    if not city:
        return render_template('404.html'), 404
    cities = session.query(City).order_by(City.name).all()
    startups = session.query(Startup).filter_by(city_id=city.id) \
            .order_by(Startup.name.asc()).all()
    return render_template('show-city.html', current_city=city, cities=cities,
                           logged_in=logged_in(), startups=startups)


@app.route('/city/<string:city_slug>/json/')
def show_city_json(city_slug):
    city = session.query(City).filter_by(slug=city_slug).first()
    if not city:
        return make_json_response('Invalid city.')
    return jsonify(city.serialize())


@app.route('/city/<string:city_slug>/<string:startup_slug>/')
def show_startup(city_slug, startup_slug):
    startup = session.query(Startup).filter_by(slug=startup_slug).first()
    current_user_id = None
    if 'user_id' in login_session:
        current_user_id = login_session['user_id']
    if not startup:
        return render_template('404.html'), 404
    return render_template('show-startup.html', startup=startup,
                           current_user_id=current_user_id,
                           logged_in=logged_in())


@app.route('/city/<string:city_slug>/<string:startup_slug>/json/')
def show_startup_json(city_slug, startup_slug):
    startup = session.query(Startup).filter_by(slug=startup_slug).first()
    if not startup:
        return make_json_response('Invalid startup.')
    return jsonify(startup.serialize())


@app.route('/city/<string:city_slug>/new/', methods=['POST', 'GET'])
def new_startup(city_slug):
    if 'username' not in login_session:
        flash('You must be logged in to post a startup.', 'error')
        return redirect('login')

    city = session.query(City).filter_by(slug=city_slug).first()
    if not city:
        return render_template('404.html', logged_in=logged_in()), 404

    if request.method == 'POST':
        name = request.form['startup-name']
        description = request.form['startup-description']
        link = request.form['startup-link']
        careers_link = request.form['startup-careers-link']
        errors = check_errors(name, description, link, careers_link)
        if errors:
            for k, error in errors.iteritems():
                flash(error, 'error')
            return render_template('new-startup.html', city=city,
                                   name=name, description=description,
                                   link=link, careers_link=careers_link,
                                   logged_in=logged_in())

        new_startup = Startup(name=name,
                              description=description,
                              link=link,
                              careers_link=careers_link,
                              city_id=city.id,
                              slug=slugify(name),
                              user_id=login_session['user_id'])
        try:
            session.add(new_startup)
            session.commit()
            flash('You have added a new startup to {}.'.format(city.name),
                  'success')
            return redirect(url_for('show_startup',
                                    city_slug=city_slug,
                                    startup_slug=new_startup.slug))
        except sqlalchemy.exc.IntegrityError, exc:
            flash('The startup already exists for the current city.', 'error')
            session.rollback()
            return render_template('new-startup.html', city=city,
                                   logged_in=logged_in())
    if request.method == 'GET':
        return render_template('new-startup.html', city=city,
                               logged_in=logged_in())


@app.route('/city/<string:city_slug>/<string:startup_slug>/edit/',
           methods=['POST', 'GET'])
def edit_startup(city_slug, startup_slug):
    if 'username' not in login_session:
        flash('You must be logged in to edit a startup.', 'error')
        return redirect('login')

    startup = session.query(Startup).filter_by(slug=startup_slug).first()
    if not startup:
        return render_template('404.html'), 404

    if startup.user_id != login_session['user_id']:
        flash('You cannot edit a startup you did not add.', 'error')
        return redirect('/')

    if request.method == 'POST':
        name = request.form['startup-name']
        description = request.form['startup-description']
        link = request.form['startup-link']
        careers_link = request.form['startup-careers-link']
        errors = check_errors(name, description, link, careers_link)
        if errors:
            for k, error in errors.iteritems():
                flash(error, 'error')
            return render_template('edit-startup.html', startup=startup,
                                   name=name, description=description,
                                   link=link, careers_link=careers_link,
                                   logged_in=logged_in())
        startup.name = name
        startup.description = description
        startup.link = link
        startup.careers_link = careers_link
        startup.slug = slugify(name)
        try:
            session.commit()
            flash('Startup has been modified.', 'success')
            return redirect(url_for('show_startup', city_slug=city_slug,
                                    startup_slug=startup.slug))
        except:
            flash('The startup already exists for the current city.', 'error')
            session.rollback()
            return render_template('edit-startup.html', startup=startup,
                                   name=name, description=description,
                                   link=link, careers_link=careers_link,
                                   logged_in=logged_in())

    if request.method == 'GET':
        name = startup.name
        description = startup.description
        link = startup.link
        careers_link = startup.careers_link
        return render_template('edit-startup.html', startup=startup,
                               name=name, description=description,
                               link=link, careers_link=careers_link,
                               logged_in=logged_in())


@app.route('/city/<string:city_slug>/<string:startup_slug>/delete/',
           methods=['POST'])
def delete_startup(city_slug, startup_slug):
    if 'username' not in login_session:
        flash('You must be logged in to delete a startup.', 'error')
        return redirect('login')

    startup = session.query(Startup).filter_by(slug=startup_slug).one()
    if login_session['user_id'] != startup.user_id:
        flash('You cannot delete a startup you did not add.', 'error')
        return redirect('/')

    session.delete(startup)
    session.commit()
    flash('Startup has been deleted.', 'success')
    return redirect(url_for('show_city', city_slug=city_slug))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', logged_in=logged_in()), 404


@app.route('/login/')
def login():
    if logged_in():
        return redirect('/index')
    state = secret_key_generator(32)
    login_session['state'] = state
    return render_template('login.html', state=state, logged_in=logged_in())


@app.route('/logout')
def logout():
    credentials = login_session.get('credentials')
    if credentials is None:
        return make_json_response('Current user is not connected.')
    credentials = client.OAuth2Credentials.from_json(credentials)
    credentials.revoke(httplib2.Http())

    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['state']

    flash('You have logged out.', 'success')
    return render_template('logout.html')


@app.route('/storeauthcode', methods=['POST'])
def store_auth_code():
    # Anti Forgery Check
    state = request.args.get('state')
    if state != login_session['state']:
        return make_json_response('Invalid state parameter.')

    auth_code = request.data
    try:
        client_secret = 'client_secret.json'
        credentials = client.credentials_from_clientsecrets_and_code(client_secret,
                ['https://www.googleapis.com/auth/userinfo.profile'], auth_code)
    except:
        return make_json_response('Failed to exchange authorization code.')

    http_auth = credentials.authorize(httplib2.Http())
    gplus_id = credentials.id_token['sub']

    # if user is already logged in
    if login_session.get('credentials'):
        return make_json_response('Current user is already connected.', 200)

    params = {'access_token': credentials.access_token, 'alt': 'json'}
    user_info = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                             params=params)
    json_data = user_info.json()

    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id
    login_session['username'] = json_data['name']
    login_session['email'] = json_data['email']

    user_id = get_user_id_by_email(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    return make_json_response('You are now logged in.', 200)


if __name__ == '__main__':
    app.secret_key = secret_key_generator(32)
    app.run(host='0.0.0.0', port=5000)
