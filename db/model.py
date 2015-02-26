from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
# import correlation
													 
engine = create_engine("sqlite:///main.db", echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

def create_db(): 
	"""Create tables, as needed."""
	Base.metadata.create_all()

#================== users table  ==================

class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key = True)
	email = Column(String(64), nullable = False)
	password = Column(String(64), nullable = False)

def __repr__(self):
    """Cleanly info about the user"""
    return "<User id=%d username=%s email=%s password=%s zipcode=%s>" % (self.id, 
    	self.username, self.email, self.password, self.zipcode)

#================== preferences table  ==================

class Preference(Base):
	"""Represents the user's cuisine preferences """
	__tablename__ = "preferences"
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('users.id'))
	cuisine = Column(String(64), nullable = False)

def __repr__(self):
    """Cleanly info about the preference"""
    return "<preference id=%d user_id=%d cuisine=%s>" % (self.id, 
    	self.user_id, self.cuisine)

#================== restaurants table  ==================

class Restaurant(Base):
	""" Represents saved information for restaurants """
	__tablename__ = "restaurants"
	id = Column(Integer, primary_key = True)
	fsq_id = Column(Integer, nullable = False)		
	name = Column(String(64), nullable = False)
	lat = Column(Float, nullable = False)
	lng = Column(Float, nullable = False)
	cuisine = Column(String(60), nullable = False)

def __repr__(self):
    """Show info about the restaurant."""
    return "<id=%d fsq_id=%d name=%s lat=%d lng=%d cuisine=%s>" % (self.id, 
    	self.fsq_id, self.name, self.lat, self.lng, self.cuisine)						

#================== bookmarks table  ==================

class Bookmark(object):
	""" Represents each user's saved restaurants (bookmarks)"""
	__tablename__ = "bookmarks"
	id = Column(Integer, primary_key = True)		
	user_id = Column(Integer, ForeignKey('users.id'))
	restaurant_id = Column(Integer, ForeignKey('restaurants.id'))

	user = relationship("User", backref	= backref('bookmarks'), order_by = id)
	restaurant = relationship("Restaurant", backref('bookmarks'), order_by = id)

def __repr__(self):
    """Show info about the bookmark."""
    return "<id=%d user_id=%d restaurant_id=%d>" % (self.id, self.user_id, 
    	self.restaurant_id)	

def main():
	pass

if __name__ == "__main__":
	# make_tables()
    main()


"""Schema:

A user has many bookmarks through restaurants
A user has many preferences

A bookmark has many users through restaurants 

A restaurant has many users through bookmarks
A restaurant has many bookmarks through users 

A bookmark belongs to a user

"""
