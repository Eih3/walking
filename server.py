"""Walk creator."""

import sqlalchemy
from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import Landmark, User, Rating, Walk, WalkLandmarkLink, connect_to_db, db
import os


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ["FLASK_SECRET_KEY"]


# Raise an error if you use an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/', methods=["GET"])
def create_new_walk():
    """Creates and maps new walk according to user input for origin, destination, 
    time constraint."""

    origin = request.args.get("origin")
    destination = request.args.get("destination")
    time = request.args.get("time)")

    return render_template('/', 
                            origin=origin, 
                            destination=destination, 
                            time=time)

# FIXME google maps api
#     return coordinates


# def display_map(coordinates):
#     api = Api(
#             consumer_key=os.environ['GOOGLE_API_KEY'])
# multiple waypoints result in multiple legs of the journey being created
# resulting from destination time and origin time calculations
# The maximum number of waypoints allowed when using the Directions service in 
# the Google Maps JavaScript API is 8, plus the origin and destination.

@app.route('/registration', methods=["GET"])
def display_registration_form():
    """Displays form for users to register an account."""

    return render_template('registration.html')


@app.route('/registration', methods=["POST"])
def process_registration_form():
    """Processes registration when user provides email and password."""

    email = request.form.get("email")
    password = request.form.get("password")

    # Create a possible user object to query if the user's email is in the users table.
    # If this user doesn't yet exist, query will return None.
    possible_user = User.query.filter_by(email=email).first()

    if possible_user:
        flash("An account has already been created for this email.")
        return redirect('/login')

    # Add user to user database
    else:
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        # add user_id to session variable, to login user automatically 
        session['user_id'] = user.user_id
        user_id = user.user_id
        flash("Your account has been created.")
        return redirect('/')

@app.route('/login', methods=["GET"])
def display_login_form():
    """Displays form fo
    r users to login"""

    return render_template('login.html')


@app.route('/login', methods=["POST"])
def process_login():
    """Process login from User, redirect to homepage"""

    email = request.form.get("email")
    password = request.form.get("password")
    
    # Create a possible user object to query if the user's email is in the users table.
    # If this user doesn't yet exist, query will return None.
    possible_user = User.query.filter_by(email=email).first()

    if possible_user and possible_user.password == password:

        # add user_id to session variable 
        session['user_id'] = possible_user.user_id
        flash("You are logged in!")
        user_id = possible_user.user_id

        return redirect('/')

    else:
        flash("Verify email and password entered is correct.")
        return redirect('/login')


@app.route('/logout')
def logout():
    """Removes user_id from the session"""

    session.pop('user_id', None)
    flash("Logged out.")

    return redirect('/')



@app.route('/profile')
def show_user():
    """Return page showing details:  walks, landmarks rated, scores."""

    user = User.query.filter_by(user_id=session.get('user_id')).first()

    ratings = user.ratings
    walks = user.walks
    
    return render_template('profile.html', 
                            user=user, 
                            ratings=ratings, 
                            walks=walks)



@app.route('/landmarks/<int:landmark_id>', methods=['GET'])
def show_landmark(landmark_id):
    """Show the details of a particular landmark."""

    # Querying landmarks table to get landmark object
    landmark = Landmark.query.get(landmark_id)
    user_id = session.get('user_id')

    if user_id:
        user_rating = Rating.query.filter_by(
                                            landmark_id=landmark_id, 
                                            user_id=user_id
                                            ).first()
    else:
        user_rating = None

    # Get the average rating of a landmark
    rating_scores = [r.user_score for r in Rating.user_score]
    avg_rating = float(sum(rating_scores))/len(rating_scores)


    # if (not user_rating) and user_id:
    #     user = User.query.get(user_id)
        #     if user:
        #         prediction = user.predict_rating(movie)
    ratings = landmark.ratings

    return render_template('landmark_details.html', 
                            landmark=landmark, 
                            ratings=ratings,
                            user_rating=user_rating,
                            average=avg_rating)
                          


@app.route('/rate_landmark', methods=["POST"])
def rate_landmark():

    score = request.form.get("score")
    landmark_id = request.form.get("landmark_id")
    user_id = session['user_id']


    # Create a possible_rating object to query if user_id AND landmark_id is in the ratings table
    possible_rating = Rating.query.filter(Rating.user_id == user_id, Rating.landmark_id == landmark_id).first()
    
    # If this score does not yet exist, we will add to the session database.
    # If this score already exists, we will update the value of the existing score.
    if possible_rating:
        possible_rating.score = score
        flash("Your rating has been updated.")
    else:
        # Instantiate new rating to add to the user database 
        new_rating = Rating(score=score, 
                            landmark_id=landmark_id, 
                            user_id=user_id)
        db.session.add(new_rating)
        flash("Rating saved.")

    db.session.commit()
    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()