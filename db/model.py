from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
                                                     
engine = create_engine("sqlite:///db/main.db", echo=True)       # specify file path for db
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

Base = declarative_base()                       # 'Base' is how we declare a class to be managed by SQLA
Base.query = session.query_property()
    
def create_db():                                                 # actually create the db in the location relative to where I am
    """Create tables as needed."""
    Base.metadata.create_all(engine)

#================== users table  ==================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    email = Column(String(64), nullable = False)
    password = Column(String(64), nullable = False)

    def __repr__(self):
        """Cleanly info about the user."""
        return "<User id=%r email=%r password=%r>" % (self.id, 
            self.email, self.password)

#================== preferences table  ==================

class Preference(Base):
    """Represents the user's cuisine preferences """
    __tablename__ = "preferences"
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    cuisine = Column(String(64), nullable = False)

    def __repr__(self):
        """Cleanly info about the preference."""
        return "<Preference id=%d user_id=%d cuisine=%s>" % (self.id, 
            self.user_id, self.cuisine)

#================== restaurants table  ==================

class Restaurant(Base):
    """ Represents saved information for restaurants."""
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key = True)
    fsq_id = Column(String(64), nullable = False)       
    name = Column(String(64), nullable = False)
    lat = Column(Float, nullable = False)
    lng = Column(Float, nullable = False)
    cuisine = Column(String(60), nullable = False)

    def __repr__(self):
        """Show info about the restaurant."""
        return "<id=%r fsq_id=%r name=%r lat=%r lng=%r cuisine=%r>" % (self.id, 
            self.fsq_id, self.name, self.lat, self.lng, self.cuisine)                       

#================== bookmarks table  ==================

class Bookmark(Base):
    """ Represents each user's saved restaurants (bookmarks)."""
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key = True)        
    user_id = Column(Integer, ForeignKey('users.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))

    user = relationship("User", backref = backref('bookmarks', order_by = id))
    restaurant = relationship("Restaurant", backref = backref('bookmarks', order_by = id))

    def __repr__(self):
        """Show info about the bookmark."""
        return "<Bookmark id=%r user_id=%r restaurant_id=%r>" % (self.id, self.user_id, 
            self.restaurant_id) 

# def save_bookmark(this_user_id, this_restaurant_id):
#   """Saves a bookmark to the bookmark table."""
#   this_user_id = session.query(User).filter(id ==id).one()

#   new_bookmark = model.Bookmark(user_id=this_user_id,         
#       restaurant_id=this_restaurant_id)


"""Schema:

A user has many bookmarks through restaurants
A user has many preferences

A bookmark has many users through restaurants 

A restaurant has many users through bookmarks
A restaurant has many bookmarks through users 

A bookmark belongs to a user

"""
