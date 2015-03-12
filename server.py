from flask import Flask, render_template, redirect, request, g, url_for, flash, make_response, jsonify
from flask import session
from db import model
import jinja2
import os
import fsqapi
import config
import json

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
	
	# Pull needed info out of request object
	username = request.form['username']
	# email = request.form['email']
	password = request.form['password']

	all_users = model.session.query(model.User)
	
	# Add the info from the request object as keys to the sessio dict
	try:
		user = all_users.filter(model.User.username==username, model.User.password==password).one()
		session['username'] = user.username
		# session['user_email'] = user.email
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

# @app.route("/")
# def index():
# 	"""Render the welcome/notifications page"""

# 	# query for a user's pending recommendations


# 	return render_template("index.html")

@app.route("/restaurant-results")
def show_restaurant_info():
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

	except Exception as e:
		# print e.message
		# if the user entered a location FSQ cannot geocode				
		fsq_venues_list = []

		flash("Please enter a city name.") 
		return redirect('/')

@app.route("/save-db")	
def save_to_db():		
	"""Saves the restaurant and the bookmark as new records in the db"""
	
	logged_in_user_id = session['user_id']

	# pulls the needed fields from the request object
	name = request.args["name"]
	fsq_id = request.args["fsqId"]
	lat = request.args["lat"]
	lng = request.args["lng"]
	cuisine = request.args["cuisine"]
	address = request.args["address"]
	city = request.args["city"]
	state = request.args["state"]
	url = request.args["url"]
	phone = request.args["phone"]

	# print "request object: ", request.args
	# print "Name: ", name
	# print "FSQ ID: ", fsq_id
	# print "Lat: ", lat 
	# print "Lng: ", lng 
	# print "Cuisine: ", cuisine

	saved_restaurant = model.session.query(model.Restaurant).filter(model.Restaurant.fsq_id==fsq_id).first()
	saved_bookmark = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==logged_in_user_id, 			
		model.Bookmark.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()

	#If the restaurant DOESN'T exist in the db (& thus implicitly the bookmark doesn't exist)
	if not saved_restaurant: 
		# save a new restaurant to the restaurants table
		new_restaurant = model.Restaurant(fsq_id=fsq_id, name=name, 
						lat=lat, lng=lng, cuisine=cuisine, address=address, city=city, state=state, url=url, phone=phone)
		model.session.add(new_restaurant)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_restaurant
		model.session.refresh(new_restaurant) 

		# save a new bookmark to the bookmarks table
		new_bookmark = model.Bookmark(user_id=logged_in_user_id, restaurant_id=new_restaurant.id)		
		model.session.add(new_bookmark)
		model.session.commit()

		return jsonify({"message": "You added %s to your bookmarks!" % new_restaurant.name}) 

	# the bookmark ALREADY exists for the user (& thus the restaurant also already exists) - ie. the restaurant id is already associated with that user 
	elif saved_bookmark:
		return jsonify({"message": "You already bookmarked this restaurant!"}) 

	# elif the restaurant DOES exist BUT the bookmark doesn't exist for this user - ie. the restaurant id is not associated with a bookmark for this user
	elif saved_restaurant and not saved_bookmark:
		new_bookmark = model.Bookmark(user_id=logged_in_user_id, restaurant_id=saved_restaurant.id)		
		model.session.add(new_bookmark)
		model.session.commit()
		return jsonify({"message": "You added %s to your bookmarks!" % saved_restaurant.name})	

@app.route("/user_info")
def get_user_info():
	"""Send user info to the modal so it can populate the modal that the user sees
	when they click recommend"""
	# query for all the usernames in the database
	all_usernames = model.session.query(model.User.username)
	# print "all usernames: ", all_usernames

	logged_in_username = session['username']
	# print "Logged in username: ", logged_in_username

	# create a list with all usernames except for the user who is currently logged in
	usernames = [user.username for user in all_usernames if user.username!=logged_in_username]
	# print "usernames list", usernames

	# send this list as JSON
	return jsonify({"username": usernames})

