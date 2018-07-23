# import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape

# create instance of Flask app
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars"
mongo = PyMongo(app)

# create route that renders index.html template and finds documents from mongo
@app.route("/")
def home():
    # import pdb; pdb.set_trace()
    # Find data
    data = mongo.db.mars.find_one()
    
    # return template and data
    return render_template("index.html", data=data)

# Route that will trigger scrape functions
@app.route("/scraper")
def scraper():

    # Run scraped functions
    data = scrape.scrape()

    mongo.db.mars.update(
        {},
        data,
        upsert=True
    )

    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)