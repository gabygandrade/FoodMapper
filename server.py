from flask import Flask, render_template, redirect, request, g, url_for, flash, make_response, jsonify
from flask import session
from db import model
import jinja2
import os
import fsqapi
import config

app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
app.jinja_env.undefined = jinja2.StrictUndefined 

fsq_client_id = config.FSQ_CLIENT_ID 			
fsq_client_secret = config.FSQ_CLIENT_SECRET

@app.route("/login")
def display_login():
	"""Render the login page"""
	return render_template("login.html")

@app.route("/login", methods=['POST'])
def login_user():
	"""Makes POST request to get user input, and user is added to the Flask session """
	
	email = request.form['email']
	password = request.form['password']

	all_users = model.session.query(model.User)
	try:
		user = all_users.filter(model.User.email==email, model.User.password==password).one()
		session['user_email'] = user.email
		session['user_id'] = user.id
		session['logged_in'] = True
		flash ("You are logged in")
		# print session
		# print user.email
		# print user.id
		return redirect("/") 
	except:
		flash("That email or password is incorrect. Please try again")
		print session
		return render_template("login.html")

@app.route("/logout")
def logout():
	"""Logs user out and clears session"""
	session.clear()
	print session 
	flash ("You have been logged out")
	return redirect("/login") 

@app.route("/")
def index():
	"""Render the page where users can search for a restaurant """
	return render_template("index.html")

@app.route("/restaurant-results")
def show_rest_info():
	"""When the user submits their search, gather the user input 
	to create the query request to the Foursquare (FSQ) API. 
	Return the response as a python dictionary and pass it to the 
	template"""
	
	# pull out parameters from request
	search_restaurant = request.args.get('search-restaurant')
	search_location = request.args.get('search-location')
	print (search_restaurant, search_location)
	# create a python dict from the Foursquare API JSON response 
	
	try:
		fsq_dict = fsqapi.search_venues(fsq_client_id, fsq_client_secret, search_restaurant, search_location) 	# Look in foursquareapi module and create fsq dict function with the parameters here
		# parse that python dict to get just the part of the request w/needed venues info
		fsq_venues_list = fsq_dict['response']['venues']
		print "FSQ Venues List: ", fsq_venues_list

		# if FSQ query returned no search results
		if fsq_venues_list == []:								
			flash("Your search came up empty. Please try another search.") 
		
		return render_template("restaurant_results.html", fsq_venues=fsq_venues_list)

	except:
		# if the user entered a location FSQ cannot geocode				
		fsq_venues_list = []

		flash("Please enter a city name.") 
		return redirect('/')

@app.route("/save-db")	
def save_to_db():		
	"""Saves the restaurant and the bookmark as new records in the db"""
	
	USER_ID = 1

	# pulls the needed fields from the request object
	name = request.args["name"]
	fsq_id = request.args["fsqId"]
	lat = request.args["lat"]
	lng = request.args["lng"]
	cuisine = request.args["cuisine"]
	url = request.args["url"]
	phone = request.args["phone"]

	# print "request object: ", request.args
	# print "Name: ", name
	# print "FSQ ID: ", fsq_id
	# print "Lat: ", lat 
	# print "Lng: ", lng 
	# print "Cuisine: ", cuisine 

	saved_restaurant = model.session.query(model.Restaurant).filter(model.Restaurant.fsq_id==fsq_id).first()
	saved_bookmark = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==USER_ID, 			
		model.Bookmark.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()

	#If the restaurant DOESN'T exist in the db (& thus implicitly the bookmark doesn't exist)
	if not saved_restaurant: 
		# save a new restaurant to the restaurants table
		new_restaurant = model.Restaurant(fsq_id=fsq_id, name=name, 
						lat=lat, lng=lng, cuisine=cuisine, url=url, phone=phone)
		model.session.add(new_restaurant)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_restaurant
		model.session.refresh(new_restaurant) 

		# save a new bookmark to the bookmarks table
		new_bookmark = model.Bookmark(user_id=USER_ID, restaurant_id=new_restaurant.id)		# change this hardcoding later to user who is logged in
		model.session.add(new_bookmark)
		model.session.commit()

		return jsonify({"message": "You added %s to your bookmarks!" % new_restaurant.name}) 

	# the bookmark ALREADY exists for the user (& thus the restaurant also already exists) - ie. the restaurant id is already associated with that user 
	elif saved_bookmark:
		return jsonify({"message": "You already bookmarked this restaurant!"}) 

	# elif the restaurant DOES exist BUT the bookmark doesn't exist for this user - ie. the restaurant id is not associated with a bookmark for this user
	elif saved_restaurant and not saved_bookmark:
		new_bookmark = model.Bookmark(user_id=USER_ID, restaurant_id=saved_restaurant.id)		# FIXME: change this hardcoding later to user who is logged in
		model.session.add(new_bookmark)
		model.session.commit()
		return jsonify({"message": "You added %s to your bookmarks!" % saved_restaurant.name})	

@app.route("/map")
def show_map():
	"""Render map"""
	return render_template("map.html")	

@app.route("/map-bookmarks")
def map_bookmarks():
	"""Map the user's bookmarks"""

	USER_ID = 1

	# get restaurant info for all the user's bookmarked restaurants
	data = model.session.query(model.Bookmark.id, model.Restaurant.fsq_id, 
		model.Restaurant.name, model.Restaurant.lat, model.Restaurant.lng, model.Restaurant.cuisine).join(model.Restaurant).filter(model.Bookmark.user_id==USER_ID).all()

	# create a dictionary with all the info necessary to pass on to jinja in order to map markers 
	restaurant_info = {}
	for item in data:
		restaurant_info[item.id] = {}
		restaurant_info[item.id]["fsq_id"] = item.fsq_id
		restaurant_info[item.id]["name"] = item.name
		restaurant_info[item.id]["lat"] = item.lat
		restaurant_info[item.id]["lng"] = item.lng
		restaurant_info[item.id]["cuisine"] = item.cuisine

	# print "restaurant_info: ", restaurant_info

	return jsonify(restaurant_info)

@app.route("/mylist")
def display_bookmarks_list():
	"""Dispaly the user's bookmarks as a list"""


# @app.route("/delete-bookmark")
# def delete_bookmark(): 
# 	"""Delete the user's selected bookmark """
# 	USER_ID = 1

# 	# get the restaurant id for the restaurant that the user wants to delete
# 	restaurant_id = request.args['restaurantId']

# 	#---TRY THESE IN INTERACTIVE PYTHON CONSOLE FIRST ---#
# 	# query for the bookmark with that user id & restaurant id 
# 	bookmark_to_delete = session.query(Bookmark).filter(Bookmark.user_id==USER_ID, Bookmark.restaurant_id==restaurant_id).first()

# 	# delete the restaurant from the db 
# 	session.delete(rest_to_bookmark)
# 	session.commit()



if __name__ == "__main__":
    app.run(debug = True)






