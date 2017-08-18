"""Paws Finder. Uses Flask, Jinja, AJAX and JSON"""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, Response, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Animal, Shelter, UserAnimal, UserSearch

import os, sys
import petfinder
from sqlalchemy import exc # this handles Integrity Errors
import json

from twilio.twiml.messaging_response import MessagingResponse

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
    dog_breeds = {"dogs": ["None", "Australian Cattledog", "Beagle", "Border Collie", 
                  "Boxer", "Bulldog", "Chihuahua", "Dachshund", "German Shepherd","Labrador Retriever", 
                  "Mixed Breed", "Pit Bull Terrier", "Staffordshire Terrier", "Yorkshire Terrier"]}
    cat_breeds = {"cats": ["None", "American Shorthair", "Calico", "Domestic Long Hair", 
                 "Domestic Medium Hair", "Domestic Short Hair", "Siamese", "Tabby", 
                 "Tabby-Brown", "Tabby-Gray","Tabby-Orange", "Tortoiseshell", "Tuxedo"]}           

    return render_template("home.html", 
                           animals=animals, ages=ages, 
                           sizes=sizes, genders=genders,
                           dog_breeds=dog_breeds,
                           cat_breeds=cat_breeds)


@app.route("/register", methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register-form2.html")


@app.route("/process-registration", methods=['POST']) 
def register_process():
    """Process registration."""

    # Get form variables from reg form
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")
    email = request.form.get("email") 
    password = request.form.get("password")    
    address1 = request.form.get("address1")    
    address2 = request.form.get("address2")      
    city = request.form.get("city")
    state = request.form.get("state")    
    zipcode = request.form.get("zipcode")    
    phone = request.form.get("phone")
    
    new_user = User(first_name=first_name, last_name=last_name,
                    email=email, password=password, 
                    address1=address1, address2=address2,
                    city=city, state=state,
                    zipcode=zipcode, phone=phone)
    
    # handles registration duplicate, flashes message
    try:     
        db.session.add(new_user)
        db.session.commit()
        flash("Welcome %s %s!  You are registered. \
              Your username is your email address, %s." 
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

    if not user:
        results = {"success": False,
        "message": "No user exists, please register."}
        return jsonify(results)  
           
    if user.password != password:
        results = {"success": False,
        "message": "Invalid username/password, try again."}
        return jsonify(results) 

    results = {"success": True,
              "firstname": user.first_name}     
    
    session["user_id"] = user.user_id
    
    
    return jsonify(results) 


@app.route("/logout.json")
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
        
   
    return render_template("shelters_search.html",
                            location=location,
                            shelters=shelter_list,
                            key=maps_api_key)


@app.route("/shelter-pets", methods=["GET"])
def show_shelter_pets():
    """Display pets in a shelter""" 

    # Get shelterID from googlemap infowindow
    shelter_id = request.args.get("id")

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
                            shelterpets=shelterpet_list)                             


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

@app.route("/alert-from-shelter", methods=["POST"])
def alert_from_shelter():
    """Get alerts from shelter when status of liked pet changes"""
    response = twiml.Response()
    # we get the SMS message from the request. we could also get the 
    # "To" and the "From" phone number as well
    inbound_message = request.form.get("Body")
    # we can now use the incoming message text in our Python application
    if inbound_message == "Hello":
        response.message("Hello back to you!")
    else:
        response.message("Hi! Not quite sure what you meant, but okay.")
    # we return back the mimetype because Twilio needs an XML response
    return Response(str(response), mimetype="application/xml"), 200



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(host="0.0.0.0")
