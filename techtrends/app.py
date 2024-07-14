import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from datetime import datetime

connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info(f"{date_time} Successfully retrieved the main page of TechTrends app")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if post is None:
      app.logger.info(f"{date_time} Invalid post_id={post_id}. Hence, 404 - File Not Found")
      return render_template('404.html'), 404
    else:
      post_title = post['title']
      app.logger.info(f"{date_time} Valid post_id={post_id}. Successfully retrieved the article: {post_title}")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.logger.info(f"{date_time} Successfully retrieved the 'About Us' page")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
            app.logger.info(f"{date_time} Unable to create new post since 'title' is missing")
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f"{date_time} Created new post with title: {title}")

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route("/healthz")
def healthz():
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info(f"{date_time} Healthz request successful")
    return response

@app.route('/metrics')
def metrics():
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(1) from posts').fetchone()[0]
    response = app.response_class(
            response=json.dumps({"db_connection_count":connection_count,"post_count":post_count}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info(f"{date_time} Metrics request successful")
    return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
