
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
    mode_query = "select * from game_mode order by game_mode_id desc"
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
    franchise_query = "select title from franchise order by title asc"
    cursor = g.conn.execute(text(franchise_query))
    franchise  = []
    for result in cursor:
        franchise.append([result[0]])
    #platforms query
    platform_query = "select title from platform"
    cursor = g.conn.execute(text(platform_query))
    platform  = []
    for result in cursor:
        platform.append(result[0])

    #dev_leaders query
    devlead_query = "select title from development_leader order by title asc"
    cursor = g.conn.execute(text(devlead_query))
    devlead  = []
    for result in cursor:
        devlead.append(result[0])
    #companies query
    company_query = "select company_id, title from company order by company_id desc"
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
    franchise = request.form['franchise']
    franchise = request.form['franchise']


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

#
#@app.route('/add', methods=['POST'])
#def add():
    # accessing form inputs from user
#    name = request.form['name']

    # passing params in for each variable into query
 #   params = {}
 #   params["new_name"] = name
 #   g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
 #   g.conn.commit()
 #   return redirect('/')
#adding a company to the DB
@app.route('/addcompany', methods=['GET'])
def addcompany_page():
    return render_template('addcompany.html')

@app.route('/addcompany', methods=['POST'])
def addcompanyDB():
    company_name = request.form['company']
    company_country = request.form['country']

    params = {}
    params["company"] = company_name
    params["country"] = company_country

    g.conn.execute(text('INSERT INTO company(title,country) VALUES (:company,:country)'),params)
    g.conn.commit()
    return redirect('/addcompany')
#adding a franchise
@app.route('/addfranchise', methods=['GET'])
def addfranchise_page():
    return render_template('addfranchise.html')

@app.route('/addfranchise', methods=['POST'])
def addfranchise():
    #completely add the new spinoff first
    spinoff_name = request.form['spinoff_title']
    spinoff_type = request.form['spinoff_type']
    spinoff_year = request.form['release_year']


    params = {}
    params["title"] = spinoff_name
    params["type"] = spinoff_type
    params["release_year"] = spinoff_year

    g.conn.execute(text('INSERT INTO spinoff(title,type,release_year) VALUES (:title,:type,:release_year)'),params)
    g.conn.commit()

    #now handle franchise work
    franchise = request.form['franchise']
    spinoff = request.form['spinoff']

    if franchise != "":
        params = {}
        params["franchise"] = franchise
        params["spinoff"] = spinoff

        g.conn.execute(text('INSERT INTO franchise(title,spinoff) VALUES (:franchise,:spinoff)'),params)
        g.conn.commit()
    return redirect('/addfranchise')


#------------------------------------------------------------------------------
# QUERYING

@app.route('/query')
def query():
    return render_template("query.html")

@app.route('/games')
def games():
    query = "SELECT game_id, title, platform, popularity_rating FROM game ORDER BY popularity_rating DESC"
    prefix = "Rating of "
    suffix = "/10"
    cursor = g.conn.execute(text(query))

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2], result[3]])
    cursor.close()
    context = dict(data = names, prefix = prefix, suffix = suffix)
    return render_template("games.html", **context)

@app.route('/games', methods=['POST'])
def games_post():
    query = ""
    prefix = ""
    suffix = ""
    button = int(request.form['sort'])

    if button == 1:
        query = "SELECT game_id, title, platform, popularity_rating FROM game ORDER BY popularity_rating DESC"
        prefix = "Rating of "
        suffix = "/10"
    elif button == 2:
        query = "SELECT game_id, title, platform, popularity_rating FROM game ORDER BY popularity_rating ASC"
        prefix = "Rating of "
        suffix = "/10"
    elif button == 3:
        query = "SELECT game_id, title, platform, TO_CHAR(current_price, '$FM999999990.00') FROM game ORDER BY current_price DESC"
        prefix = "Current price: "
    elif button == 4:
        query = "SELECT game_id, title, platform, TO_CHAR(current_price, '$FM999999990.00') FROM game ORDER BY current_price ASC"
        prefix = "Current price: "
    cursor = g.conn.execute(text(query))

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2], result[3]])
    cursor.close()
    context = dict(data = names, prefix = prefix, suffix = suffix)
    return render_template("games.html", **context)

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
def query_platform():
    platform_query = "SELECT title FROM platform"
    cursor = g.conn.execute(text(platform_query))

    platform  = []
    for result in cursor:
        platform.append(result[0])
    cursor.close()
    context = dict(data = platform)
    return render_template("queryplatform.html", **context)

