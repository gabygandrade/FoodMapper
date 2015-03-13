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
    """Represents each user."""
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    username = Column(String(15), nullable = False)
    email = Column(String(64), nullable = False)
    password = Column(String(64), nullable = False)

    def __repr__(self):
        """Cleanly info about the user."""
        return "<User id=%r username=%r email=%r password=%r>" % (self.id, 
            self.username, self.email, self.password)

#================== restaurants table  ==================

class Restaurant(Base):
    """Represents saved information for restaurants."""
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key = True)
    fsq_id = Column(String(64), nullable = False)       
    name = Column(String(64), nullable = False)
    lat = Column(Float, nullable = False)
    lng = Column(Float, nullable = False)
    cuisine = Column(String(64), nullable = False)
    address = Column(String(64), nullable = False)
    city = Column(String(64), nullable = False)
    state = Column(String(20), nullable = False)
    phone = Column(String(25))
    url = Column(String(120))
    icon_url = Column(String(200))

    def __repr__(self):
        """Show info about the restaurant."""
        return "<Restaurant id=%r fsq_id=%r name=%r lat=%r lng=%r cuisine=%r \
        address=%r city=%r state=%r phone=%r url=%r icon_url=%r>" % (self.id, 
            self.fsq_id, self.name, self.lat, self.lng, self.cuisine, 
            self.address, self.city, self.state, self.phone, self.url, self.icon_url)                       

#================== bookmarks table  ==================

class Bookmark(Base):
    """Represents each user's saved restaurants (bookmarks)."""
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key = True)        
    user_id = Column(Integer, ForeignKey('users.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))

    user = relationship("User", backref = backref('bookmarks', order_by = id))
    restaurant = relationship("Restaurant", backref = backref('bookmarks', order_by = id))

    bookmarkrec = relationship("BookmarkRecommendation", backref = backref('bookmarks', order_by = id))
   
    def __repr__(self):
        """Show info about the bookmark."""
        return "<Bookmark id=%r user_id=%r restaurant_id=%r>" % (self.id, self.user_id, 
            self.restaurant_id) 

#================== bookmark recommendations table  ==================

class BookmarkRecommendation(Base):
    """Represents the recommendations associated with a bookmark."""
    __tablename__ = "bookmarkrecs"
    id = Column(Integer, primary_key = True)   
    bookmark_id = Column(Integer, ForeignKey('bookmarks.id'))
    recommendation_id = Column(Integer, ForeignKey('recommendations.id'))

    bookmark = relationship("Bookmark", backref = backref('bookmarkrecs', order_by = id))
    recommendation = relationship("Recommendation", backref = backref('bookmarkrecs', order_by = id))

    def __repr__(self):
        """Show info about the bookmarkrecommendation."""
        return "<Bookmark id=%r bookmark_id=%r recommendation_id=%r>" % (self.id, self.bookmark_id, 
            self.recommendation_id) 

#================== recommendations table  ==================
class Recommendation(Base):
    """Represents each user's recommendations."""
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key = True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))  
    recommender_id = Column(Integer, ForeignKey('users.id'))
    recipient_id = Column(Integer, ForeignKey('users.id'))
    pending = Column(Boolean, nullable = False)

    recommender = relationship("User", foreign_keys=[recommender_id], backref=backref("recommendations_made"))
    recipient = relationship("User", foreign_keys=[recipient_id], backref=backref("recommendations_received"))

    restaurant = relationship("Restaurant", backref = backref('recommendations', order_by = id))

    def __repr__(self):
        """Show info about the recommendation."""
        return "<Recommendation id=%r restaurant_id=%r recommender_id=%r recipient_id=%r pending=%r>" % (self.id,
            self.restaurant_id, self.recommender_id, self.recipient_id, self.pending)

"""Schema:

A user has many bookmarks
A user has many recommendations

A restaurant can be bookmarked by a user
A restaurant can be recommended by a user

"""
