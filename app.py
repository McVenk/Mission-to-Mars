# import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
from scrape_mars1 import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")



@app.route("/")
def index():
    # Run the scrape function
    mars_data = mongo.db.mars_data.find_one()

   
    # Redirect back to home page
    return render_template("index.html",mars=mars_data)

# Defining another route to execute scrape of all sites
@app.route("/scrape")
def scrape():
    # adding data to mongo-mars_data fb
    mars_data=scrape_mars()
    #print("***************")
    print(type(mars_data))
    #print("***************")
    # sending data into database collection
    mongo.db.mars_data.update({}, mars_data, upsert=True)

    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)