@app.route('/query/genre')
def query_genre():
    genre_query = "SELECT title FROM genre"
    cursor = g.conn.execute(text(genre_query))

    genre = []
    for result in cursor:
        genre.append(result[0])
    cursor.close()
    context = dict(data = genre)
    return render_template("querygenre.html", **context)

@app.route('/query/year')
def year():
    # getting the minimum and maximum release years for our range sliders
    query = "SELECT TO_CHAR(MIN(EXTRACT('Year' FROM release_date)), 'FM999999990'), " \
            "TO_CHAR(MAX(EXTRACT('Year' FROM release_date)), 'FM999999990') FROM release_date"
    cursor = g.conn.execute(text(query))
    names = []
    for result in cursor:
        names.append([result[0], result[1]])
    cursor.close()
    context = dict(data = names)
    return render_template("year.html", **context)

@app.route('/query/game')
def query_game():
    return render_template("querygame.html")

@app.route('/query/budget', methods=['POST'])
def budget_post():
    # accessing form inputs from user
    min_price = request.form['min']
    max_price = request.form['max']

    params = {}
    params["min_price"] = min_price
    params["max_price"] = max_price

    query = "SELECT g.game_id, g.title, g.platform, " \
            "TO_CHAR(g.current_price, '$FM999999990.00') FROM game g " \
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

@app.route('/query/genre', methods=['POST'])
def genre_post():
    # accessing form inputs from user
    params = {}
    params["genre"] = request.form['genre']

    query = "SELECT g.game_id, g.title, g.platform, g.genre FROM game g " \
            "WHERE g.genre = :genre"
    cursor = g.conn.execute(text(query), params)

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2], result[3]])
    cursor.close()
    context = dict(data = names)

    return render_template("results.html", **context)

@app.route('/query/year', methods=['POST'])
def year_post():
    # accessing form inputs from user
    min_yr = request.form['min']
    max_yr = request.form['max']

    params = {}
    params["min_yr"] = min_yr
    params["max_yr"] = max_yr

    query = "SELECT g.game_id, g.title, g.platform, " \
            "TO_CHAR(EXTRACT('Year' FROM release_date), 'FM999999990') AS release_year FROM game g NATURAL JOIN release_date r " \
            "WHERE EXTRACT('Year' FROM release_date) >= :min_yr AND EXTRACT('Year' FROM release_date) <= :max_yr " \
            "ORDER BY release_year DESC"
    cursor = g.conn.execute(text(query), params)

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2], result[3]])
    cursor.close()
    context = dict(data = names)

    return render_template("results.html", **context)

@app.route('/query/game', methods=['POST'])
def game_post():
    # accessing form inputs from user
    name = '%' + request.form['name'].lower() + '%'

    params = {}
    params["name"] = name

    query = "SELECT g.game_id, g.title, g.platform FROM game g " \
            "WHERE LOWER(g.title) LIKE :name"
    cursor = g.conn.execute(text(query), params)

    names = []
    for result in cursor:
        names.append([result[0], result[1], result[2]])
    cursor.close()
    context = dict(data = names)

    return render_template("results.html", **context)

@app.route('/query/all/<search>', methods=['GET', 'POST'])
def all_post(search=None):
    search = '%' + search.lower() + '%'

    params = {}
    params["search"] = search

    query = "SELECT g.game_id, g.title, g.platform FROM game g " \
            "WHERE LOWER(g.title) LIKE :search"
    cursor = g.conn.execute(text(query), params)

    games = []
    for result in cursor:
        games.append([result[0], result[1], result[2]])

    query = "SELECT g.title FROM genre g " \
            "WHERE LOWER(g.title) LIKE :search"
    cursor = g.conn.execute(text(query), params)

    genres = []
    for result in cursor:
        genres.append([result[0]])

    query = "SELECT c.company_id, c.title FROM company c " \
            "WHERE LOWER(c.title) LIKE :search"
    cursor = g.conn.execute(text(query), params)

    companies = []
    for result in cursor:
        companies.append([result[0], result[1]])

    query = "SELECT p.title FROM platform p " \
            "WHERE LOWER(p.title) LIKE :search"
    cursor = g.conn.execute(text(query), params)

    platforms = []
    for result in cursor:
        platforms.append([result[0]])

    cursor.close()
    context = dict(games = games, genres = genres, companies = companies,
                        platforms = platforms)

    return render_template("allresults.html", **context)

#------------------------------------------------------------------------------

