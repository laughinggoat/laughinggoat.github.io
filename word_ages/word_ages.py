# -*- coding: utf-8 -*-

import requests, os, bs4, time
from multiprocessing import Pool
from flask import Flask,send_from_directory
from flask.json import jsonify
from flask import make_response, request, current_app ##???
import simplejson as json
from datetime import timedelta
from functools import update_wrapper
import pickle

## Set up Flask app
app = Flask(__name__)

## Nonsense to deal with crossdomain error
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp
        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


base_url = "https://www.merriam-webster.com/dictionary/"

def first_known_use(word):
    url = base_url + word
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html5lib")
    target_id = "first-known-use-explorer"
    if len(word)<3:
        return None
    try:
        date_div = soup.find_all("div", {"id" : target_id})
        date = date_div[0].find_all("div", {"class" : "new-text"})
        return date_div[0].find_all("div")[0].find("p").text.split(": ")[1]
    except:
        return None

def get_word_ages(text):
    start = time.time()
    words = text.split(' ')
    p = Pool(10)
    word_scores = p.map(first_known_use,words)
    p.terminate()
    p.join()
    end = time.time()
    delta = str(end-start)
    print('Took ' + delta + ' seconds')
    return word_scores

def usable_age(age):
    if not age:
        return None
    if "century" in age:
        if "before" in age:
            century = age.split(" ")[1][:-2]
            return int(century)*100
        else:
            century = age.split(" ")[0][:-2]
            return (int(century)*100)-50
    if "circa" in age:
            year = age.split(" ")[1]
            return int(year)
    else:
        return int(age)

def mean_age(ages):
    usable_ages = [usable_age(age) for age in ages if age]
    return sum(usable_ages)/len(usable_ages)

@app.route("/")
def send_foo():
     return send_from_directory('static', 'word_ages3.html')

@app.route("/load", methods=["POST", "GET"])
@crossdomain(origin='*')
def send_examples():
    with open('example.p','rb') as f:
        examples = pickle.load(f)
    return json.dumps(examples)

@app.route("/convert", methods=["POST", "GET"])
@crossdomain(origin='*')
def analyse():
    text = request.form.get("converttext")
    while True:
        try:
            ages = get_word_ages(text)
        except:
            continue
        break
    usable = [usable_age(age) for age in ages]
    ages_zip = list(zip(text.split(' '), usable, ages))
    return json.dumps(ages_zip)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
