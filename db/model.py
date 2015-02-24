from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
# import correlation

SQLITEDB = os.environ.get('SQLITEDB')					# TODO: clarify what this means. Does it mean I'm adding my database file as an environment variabel? 
														# DO I need a connect function? 
engine = create_engine("SQLITEDB", echo=True)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

#================== user tables  ==================

class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key = True)
	email = Column(String(64), nullable = False)
	password = Column(String(64), nullable = False)

    def __repr__(self):
        """Cleanly info about user """
        return "<User id=%d username=%s email=%s password=%s zipcode=%s>" % 
        (self.id, self.username, self.email, self.password, self.zipcode)

#================== preferences table  ==================

class Preferences(Base)
	"""Represents the user's cuisine preferences """
	__tablename__ = "preferences"
	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('users.id'))
	cuisine = Column(String(64), nullable = False)

	# will have a different entry for each cuisine

#================== restaurants table  ==================

class Restaurant(Base):
	""" Represents saved information for restaurants """
	__tablename__ = "restaurants"
	id = Column(Integer, primary_key = True)
	fsq_id = Column(Integer, nullable = False)		# foursquare id
	name = Column(String(64), nullable = False)
	lat = Column(Float, nullable = False)
	lng = Column(Float, nullable = False)
	cuisine = Column(String(60), nullable = False)

	 def __repr__(self):
        """Show info about restaurant."""
        return "<Cat id=%d fsq_id=%d name=%s lat=%d lng=%d cuisine=%s>" % 
        (self.id, self.fsq_id, self.name, self.lat, self.lng, self.cuisine)

	# TODO: the name, lat, long, and cuisine have to come from the fs API 
	# def save_restaurant(name, lat, lng, cuisine):			# The parameters I put are the ones I need to get from the foursquare API
	# sr = Restaurant(fs_id= )								# Here I need to pass in the FS id from the API call 

#================== bookmarks table  ==================

class Bookmark(object):
	""" Represents each user's saved restaurants (bookmarks)"""
	__tablename__ = "bookmarks"
	id = Column(Integer, primary_key = True)		
	user_id = Column(Integer, ForeignKey('users.id'))
	restaurant_id = Column(Integer, ForeignKey('restaurants.id'))

	user = relationship("User", backref	= backref('bookmarks'), order_by = id)

	restaurant = relationship("Restaurant", backref('bookmarks'), order_by = id)

	# def save_bookmark(): 			# what should this function take in? user and restaurant? 
	# """Saves a bookmark to a user account. Takes in the bookmark, queries by user id and writes 
	# to the bookmarks table"""
	# TODO:
	# user_id = session.query(User).filter_by(User.id = id).one()			# Query for the user id?
	# sb =  Bookmark(user_id=???, restaurant_id=???, fs_restaurant_id=???)					# create a new instance of the Bookmark class with specific attributes
	# session.add(sb)					# add the saved bookmark - DONE
	# session.commit()					# commit it to the db  - DONE 

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