@app.route('/game/<game>')
def game(game = None):
    if game == None:
        return render_template("notfound.html")

    params = {}
    params["game"] = game
    query = "SELECT g.title, g.description, g.popularity_rating, " \
            "g.esrb_rating, TO_CHAR(g.release_price, 'FM999999990.00'), " \
            "TO_CHAR(g.current_price, 'FM999999990.00'), gm.game_mode, " \
            "g.genre, g.franchise, g.platform, g.dev_leader, d.title, " \
            "p.title FROM ((game g LEFT OUTER JOIN company d ON " \
            "g.developer = d.company_id) LEFT OUTER JOIN company p ON " \
            "g.publisher = p.company_id) LEFT OUTER JOIN game_mode gm ON " \
            "g.game_mode = gm.game_mode_id WHERE g.game_id = :game"
    cursor = g.conn.execute(text(query), params)
    names = []
    for result in cursor:
        names.append([thing for thing in result])

    query = "SELECT d.company_id FROM game g, company d " \
            "WHERE g.game_id = :game AND g.developer = d.company_id"
    cursor = g.conn.execute(text(query), params)
    developer = []
    for result in cursor:
        developer.append([thing for thing in result])

    query = "SELECT p.company_id FROM game g, company p " \
            "WHERE g.game_id = :game AND g.publisher = p.company_id"
    cursor = g.conn.execute(text(query), params)
    publisher = []
    for result in cursor:
        publisher.append([thing for thing in result])

    cursor.close()

    if not names:
        return render_template("notfound.html")

    context = dict(data = names, dev = developer, pub = publisher)
    return render_template("game.html", **context)

#------------------------------------------------------------------------------

@app.route('/genre/<genre>')
def genre(genre = None):
    if genre == None:
        return render_template("notfound.html")

    params = {}
    params["genre"] = genre
    query = "SELECT g.title, g.description, n.num_games FROM genre g LEFT OUTER JOIN " \
            "(SELECT genre.title, COUNT(*) AS num_games FROM game, genre " \
            "WHERE game.genre = genre.title GROUP BY genre.title) AS n " \
            "ON n.title = g.title WHERE g.title = :genre"
    cursor = g.conn.execute(text(query), params)
    names = []
    for result in cursor:
        names.append([thing for thing in result])

    genre_query = "SELECT game.game_id, game.title, game.platform FROM game, genre " \
            "WHERE genre.title = :genre AND game.genre = genre.title"
    cursor = g.conn.execute(text(genre_query), params)
    games = []
    for result in cursor:
        games.append([thing for thing in result])
    cursor.close()

    if not names:
        return render_template("notfound.html")

    context = dict(data = names, games = games)
    return render_template("genre.html", **context)

#------------------------------------------------------------------------------
@app.route('/platform/<platform>')
def platform(platform = None):
    if platform == None:
        return render_template("notfound.html")

    params = {}
    params["platform"] = platform 
    query = "select * from platform as p where p.title = :platform"
    cursor = g.conn.execute(text(query), params)
    names = []
    for result in cursor:
        names.append([thing for thing in result])

    games_query = "SELECT game_id, title, platform FROM game where platform = :platform"
    cursor = g.conn.execute(text(games_query), params)
    games = []
    for result in cursor:
        games.append([thing for thing in result])

    count_query = "SELECT count(*) from (select game_id from game where platform = :platform) as f"
    cursor = g.conn.execute(text(count_query), params)
    count = []
    for result in cursor:
        count.append(result[0])

    cursor.close()

    if not names:
        return render_template("notfound.html")

    context = dict(data = names, games = games, count = count)
    return render_template("platform.html", **context)

#---------------------------------------------------------------------

@app.route('/company/<company>')
def company(company = None):
    if company == None:
        return render_template("notfound.html")

    params = {}
    params["company"] = company
    query = "SELECT title, country FROM company WHERE company_id = :company"
    cursor = g.conn.execute(text(query), params)
    names = []
    for result in cursor:
        names.append([thing for thing in result])

    dev_query = "SELECT game.game_id, game.title, game.platform FROM game, company " \
            "WHERE company.company_id = :company AND game.developer = company.company_id"
    cursor = g.conn.execute(text(dev_query), params)
    devs = []
    for result in cursor:
        devs.append([thing for thing in result])
    cursor.close()

    pub_query = "SELECT game.game_id, game.title, game.platform FROM game, company " \
            "WHERE company.company_id = :company AND game.publisher = company.company_id"
    cursor = g.conn.execute(text(pub_query), params)
    pubs = []
    for result in cursor:
        pubs.append([thing for thing in result])
    cursor.close()

    if not names:
        return render_template("notfound.html")

    context = dict(data = names, devs = devs, pubs = pubs)
    return render_template("company.html", **context)

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
