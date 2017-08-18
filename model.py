"""Models and database functions for BFF Finder project."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc # added this to handle IntegrityError 

# This is the connection to the PostgreSQL database; we're getting
# this through the Flask-SQLAlchemy helper library. On this, we can
# find the `session` object, where we do most of our interactions
# (like committing, etc.)

db = SQLAlchemy()


#####################################################################
# Model definitions

class User(db.Model):
    """User of PAWS Finder website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True) # this is the username
    password = db.Column(db.String(30), nullable=False)
    address1 = db.Column(db.String(64), nullable=True)
    address2 = db.Column(db.String(64), nullable=True)        
    city = db.Column(db.String(15), nullable=True)
    state = db.Column(db.String(10), nullable=True)   
    zipcode = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(15), nullable=True)

    liked_animals = db.relationship("Animal", 
                                    secondary="usersanimals", 
                                    backref="users")

    def __repr__(self):
        """Provide helpful representation when printed."""

        s =  "<User first_name=%s last_name=%s user_id=%s email=%s>" 
        return s % (self.first_name, self.last_name, self.user_id, self.email)


class Animal(db.Model):
    """Animals on PAWS Finder website. Dogs and cats only."""

    __tablename__ = "animals"

    animal_id = db.Column(db.Integer,
                         autoincrement=True,
                         primary_key=True)
    shelter_id = db.Column(db.Integer, db.ForeignKey('shelters.shelter_id'), nullable=True)
    animal = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=True)    
    breed = db.Column(db.String(64), nullable=True)
    age = db.Column(db.String(64), nullable=True)
    gender = db.Column(db.String(64), nullable=True)
    pet_id = db.Column(db.Integer, nullable=True)
    size = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(2000), nullable=True)
    last_update = db.Column(db.DateTime, nullable=True)

    shelter = db.relationship("Shelter",
                              backref=db.backref("animals"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Animal animal_id=%s name=%s breed=%s age=%s gender=%s>" 
        return s % (self.animal_id, self.name, self.breed, self.age, self.gender)

    def to_dict(self):
        """Returns a dictionary representing the object"""

        
        # another way to do this but more complex               
        dict_of_obj = {}       
        # iterate through the table's columns, adding the value in each
        # to the dictionary
        for column_name in self.__mapper__.column_attrs.keys():
            value = getattr(self, column_name, None)
            dict_of_obj[column_name] = value


        #return the completed dictionary
        return dict_of_obj


class Shelter(db.Model):
    """Shelter info on PAWS Finder website."""

    __tablename__ = "shelters"

    shelter_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    address1 = db.Column(db.String(64), nullable=False)
    address2 = db.Column(db.String(64), nullable=True)        
    city = db.Column(db.String(15), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(10), nullable=False)    
    zipcode = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.String(64), nullable=True)
    longitude = db.Column(db.String(64), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Shelter name=%s email=%s city=%s state=%s shelter_id=%s>"
        return s % (self.name, self.email, self.city, self.state, self.shelter_id)

class UserAnimal(db.Model):
    """Association table that links users to animals"""

    __tablename__ = "usersanimals"

    user_animal_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    animal_id = db.Column(db.Integer, 
                          db.ForeignKey('animals.animal_id'),
                          nullable=False)
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.user_id'), 
                        nullable=False)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("usersanimals"))

    # Define relationship to animal
    animal = db.relationship("Animal",
                            backref=db.backref("usersanimals"))

    def __repr__(self):
        """Provide helpful representation when printed."""
        s = "<UserAnimal user_animal_id=%s animal_id=%s user_id=%s>"
        return s %(self.user_animal_id, self.animal_id, self.user_id)

class UserSearch(db.Model):
    """Association table that enables users to capture and refresh their searches."""

    __tablename__ = "usersearch"

    user_search_id = db.Column(db.Integer,
                          autoincrement=True,
                          primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    zipcode = db.Column(db.String(10), nullable=True)    
    animal = db.Column(db.String(64), nullable=False) 
    age = db.Column(db.String(64), nullable=True)
    size = db.Column(db.String(64), nullable=True)
    gender = db.Column(db.String(64), nullable=True)
    breed = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)


    
    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("usersearch"))


    def __repr__(self):
        """Provide helpful representation when printed."""
        s = "<UserSearch user_search_id=%s user_id=%s animal=%s age=%s size=%s gender=%s>"
        return s %(self.user_search_id, self.user_id, self.animal, self.age, 
                   self.size, self.gender)        
    

    def to_dict(self):
        """Returns a dictionary representing the object"""

        dict_of_obj = {'user_id': self.user_id, 
                       'zipcode': self.zipcode,
                       'animal': self.animal,
                       'age': self.age,
                       'size': self.size,
                       'gender': self.gender,
                       'breed': self.breed,
                       'title': self.title,
                       'description': self.description}

        # another way to do this but more complex               
        # dict_of_obj = {}       
        #iterate through the table's columns, adding the value in each
        #to the dictionary
        # for column_name in self.__mapper__.column_attrs.keys():
        #     value = getattr(self, column_name, None)
        #     dict_of_obj[column_name] = value


        #return the completed dictionary
        return dict_of_obj

# Testing DB section
def connect_to_db(app, db_uri="postgresql:///pawsfinder"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.app = app
    db.init_app(app)


def example_data():
    """Create example data for the test database."""

    user1 = User(first_name="Generosa", last_name="Litton",email="glitton@gmail.com", password="uRGr34t")
    user2 = User(first_name="Django", last_name="Litton",email="django@gmail.com", password="theBee!",
                address1="136 North Drive", city="San Francisco", state="CA", zipcode="94132")


    db.session.add_all([user1, user2])
    db.session.commit()        
        
#####################################################################
# Helper functions #used before I did the testing

# def connect_to_db(app):
#     """Connect the database to our Flask app."""

#     # Configure to use our PostgreSQL database
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///furfinder'
#     db.app = app
#     db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will
    # leave you in a state of being able to work with the database
    # directly.

    from server import app
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    connect_to_db(app)
    print "Connected to DB."
    db.create_all()
