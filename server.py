"""Paws Finder. Uses Flask, Jinja, AJAX and JSON"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, Response, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Animal, Shelter, UserAnimal, UserSearch

import os, sys
import petfinder
from sqlalchemy import exc # this handles Integrity Errors
import json

# Twilio SMS API
from twilio import twiml #this is for route /receive-sms
#This is for the send-alert route
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse, Message

# Twilio API credentials
twilio_api_key = os.environ["TWILIO_API_KEY"]
twilio_api_secret = os.environ["TWILIO_API_SECRET"]

#Create TWILIO client object
client = Client(twilio_api_key, twilio_api_secret)

#add password hash using sha256_crypt
from passlib.hash import sha256_crypt

# Google Maps api key
maps_api_key = os.environ["GOOGLEMAPS_API_KEY"]

# Petfinder API credentials
api_key = os.environ["PETFINDER_API_KEY"]
api_secret = os.environ["PETFINDER_API_SECRET"]
# Instantiate petfinder api with my credentials
api = petfinder.PetFinderClient(api_key=api_key, 
                                api_secret=api_secret)
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Required to use Flask sessions and the debug toolbar
app.secret_key = "LGkjsdFlfkjaBldsmDasVfd36p9!9u0m43qlnXalrCd1f43aB"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
    """Homepage."""
    
    animals = ["dog", "cat"]
    ages = ["Baby", "Young", "Adult", "Senior"]
    sizes = {'S': 'small', 'M': 'medium', 'L': 'large', 'XL': 'xlarge'}
    genders = {"F": "female", "M": "male"}
    dog_breeds = {"dogs": ["None", "Australian Cattledog", "Australian Shepherd", 
                  "Basset Hound", "Beagle", "Border Collie", "Boston Terrier",
                  "Boxer", "Bulldog", "Catahoula Leopard Dog", "Cattle Dog", 
                  "Chihuahua", "Cocker Spaniel", "Dachshund", "Dalmatian", "English Bulldog",
                  "French Bulldog", "German Shepherd", "Great Dane", "Great Pyrenees", "Greyhound",
                  "Labrador Retriever", "Mixed Breed", 
                  "Pit Bull Terrier", "Pug", "Staffordshire Terrier", "Yorkshire Terrier"]}
    cat_breeds = {"cats": ["None", "American Shorthair", "Calico", "Domestic Long Hair", 
                 "Domestic Medium Hair", "Domestic Short Hair", "Siamese", "Tabby", 
                 "Tabby-Brown", "Tabby-Gray","Tabby-Orange", "Tortoiseshell", "Tuxedo"]}           

    return render_template("home.html", 
                           animals=animals, ages=ages, 
                           sizes=sizes, genders=genders,
                           dog_breeds=dog_breeds,
                           cat_breeds=cat_breeds)

#using a modal so don't need this route
# @app.route("/register", methods=['GET'])
# def register_form():
#     """Show form for user signup."""

#     return render_template("register-form2.html")


@app.route("/process-registration", methods=['POST']) 
def register_process():
    """Process registration."""

    # Get form variables from reg form
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    email = request.form.get("email") 
    password = request.form.get("password")    
    phone = request.form.get("phone")

    #hash the password and store this in DB
    password_hash = sha256_crypt.encrypt(password)
    
    new_user = User(first_name=first_name, last_name=last_name,
                    email=email, password=password_hash,
                    phone=phone)
    
    # handles registration duplicate, flashes message
    try:     
        db.session.add(new_user)
        db.session.commit()
        flash("Welcome %s %s! \
              Your username is %s." 
              % (first_name, last_name, email))
    except exc.IntegrityError:
        flash("User already exists. Please login")
        db.session().rollback()    
    
    return redirect("/")


@app.route("/login.json", methods=["POST"])
def perform_login():
    """Checks credentials, processes log in"""

    # Get credentials from form 
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()  

    #output of password_to_verify is True/False.  Check user input vs. database
    password_to_verify = sha256_crypt.verify(password, user.password)

    # print user.password
    # print password_to_verify

    if not user:
        results = {"success": False,
        "message": "No user exists, please register."}
        return jsonify(results)  
           
    if not password_to_verify: 
        results = {"success": False,
        "message": "Invalid username/password, try again."}
        return jsonify(results) 

    results = {"success": True,
              "firstname": user.first_name}     
    
    session["user_id"] = user.user_id
    
    
    return jsonify(results) 


@app.route("/logout.json", methods=['POST'])
def logout_json():
    """Log out."""

    del session["user_id"]
    results = {"success": True,
              "message": "Logged out."}
    
    return jsonify(results)


@app.route("/search", methods=["GET"])
def process_search():
    """Process form variables from quick search fields. No account needed."""
    
    genders = {"F": "female", "M": "male"}

    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 
    animal = request.args.get("animal")  
    gender = request.args.get("gender")

    # assign location to either zipcode or city, state
    if not zipcode:
        location = city + " " + state 
    elif not city or state:
        location = zipcode 

    # Call api and process search, note variables are singular.
    pets = api.pet_find(location=location,
                            animal=animal, 
                            gender=gender, 
                            output="basic", 
                            count=50)
        
    # import pdb; pdb.set_trace()

    pet_list = []
    # loop through a range from the api call
    # append to pet_list
    for i in range(20):
        pet = pets.next()
        pet_list.append(pet)        
   
    return render_template("results.html",
                            location=location,
                            animal=animal, 
                            genders=genders, #dictionary containing gender info 
                            gender=gender, # user form input
                            pets=pet_list)


@app.route("/search-complete", methods=["GET"])
def process_complete_search():
    """Process form variables from complete search fields. User is logged in."""
    
    sizes = {'S': 'small', 'M': 'medium', 'L': 'large', 'XL': 'extra large'}
    genders = {"F": "female", "M": "male"}

    # Get form variables
    zipcode = request.args.get("zipcode")
    city = request.args.get("city") 
    state = request.args.get("state") 
    animal = request.args.get("animal")  
    age = request.args.get("age")
    size = request.args.get("size")
    gender = request.args.get("gender")
    if animal == "dog":
        breed = request.args.get("dog-breeds")
    else:   
        breed = request.args.get("cat-breeds") 

    search_info = {"zipcode":zipcode,
                   "animal": animal,
                   "age": age,
                   "size": size,
                   "gender": gender,
                   "breed": breed}
                   
    session["last_search"] = search_info 

    # assign location to either zipcode or city, state
    if not zipcode:
        location = city + " " + state 
    elif not city or not state:
        location = zipcode                
    else:
        location = zipcode       

    liked = db.session.query(UserAnimal.animal_id).filter(UserAnimal.user_id == session['user_id']).subquery()
    liked_petid = db.session.query(Animal.pet_id).filter(Animal.animal_id.in_(liked)).all()
    liked_petid = [str(liked_pet[0]) for liked_pet in liked_petid]

    pets = api.pet_find(location=location,
                        animal=animal, 
                        age=age,
                        size=size,
                        gender=gender, 
                        breed=breed,
                        output="basic", 
                        count=50)

    # import pdb; pdb.set_trace()

    pet_list = []
    # loop through a range from the api call
    # append to pet_list
    for i in range(30):
        try:
            pet = pets.next()
            pet_list.append(pet)   
        except: 
            break    


    # print pet_list[2]

    return render_template("results_complete.html",
                            location=location,
                            animal=animal, 
                            age=age,
                            sizes=sizes, # dictionary that contain sizes data
                            size=size, # user form input
                            genders=genders, # dictionary that contain gender data 
                            gender=gender, # user form input
                            breed=breed,
                            pets=pet_list,
                            liked_petid=liked_petid,
                            search_info=search_info)    


@app.route("/save-search.json", methods=["POST"])
def save_search_results():
    """Save search criteria."""

    #get credentials from form
    title = request.form.get("title")
    description = request.form.get("description")

    current_search = UserSearch.query.filter(UserSearch.user_id == session["user_id"],
                                             UserSearch.zipcode == session['last_search']["zipcode"],
                                             UserSearch.animal == session['last_search']["animal"],
                                             UserSearch.age == session['last_search']["age"],
                                             UserSearch.size == session['last_search']["size"],
                                             UserSearch.gender == session['last_search']["gender"],
                                             UserSearch.breed == session['last_search']["breed"]).first()


    saved_search = UserSearch(user_id=session["user_id"],
                              zipcode=session['last_search']['zipcode'],  
                              animal=session['last_search']['animal'], 
                              age=session['last_search']['age'],  
                              size=session['last_search']['size'],  
                              gender=session['last_search']['gender'],
                              breed=session['last_search']['breed'],
                              title=title,
                              description=description)

    if current_search == saved_search:
        results = {"success": False,
                   "message": "You already saved this search."} 

    # so if current search == saved search then hide box
    # for 87 call back in savedpaws, inspect results, if results == success
    # then search already exists, hide box

    db.session.add(saved_search)
    db.session.commit() 

    results = {"success": True, 
               "message": "Your search is saved!"}

    return jsonify(results)  

@app.route("/get-saved-searches.json", methods=["GET"])
def get_saved_searches():
    """Retrieve saved searches from dB."""
    loggedin_user = session.get("user_id")#session is a dict, 
    #so .get() enables value of user_id to be returned

    if loggedin_user:
        searches = UserSearch.query.filter(UserSearch.user_id == loggedin_user).all()
    else:
        flash("Log in to see your saved searches!  Do it NOW!")  
        return redirect("/")     

    saved_searches = []

    for search in searches:
        # another way to do this, but longer
        # search_dict = {}
        # search_dict["title"] = search.title
        # search_dict["description"] = search.description
        # search_dict["usersearch_id"] = search.user_search_id
        saved_searches.append(search.to_dict())   
    
    results = {"results": saved_searches}

    return jsonify(results)  


@app.route("/shelters-search", methods=["GET"])
def process_search_shelters():
    """Display shelter search form""" 

    maps_api_key = os.environ["GOOGLEMAPS_API_KEY"]

    # Get form variables
    location = request.args.get("zipcode")

    # Call api and process search, note variables are singular.
    shelters = api.shelter_find(location=location,
                                count=50)

    shelter_list = []
    # loop through a range from the api call
    # append to shelter_list
    for i in range(30):
        shelter = shelters.next()
        shelter_list.append(shelter)  

    # print shelter_list[2]    
        
   
    return render_template("shelters_search.html",
                            location=location,
                            shelters=shelter_list,
                            key=maps_api_key)


@app.route("/shelter-pets", methods=["GET"])
def show_shelter_pets():
    """Display pets in a shelter""" 

    # Get shelterID from googlemap infowindow
    shelter_id = request.args.get("id")
    # print shelter_id

    # Get shelter name from googlemap infowindow
    # Display name in shelter_pets.html
    shelter_name = request.args.get("name")
    # print shelter_name

    # Call api and process search, note variables are singular.
    shelter_pets = api.shelter_getpets(id=shelter_id,
                                       output="full",
                                       count=30)

    shelterpet_list = []

    # loop through a range from the api call
    # append to list
    for i in range(10):
        shelter_pet = shelter_pets.next()
        shelterpet_list.append(shelter_pet)   
       
    return render_template("shelter_pets.html",
                            shelterpets=shelterpet_list,
                            shelter_name=shelter_name)                             


@app.route("/like-pets.json", methods=["POST"])
def like_pets():
    """Save liked pets from search results."""

    #get credentials from clicking the like button
    shelter_id = request.form.get("shelterId")
    animal = request.form.get("animal")
    name = request.form.get("name")    
    breed = request.form.get("breeds")
    age = request.form.get("age")
    gender = request.form.get("gender")
    pet_id = request.form.get("petID")
    size = request.form.get("size")
    description = request.form.get("description")
    last_update = request.form.get("lastupdate")
    
    liked_pet = Animal(shelter_id=shelter_id,
                       animal=animal,
                       name=name,
                       breed=breed,
                       age=age,
                       gender=gender,
                       pet_id=pet_id,
                       size=size,
                       description=description,
                       last_update=last_update)     


    db.session.add(liked_pet)
    db.session.commit() 
    
    # instantiate useranimal object so users can find liked animals through usersanimals table
    new_user_animal = UserAnimal(user_id=session.get("user_id"), animal=liked_pet)
    db.session.add(new_user_animal)
    db.session.commit() 

    results = {"success": True, 
               "message": "Liked!", "pet_id":pet_id}

    return jsonify(results)


@app.route("/get-liked-pets.json", methods=["GET"])
def get_liked_pets():
    """Retrieve liked pets from dB."""
    loggedin_user = session.get("user_id")#session is a dict, 
    #so .get() enables value of user_id to be returned

    if loggedin_user:
        user = User.query.filter(User.user_id == loggedin_user).first()
        saved_pets = user.liked_animals
    else:
        flash("Log in to see your saved paws!  Do it NOW!")  
        return redirect("/")     

    liked_pets = []

    for pet in saved_pets:
        # another way to do this, but longer
        # search_dict = {}
        # search_dict["title"] = search.title
        # search_dict["description"] = search.description
        # search_dict["usersearch_id"] = search.user_search_id
        liked_pets.append(pet.to_dict())   
    
    results = {"results": liked_pets}

    return jsonify(results) 


@app.route("/send-alert", methods=["GET"])
def send_alert():
    """Shelter sends SMS updates about saved pets"""

    # TO DO:  Insert user phone in the 'to' area

    #Create alert message
    message = client.messages.create(
         to = os.environ["MY_PHONE"],
         from_ = os.environ["TWILIO_PHONE"],
         body = "There are updates to your saved pets! \
         Type 'Yes' if interested.",
         media_url = ["http://bit.ly/2tlWPcH"])

    return Response("Shelter alert sent!"), 200


@app.route("/sms", methods=["POST"])
def respond_to_shelter_alert():
    """User response to alert from shelter"""

    # Based on users response, message is returned
    inbound_message = request.values.get("Body", None)

    # Respond to the user 
    if inbound_message == "Yes":
        message = "Contact us for an appointment."
    elif inbound_message == "No":
        message = "Have a great day!"
    else:    
        message = "Check PAWS Finder for updates."

    response = MessagingResponse()
    response.message(message)    

    return str(response)


@app.route("/receive-text", methods=["POST"])
def receive_sms():
    """User sends text message to shelter about interest in pet"""
    # Refer to: https://www.twilio.com/blog/2016/09/how-to-receive-and-respond-to-a-text-message-with-python-flask-and-twilio.html    

    # Get data from form
    number = request.form['From']
    message_body = request.form['Body']
    # Acknowledge reciept of sms
    response = MessagingResponse()
    response.message('Hello {}, thank you for your interest! We got your message, "{}". We will get back to you ASAP. ;-)'
                     .format(number, message_body))
    
    return str(response)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = False
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")
