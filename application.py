# !/usr/bin/env python

from db_setup import Base, Company, CarType, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc
from flask import request, url_for, flash, jsonify
from flask import Flask, render_template, redirect
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Cars Companies Application"

app = Flask(__name__)


# engine = create_engine('sqlite:///carscompanies.db?check_same_thread=False')
engine = create_engine(
    'sqlite:///carscompanieswithusers.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery
# Store it in the session for later validation


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 404)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data

    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Faild to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error'), 50))
        response.headers['Content-Type'] = 'application/json'
    # Verity that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("token's client ID doesn't match app's."), 401)
        print "Token's client ID doesn't match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in.
    Stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if Stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check if the user exists, if it doesn't make a new user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1> Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''"
     style= "width: 300px; height: 300px; border-radius: 150px
    ; -webkit-border-radius:150px; -moz-border-radius: 150px;">
    '''
    flash("you are now logged in as %s" % login_session['username'])
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    companies = session.query(Company)
    latestCars = session.query(CarType).order_by(CarType.id.desc()).limit(10)
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash('Current user not connected.', 'success')
        return render_template(
            'index.html',
            companies=companies,
            latestCars=latestCars)
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/'
    url += 'oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected', 'success')
        return render_template(
            'index.html',
            companies=companies,
            latestCars=latestCars)
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        flash('Failed to revoke token for given user.', 'success')
        return render_template(
            'index.html',
            companies=companies,
            latestCars=latestCars)

# Create New user


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Get user object


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# The main page that shows a list of companies.


@app.route('/')
def MainPage():
    loggedin = False
    if 'username' in login_session:
        loggedin = True
    companies = session.query(Company).all()
    latestCars = session.query(CarType).order_by(CarType.id.desc()).limit(10)
    return render_template(
        'index.html',
        companies=companies,
        latestCars=latestCars,
        loggedin=loggedin)

# Making an API Endpoint (GET Request) for a specific company's cars


@app.route('/<int:company_id>/cars/JSON/')
def CompanyCarsJSON(company_id):
    company = session.query(Company).filter_by(id=company_id).one()
    cars = session.query(CarType).filter_by(company_id=company_id).all()
    return jsonify(CarType=[car.serialize for car in cars])

# Shows a list of cars for a spcific company


@app.route('/<int:company_id>/cars/')
def CompanyCars(company_id):
    loggedin = False
    if 'username' in login_session:
        loggedin = True
    company = session.query(Company).filter_by(id=company_id).one()
    creator = {'info': getUserInfo(company.user_id)}
    creator['check'] = True
    if ('username' not in login_session or
            creator['info'].id != login_session['user_id']):
        creator['check'] = False

    cars = session.query(CarType).filter_by(company_id=company_id).all()
    return render_template(
        'companyCars.html',
        company=company,
        cars=cars,
        creator=creator,
        loggedin=loggedin)

# Shows car details for a spcific company


@app.route('/<int:company_id>/cars/<int:car_id>')
def CompanyCarsDetails(company_id, car_id):
    loggedin = False
    if 'username' in login_session:
        loggedin = True
    carDetails = session.query(CarType).filter_by(id=car_id).one()
    company = session.query(Company).filter_by(id=company_id).one()
    creator = {'info': getUserInfo(carDetails.user_id)}
    creator['check'] = True
    if ('username' not in login_session or
            creator['info'].id != login_session['user_id']):
        creator['check'] = False

    cars = session.query(CarType).filter_by(company_id=company_id).all()
    return render_template(
        'companyCarsDetails.html',
        company=company,
        cars=cars,
        creator=creator,
        carDetails=carDetails,
        loggedin=loggedin)

# Create new company


@app.route('/newCompany', methods=['GET', 'POST'])
def createCompany():
    loggedin = True
    if 'username' not in login_session:
        loggedin = False
        return redirect('/login')

    if request.method == 'POST':
        newCompany = Company(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(newCompany)
        session.commit()
        message = "a new company calld '" + \
            request.form['name'] + "' has been created!"
        flash(message)
        return redirect('/')
    else:
        return render_template('newCompany.html', loggedin=loggedin)

# Making an API Endpoint (GET Request) for a specific car


@app.route('/<int:company_id>/cars/<int:car_id>/JSON/')
def CarsDetailsJSON(company_id, car_id):
    car = session.query(CarType).filter_by(
        id=car_id).filter_by(
        company_id=company_id).one()
    return jsonify(CarType=car.serialize)

# Add new car for a specific company


@app.route('/<int:company_id>/newCar/', methods=['GET', 'POST'])
def newCar(company_id):
    loggedin = True
    if 'username' not in login_session:
        loggedin = False
        return redirect('/login')
    company = session.query(Company).filter_by(id=company_id).one()
    if request.method == 'POST':
        newCar = CarType(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            company_id=company_id,
            user_id=login_session['user_id'])
        session.add(newCar)
        session.commit()
        message = "a new car calld '" + \
            request.form['name'] + "' has been created!"
        flash(message, 'success')
        return redirect(url_for('CompanyCars', company_id=company_id))
    else:
        return render_template(
            'newCar.html',
            company_id=company_id,
            loggedin=loggedin)


# Edit cars
@app.route('/<int:company_id>/<int:car_id>/edit/',
           methods=['GET', 'POST'])
def editCar(company_id, car_id):
    loggedin = True
    if 'username' not in login_session:
        loggedin = False
        return redirect('/login')
    car = session.query(CarType).filter_by(id=car_id).one()
    if login_session['user_id'] != car.user_id:
        message = '''
        Sorry, you are not allowed to edit this car since
         you are not the one who created it!
         Thanks for understanding.
        '''
        flash(message, 'danger')
        return redirect(url_for('CompanyCars', company_id=company_id))

    car = session.query(CarType).filter_by(id=car_id).one()
    if request.method == 'POST':
        message = "'" + car.name
        car.name = request.form['name']
        car.description = request.form['description']
        car.price = request.form['price']
        session.add(car)
        session.commit()
        message += "' has been changed to '" + request.form['name'] + "'"
        flash(message, 'success')
        return redirect(url_for('CompanyCars', company_id=company_id))
    else:
        return render_template(
            'editCar.html', car=car, loggedin=loggedin)

# Delete Car


@app.route('/<int:company_id>/<int:car_id>/delete/', methods=['GET', 'POST'])
def deleteCar(company_id, car_id):
    loggedin = True
    if 'username' not in login_session:
        loggedin = False
        return redirect('/login')
    car = session.query(CarType).filter_by(id=car_id).one()
    if login_session['user_id'] != car.user_id:
        message = '''
        Sorry, you are not allowed to delete this car since
         you are not the one who created it!
         Thanks for understanding.
        '''
        flash(message, 'danger')
        return redirect(url_for('CompanyCars', company_id=company_id))

    car = session.query(CarType).filter_by(id=car_id).one()
    if request.method == 'POST':
        message = "'" + car.name + "' has been deleted!"
        session.delete(car)
        session.commit()
        flash(message, 'danger')
        return redirect(url_for('CompanyCars', company_id=company_id))
    else:
        return render_template(
            'deleteCar.html', car=car, loggedin=loggedin)


if __name__ == '__main__':
    app.secret_key = '5ecret_k3y'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