@app.route("/map")
def show_map():
	"""Render map and return info about user's bookmarks to populate list"""
	logged_in_user_id = session['user_id']

	# query for the user's bookmarks and all related information 
	detailed_data = model.session.query(model.Bookmark.id, model.Restaurant.id, 
		model.Restaurant.fsq_id, model.Restaurant.name, model.Restaurant.cuisine, 
		model.Restaurant.address, model.Restaurant.city, model.Restaurant.state, 
		model.Restaurant.phone, model.Restaurant.url).join(model.Restaurant).filter(model.Bookmark.user_id==logged_in_user_id).all()
	print detailed_data 

	return render_template("map.html", restaurant_data = detailed_data)	

@app.route("/bookmark-info")
def return_bookmark_info():
	"""Return information about the user's bookmarks to populate map"""

	logged_in_user_id = session['user_id']

	# get restaurant info for all the user's bookmarked restaurants
	data = model.session.query(model.Bookmark.id, model.Restaurant.fsq_id, 
		model.Restaurant.name, model.Restaurant.lat, model.Restaurant.lng, 
		model.Restaurant.cuisine, model.Restaurant.address, model.Restaurant.url).join(model.Restaurant).filter(model.Bookmark.user_id==
		logged_in_user_id).all()

	# create a dictionary with all the info necessary to pass on to jinja in order to map markers 
	restaurant_info = {}
	for item in data:
		restaurant_info[item.id] = {}						# item.id == bookmark id 
		restaurant_info[item.id]["fsq_id"] = item.fsq_id
		restaurant_info[item.id]["name"] = item.name
		restaurant_info[item.id]["lat"] = item.lat
		restaurant_info[item.id]["lng"] = item.lng
		restaurant_info[item.id]["cuisine"] = item.cuisine
		restaurant_info[item.id]["address"] = item.address
		restaurant_info[item.id]["url"] = item.url

	print session
	print logged_in_user_id
	print "\n \n restaurant_info: ", restaurant_info

	return jsonify(restaurant_info)

@app.route("/delete-bookmark")
def delete_bookmark(): 
	"""Delete the user's selected bookmark """
	logged_in_user_id = session['user_id']

	# get the bookmark id for the bookmark the user wants to delete 
	bkm_id_to_delete = request.args['bookmarkId']
	
	# query for the bookmark with that id 
	bkm_to_delete = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==logged_in_user_id, 
		model.Bookmark.id==bkm_id_to_delete).first()
	print "Bookmark to delete ", bkm_to_delete
	restaurant_to_delete = bkm_to_delete.restaurant.name
	print "Restaurant name to delete ", restaurant_to_delete
	
	# delete the restaurant from the db 
	model.session.delete(bkm_to_delete)
	model.session.commit()

	# return "This string!"
	return jsonify({"message": "You deleted %s from your bookmarks." % restaurant_to_delete}) 

