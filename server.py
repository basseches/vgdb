
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "imb2139"
DATABASE_PASSWRD = "password"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
    """
    #
    # example of a database query
    #
    select_query = "select s.game_id, s.title, s.popularity_rating, ROW_NUMBER() OVER (ORDER BY popularity_rating desc) from (select distinct game_id, title, popularity_rating from game) as s LIMIT 3"
    cursor = g.conn.execute(text(select_query))
    names = []
    for result in cursor:
        names.append([result[1], result[2], result[3], result[0]])
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be 
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #     
    #     # creates a <div> tag for each element in data
    #     # will print: 
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data = names)


    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)

@app.route('/addgame', methods=['GET'])
def addgame_page():
    #pull in the correct data needed for the dropdown menus
    mode_query = "select * from game_mode"
    cursor = g.conn.execute(text(mode_query))
    mode = []
    for result in cursor:
        mode.append([result[0], result[1]])
    #genre query
    genre_query = "select title from genre"
    cursor = g.conn.execute(text(genre_query))
    genre = []
    for result in cursor:
        genre.append(result[0])
    #franchise query
    franchise_query = "select title from franchise"
    cursor = g.conn.execute(text(franchise_query))
    franchise  = []
    for result in cursor:
        franchise.append(result[0])
    #platforms query
    platform_query = "select title from platform"
    cursor = g.conn.execute(text(platform_query))
    platform  = []
    for result in cursor:
        platform.append(result[0])

    #dev_leaders query
    devlead_query = "select title from development_leader"
    cursor = g.conn.execute(text(devlead_query))
    devlead  = []
    for result in cursor:
        devlead.append(result[0])
    #companies query
    company_query = "select company_id, title from company"
    cursor = g.conn.execute(text(company_query))
    company = []
    for result in cursor:
        company.append([result[0],result[1]])
    #close at the end
    cursor.close()
    #send info to template as a dictionary
    context = dict(modes = mode, platforms = platform, genres = genre, franchises = franchise, dev_leaders = devlead, companies = company)
    return render_template("addgame.html", **context)

@app.route('/addgame', methods=['POST'])
def addgame():
    title = request.form['title']
    desc = request.form['desc']
    popRate = request.form['popRate']
    esrb = request.form['ESRB']
    release_price = request.form['release_price']
    current_price = request.form['current_price']
    genre = request.form['genre']
    franchise = request.form['franchise']
    platform = request.form['platform']
    dev_leader = request.form['dev_leader']
    developer = request.form['developer']
    publisher = request.form['publisher']
    game_mode = request.form['game_mode']
    

    params = {}
    params["title"] = title
    params["description"] = desc
    params["popularity_rating"] = popRate
    params["esrb_rating"] = esrb
    params["release_price"] = release_price
    params["current_price"] = current_price
    params["genre"] = genre
    params["game_mode"] = game_mode
    params["franchise"] = franchise
    params["platform"] = platform
    params["dev_leader"] = dev_leader
    params["developer"] = developer
    params["publisher"] = publisher

    #push the data to the database
    g.conn.execute(text('INSERT INTO game(title,description,popularity_rating,esrb_rating, release_price, current_price, genre, franchise, platform, dev_leader, game_mode, developer,publisher) VALUES (:title, :description,:popularity_rating,:esrb_rating,:release_price,:current_price,:genre,:franchise,:platform,:dev_leader,:game_mode,:developer,:publisher)'), params)
    g.conn.commit();
    return redirect('/addgame')

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    # accessing form inputs from user
    name = request.form['name']
    
    # passing params in for each variable into query
    params = {}
    params["new_name"] = name
    g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
    g.conn.commit()
    return redirect('/')

#------------------------------------------------------------------------------
# QUERYING

@app.route('/query')
def query():
    return render_template("query.html")

@app.route('/query/budget')
def budget():
    # getting the minimum and maximum prices for our range sliders
    query = "SELECT TO_CHAR(MIN(current_price), 'FM999999990'), " \
        "TO_CHAR(MAX(current_price), 'FM999999990') FROM game"
    cursor = g.conn.execute(text(query))
    names = []
    for result in cursor:
        names.append([result[0], result[1]])
    cursor.close()
    context = dict(data = names)
    return render_template("budget.html", **context)

@app.route('/query/platform')
def platform():
    platform_query = "SELECT title FROM platform"
    cursor = g.conn.execute(text(platform_query))

    platform  = []
    for result in cursor:
        platform.append(result[0])
    cursor.close()
    context = dict(data = platform)
    return render_template("queryplatform.html", **context)

@app.route('/query/budget', methods=['POST'])
def budget_post():
    # accessing form inputs from user
    min_price = request.form['min']
    max_price = request.form['max']

    params = {}
    params["min_price"] = min_price
    params["max_price"] = max_price

    query = "SELECT g.game_id, g.title, g.platform, " \
        "TO_CHAR(g.current_price, 'FM999999990.00') FROM game g " \
        "WHERE current_price >= :min_price AND current_price <= :max_price " \
        "ORDER BY current_price ASC"
    cursor = g.conn.execute(text(query), params)

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2], result[3]])
    cursor.close()
    context = dict(data = names)

    return render_template("results.html", **context)

@app.route('/query/platform', methods=['POST'])
def platform_post():
    # accessing form inputs from user
    params = {}
    params["platform"] = request.form['platform']

    query = "SELECT g.game_id, g.title, g.platform FROM game g " \
        "WHERE g.platform = :platform"
    cursor = g.conn.execute(text(query), params)

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2]])
    cursor.close()
    context = dict(data = names)

    return render_template("results.html", **context)

#------------------------------------------------------------------------------

@app.route('/game/<game>')
def game(game = None):
    if game == None:
        return render_template("notfound.html")

    params = {}
    params["game"] = game
    query = "SELECT g.title, g.description, g.popularity_rating, " \
            "g.esrb_rating, TO_CHAR(g.release_price, 'FM999999990.00'), " \
            "TO_CHAR(g.current_price, 'FM999999990.00'), g.game_mode, " \
            "g.genre, g.franchise, g.platform, g.dev_leader, d.title, " \
            "p.title FROM (game g LEFT OUTER JOIN company d ON " \
            "g.developer = d.company_id) LEFT OUTER JOIN company p ON " \
            "g.publisher = p.company_id WHERE g.game_id = :game"
    cursor = g.conn.execute(text(query), params)
    names = []
    for result in cursor:
        names.append([thing for thing in result])
    cursor.close()

    if not names:
        return render_template("notfound.html")

    context = dict(data = names)
    return render_template("game.html", **context)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
