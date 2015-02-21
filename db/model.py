from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
# import correlation

engine = create_engine("sqlite:///ratings.db", echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key = True)
	email = Column(String(64), nullable = False)
	password = Column(String(64), nullable = False)

    # def __repr__(self):
    #     """Cleanly show info about self """
    #     return "<User id=%d username=%s email=%s password=%s zipcode=%s>" % (self.id, self.username, self.email, self.password, self.zipcode)

class UserPreferences(Base)
	"""Represents the user's cuisine preferences """
	__tablename__ = "userpreferences"
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('users.id'))
	preference1 = Column(String(64), nullable = False)
	preference2 = Column(String(64), nullable = False)
	preference3 = Column(String(64)) # Default to nullable = True
	preference4 = Column(String(64))

class Restaurant(Base):
	""" Represents saved information for restaurants """
	__tablename__ = "restaurants"
	id = Column(Integer, primary_key = True)
	fs_id = Column(Integer, nullable = False)
	name = Column(String(64), nullable = False)
	lat = Column(Float, nullable = False)
	lng = Column(Float, nullable = False)
	cuisine = Column(String(60), nullable = False)

class Bookmarks(object):
	""" Represents each user's saved restaurants (bookmarks) """
	__tablename__ = "userrests" 
	# id = Column(Integer, primary_key = True)		# id for the specific user restaurant
	user_id = Column(Integer, ForeignKey('users.id'))
	restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
	fs_restaurant_id = Column(Integer, ForeignKey('restaurants.fs_id'))

	def add_bookmark(): 
		#function to add bookmark

def main():
	pass

if __name__ == "__main__":
    main()



"""Schema Notes:

A user has many restaurants
A user has many bookmarks

A restaurant has many users
A restaurant has many bookmarks

A bookmark belongs to a user

"""

