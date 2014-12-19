import os
import redis
import flask
import urlparse

from model.movies import get_auto_complete_result, get_movie_by_title
from flask import Flask, Response,request, render_template
from app import app

url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL'))
redis_handle = redis.Redis(host=url.hostname, port=url.port, password=url.password)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/movies/', methods=['GET'])
def get_movie():
    title = request.args.get("title")
    result = get_movie_by_title(redis_handle, title)
    response = {}
    response["data"] = result
    return flask.jsonify(response)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get("query")
    result = get_auto_complete_result(redis_handle, "title", search, 10)
    response = {}
    response["data"] = result
    return flask.jsonify(response)

@app.route('/js/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