@app.route("/recommend")
def recommend_restaurant():
	"""Send information to server for one user to recommend a restaurant to another"""

	#get the user id of the recommender(logged in user)
	recommender_id = session['user_id']
	# print "recommender id: ", recommender_id

	#get the user id of the recipient (from request obj), as well as rest of info needed to save to db 
	recipient_username = request.args['usernameRecipient']
	name = request.args["name"]
	fsq_id = request.args["fsqId"]
	lat = request.args["lat"]
	lng = request.args["lng"]
	cuisine = request.args["cuisine"]
	address = request.args["address"]
	city = request.args["city"]
	state = request.args["state"]
	url = request.args["url"]
	phone = request.args["phone"]

	# print "Request object: ", request.args

	# query for the recipient 
	recipient = model.session.query(model.User).filter(model.User.username==recipient_username).first()
	print "recipient id: ", recipient.id

	# query to check if that restaurant is already in restaurants table
	saved_restaurant = model.session.query(model.Restaurant).filter(model.Restaurant.fsq_id==fsq_id).first()

	# query to check if the recipient already has that restaurant bookmarked 
	saved_bookmark = model.session.query(model.Bookmark).filter(model.Bookmark.user_id==recipient.id, 			
		model.Bookmark.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()

	# query to see if the recipient already has that recommendation	pending - CHECK THIS AFTER MAKE MY FIRST RECOMMENDATION
	# pending_recommendation = model.session.query(model.Recommendation).filter(model.Recommendation.recipient_id==recipient.id,
	# 	model.Recommendation.restaurant_id==saved_restaurant.id, model.Recommendation.pending==True).first()
	# FIXME: WITH THIS QUERY THE IF NOT SAVED RESTAURANT CONDITIONAL DOESN'T WORK

	saved_recommendation = model.session.query(model.Recommendation).filter(model.Recommendation.recommender_id==recommender_id, 
		model.Recommendation.recipient_id==recipient.id, model.Recommendation.restaurant.has(model.Restaurant.fsq_id==fsq_id)).first()
	# print "*********Saved recommendation: ", saved_recommendation

	if not saved_restaurant:
		# save the restaurant to db
		new_restaurant = model.Restaurant(fsq_id=fsq_id, name=name, 
						lat=lat, lng=lng, cuisine=cuisine, address=address, city=city, 
						state=state, url=url, phone=phone)
		model.session.add(new_restaurant)
		model.session.commit()

		# refresh to refer to the SQLAlchemy reference for the new_restaurant
		model.session.refresh(new_restaurant) 

		# save a new recommendation 
		new_recommendation = model.Recommendation(restaurant_id=new_restaurant.id, 
			recommender_id=recommender_id, recipient_id=recipient.id, pending=True)		
		model.session.add(new_recommendation)
		model.session.commit()

		return jsonify({"message": "You recommended %s to %s!" % (new_restaurant.name, recipient_username)}) 

	# elif saved_restaurant and not (pending_recommendation and saved_bookmark):	#FIXME: Not sure if AND or OR Is appropriate here - want to make sure its neither 
	# 	# add a new recommendation to that user
	# 	new_recommendation = model.Recommendation(restaurant_id=saved_restaurant.id, 
	# 		recommender_id=recommender_id, recipient_id=recipient.id, pending=True)		
	# 	model.session.add(new_recommendation)
	# 	model.session.commit()

	elif saved_recommendation:
		return jsonify({"message": "You already recommended %s to %s!" % (saved_restaurant.name, recipient_username)}) 

	# elif pending_recommendation:
	# 	return jsonify({"message": "%s already has this recommendation pending!" % recipient_username}) 
	elif saved_bookmark:
		return jsonify({"message": "%s already has this restaurant bookmarked." % recipient_username}) 

	else:
		new_recommendation = model.Recommendation(restaurant_id=saved_restaurant.id, 
		recommender_id=recommender_id, recipient_id=recipient.id, pending=True)		
		model.session.add(new_recommendation)
		model.session.commit()
		return jsonify({"message": "You recommended %s to %s!" % (saved_restaurant.name, recipient_username)}) 

	return "got to recommend restaurant route!"

@app.route("/")
def show_recommendations():
	"""Send to front-end to show recommendation notifications"""
	
	logged_in_user_id = session['user_id']
	logged_in_username = session['username']

	recommendations = model.session.query(model.Recommendation).filter(
		model.Recommendation.recipient_id == logged_in_user_id, model.Recommendation.pending==True).all()

	# rec = recommendations.all()[0]
	# for rec in recommendations:
	# 	print rec.restaurant.cuisine

	# rec_data = {}
	# for rec in recommendations:
	# 	print rec.recommender.username
	# 	print rec.recipient.username
	# 	print rec.id
	# 	print rec.restaurant.name
	# 	print rec.restaurant.cuisine
	# 	print rec.restaurant.address
	# 	print rec.restaurant.city
	# 	print rec.restaurant.state
	# 	print rec.restaurant.url

	rec_data = {}
	for rec in recommendations:
		rec_data[rec.id] = {}						# item.id == bookmark id 
		rec_data[rec.id]["bkm_id"] = rec.id
		rec_data[rec.id]["recommender_username"] = rec.recommender.username
		rec_data[rec.id]["recipient_username"] = rec.recipient.username
		rec_data[rec.id]["rest_name"] = rec.restaurant.name
		rec_data[rec.id]["rest_cuisine"] = rec.restaurant.cuisine
		rec_data[rec.id]["rest_address"] = rec.restaurant.address
		rec_data[rec.id]["rest_city"] = rec.restaurant.city
		rec_data[rec.id]["rest_state"] = rec.restaurant.state
		rec_data[rec.id]["rest_url"] = rec.restaurant.url
		rec_data[rec.id]["rec_pending"] = rec.pending

	print rec_data

	# return jsonify({"message": "this message"})
	return render_template("index.html", recommendations = rec_data, username = logged_in_username)

# @app.route("/change-recommendation")
# def change_recommendation():

if __name__ == "__main__":
    app.run(debug = True)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", debug=False)





