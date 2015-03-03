from flask import Flask, render_template, redirect, request, g, url_for, flash, make_response, jsonify
from flask import session as fsess
from db import model
import jinja2
import os
import foursquareapi
import config

app = Flask(__name__)
app.secret_key = config.APP_SECRET_KEY
app.jinja_env.undefined = jinja2.StrictUndefined 

fs_client_id = config.FS_CLIENT_ID 			
fs_client_secret = config.FS_CLIENT_SECRET

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
		fs_dict = foursquareapi.search_FSQ_venues(fs_client_id, fs_client_secret, search_restaurant, search_location) 	# Look in foursquareapi module and run the create_fs_dict function with the parameters here
		# parse that python dict to get just the part of the request w/needed venues info
		fs_venues_list = fs_dict['response']['venues']
		# print "FS Venues List: ", fs_venues_list

		# if FSQ query returned no search results
  
		if fs_venues_list == []:								
			flash("Your search came up empty. Please try another search.") 
		
		return render_template("restaurant_results.html", 
		fs_venues_list=fs_venues_list)

	except:
		# if the user entered a location FSQ cannot geocode				
		fs_venues_list = []
		flash("Please enter a city name.") 
		return redirect('/')

@app.route("/save-db")		# FIXME: change name of this route to save_to_db()
def save_to_db():		
	"""Saves the restaurant and the bookmark as new records in the db"""
	
	USER_ID = 1

	# pulls the needed fields from the request object
	name = request.args["name"]
	fsq_id = request.args["fsqId"]
	lat = request.args["lat"]
	lng = request.args["lng"]
	cuisine = request.args["cuisine"]

	# print "Request.args object: ", request.args
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
						lat=lat, lng=lng, cuisine=cuisine)
		model.session.add(new_restaurant)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_restaurant
		model.session.refresh(new_restaurant) 

		# save a new bookmark to the bookmarks table
		new_bookmark = model.Bookmark(user_id=USER_ID, restaurant_id=new_restaurant.id)		# change this hardcoding later to user who is logged in
		model.session.add(new_bookmark)
		model.session.commit()

		return jsonify({'message': 'You added %s to your bookmarks!' % new_restaurant.name}) 

	# the bookmark ALSO ALREADY exists for the user (& thus the restaurant also already exists) - ie. the restaurant id is already associated with that user 
	elif saved_bookmark:
		return jsonify({'message': 'You already bookmarked this restaurant!'}) 

	# elif the restaurant DOES exist BUT the bookmark doesn't exist for this user - ie. the restaurant id is not associated with a bookmark for this user
	elif saved_restaurant and not saved_bookmark:
		new_bookmark = model.Bookmark(user_id=USER_ID, restaurant_id=saved_restaurant.id)		# change this hardcoding later to user who is logged in
		model.session.add(new_bookmark)
		model.session.commit()
		return jsonify({'message': 'You added %s to your bookmarks!' % saved_restaurant.name})	

@app.route("/map")
def show_map():
	"""Show map with the user's bookmarks"""

	USER_ID = 1

	# get restaurant info for all the user's bookmarked restaurants
	restaurant_data = model.session.query(model.Bookmark.id, model.Restaurant.fsq_id, model.Restaurant.name, 
		model.Restaurant.lat, model.Restaurant.lng, model.Restaurant.cuisine).join(model.Restaurant).filter(model.Bookmark.user_id==USER_ID).all()

	# create a dictionary with all the info necessary to pass on to jinja in order to map markers 
	restaurant_dict = {}
	for item in restaurant_data:
		restaurant_dict[item.id] = {}
		restaurant_dict[item.id]["fsq_id"] = item.fsq_id
		restaurant_dict[item.id]["name"] = item.name
		restaurant_dict[item.id]["lat"] = item.lat
		restaurant_dict[item.id]["lng"] = item.lng
		restaurant_dict[item.id]["cuisine"] = item.cuisine

	print "restaurant_dict", restaurant_dict 
	return render_template("map.html", restaurant_dict = jsonify(restaurant_dict))	

if __name__ == "__main__":
    app.run(debug = True)














# Work on login after map

# @app.route("/login")
# def display_login():
# 	# Displays login page
# 	return render_template("login.html")

# @app.route("/login", methods=['POST'])
# def login_user():
# 	# Makes POST request to get user input to log into account
# 	print "login function running"
# 	email = request.form['email']
# 	password = request.form['password']
# 	print (email, password)
# 	# login = model.login(email, password)	# need to create login function in model to tie this back to 
# 	return redirect("/login") 

# def save_object(obj_instance):
# 	try:
# 		session.add(obj_instance)
# 		session.commit()
# 		return 200
# 	except:
# 		return 500