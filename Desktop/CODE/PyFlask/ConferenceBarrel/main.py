''' To run the application: 

-> Set the environment variable that contains the aplication
    The flask will look for this appication in the variable named «FLASK_APP»
-> use this command: $Env:FLASK_APP="main.py"

($Env:FLASK_APP="Any_Other_Name.py")


By default we need lways to restart server to see the changes,
but by setting «debug» variable we can change that: $Env:FLASK_DEBUG=1
After that all the chages will be seen after refreshing html page

'''
# Import Flask application object
# reneder_template() -> to render html page inside the «basetemplatepage.html»
# abrot() -> to display «404» error if page does not exists
# reuest to 'POST' and 'GET' data from data base (used in search form)
from flask import Flask, render_template, abort, request

# Import SQLAlchemy to manage DB
from flask_sqlalchemy import SQLAlchemy


# Date time for db use
from datetime import datetime


# New instance of a Flask bject to handle http trafic
# Value passed into initializer is the default module for assets to be found
# For large application it is better to have assets in a several modules for usability
# For small application it is not necessary
app = Flask(__name__)




####### Setting up the data base
# We will use Flask-SQLAlchemy to write code and test on SQLite
# As this code can be used on others data bases we will then use PotrageSQL to implement app on Heroku

# Path to the sql db
# To use another data base (PostregeSQL) we will need just to use another path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conferencebarrel.sqlite'

# Dissable a Flask warning - no reason why it is appear
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Pass SQLAlchemy with initilizer into new variable for future use
db = SQLAlchemy(app)


# Create a class to manage Conference DB:
class Conference(db.Model):
    #### this vars: «id», «title»,«date»,«ticket_cost» => will be used in the html page inside the « block » : <h3> Conference name: {{conference_details.title}} </h3>
    # field name = database.Column(value/field type, constrains «primary_key=True», «nullable=False» (NOT NULL), «default=datetime.utcnow»(if an object is not assigned by defaut it will assume todays date)) 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ticket_cost = db.Column(db.Float, nullable=False)

    # Function for string representation of the method
    def __repr__(self):
        return f'Conference {self.title}'


# After create class «Conference» -> VIEW FILE CALLED «manage_db_in_terminal_info»





# Function for http requests
# We need to use wrapper to wrapp this function in a https response -> To wich request should be handled by this function
## -> Every wrapper need to have same name that function: @app.route('/Nome1') -> def Nome1()
# We wrapp httpm request to a «index» function wich can return text into html page or html page, or other contentn into html page
## -> To readdress the main page «http://127.0.0.1:5000/» to «/index» use @app.route('/')
@app.route('/')
@app.route('/index')
def index():
    #To pass plain text into html just type: «return "Conference Barrel"»
    #To return html page use templates function «return render_template('name.tml')»
    return render_template('index.html')



### html for «about» page
# Add another wrapper to add new function that will create html content
@app.route('/static/about')
def about():
    return 'About this Conference Barrel'


### html for «conferences» page
### html for «/conferences/<conference_id>» page
# -> To pass any numeric value into html page = define variable in wrapper: <conference_id>
# and pass it into function 
# -> To specify var type add «int» : <int:conference_id>
# -> To create a page for "conferences" only just create another wrapper above existant function 
## -> You can have multiple route to decorate (wrap) a single function
#####  Explanation: if there is «number» after «/conference/» display «details.html»
#####               Else (if there is NO «number» after «/conference/») display «conferences.html»

Conf_num = 0

@app.route('/conferences')
@app.route('/conferences/<int:conference_id>')
## -> Add the default of "None" so the if would function properly
def conferences(conference_id=None):
    if conference_id is not None:
        # declare global variable to pass into it any «conference_id» to pass into «404» error page
        global Conf_num
        Conf_num = conference_id
        # return text with variable passed into function and wrapped into html request wrapper previously
        # return f'Detailes about conference {conference_id}'
        ### Import all values from table by field ID
        conference_details = Conference.query.get(conference_id)
        # If «conference_details» object is None display «404» page error
        if conference_details is None:
            abort(404)
        return render_template('details.html', conference_details=conference_details)
    else:
        # To view data base just use variable to pass data base values: conferences = Conference.query.all()
        return render_template('conferences.html', conferences=Conference.query.all())

@app.errorhandler(404)
def handle_404(e):
    # «return» function is a tuple so you can add another argument after comma «,»
    return render_template('404.html', Conf_num=Conf_num),404

# to search data base with «request» method from Flask
# To use other method than 'GET' (wich is defined by default) add into «@app.route» oher methods: methods=['GET', 'POST']
@app.route('/search', methods=['GET', 'POST'])
def search():
    # get the form method from search form with «request» method
    if request.method == 'POST':
        # var that passes value into search query
        needle = request.form['needle']
        # Pass result into «result» 
        ### => «filter» «Conference» data base by «title» «like» in «needle» varibale + search for «all()»
        # «%» meanins anything after and aything before the value in the «needle»
        results = Conference.query.filter(Conference.title.like(f'%{needle}%')).all()
        # «return» «results.html» page with «results» from querying data base
        return render_template('results.html', results=results)
    else:
        return render_template('search.html')



