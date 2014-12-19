import  os, requests, redis, json
import urlparse

movie_api_url = "http://data.sfgov.org/resource/yitu-d5am.json"

# Load data into redis.

GOOGLE_API_KEY = 'AIzaSyBujpw4p4cnB-JgFFMBGEuwvAGFYllkGps'
GOOGLE_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address={address}&sensor={sensor}&key={key}'

def add_to_auto_complete_sorted_set(redis_handle, category, data):
    '''
    Process a data record for auto_complete. I used the sorted set as the data structure to cache the prefix. For example,
    if we want to cache for word apple. We will stored the following prefix:
    a, ap, app, appl, apple*. I use * to indicate the ending of a complete term. So once we navigate to a prefix we can easily find the
    candidate ending as *.
    :param redis_handle:
    :param category: The autocomplete part of the data. For example, title could be the part of auto complete search.
     In the future we can also set other part of the data to cache the auto_complete.
    :param data: The movie record to process for auto_completing
    :return:
    '''
    print "Loading " + category+ " "+ data + " into redis db for auto complete pre-processing"
    n = data.strip()
    auto_complete_set = category + "_compl"
    for l in range(1,len(n)):
        prefix = n[0:l]
        redis_handle.zadd(auto_complete_set, prefix, 0)
    redis_handle.zadd(auto_complete_set, n+"*", 0)

def get_auto_complete_result(redis_handle, category, prefix, count):
    '''
    Given a user input prefix and returns a list of auto_complete items. Redis sorted set provides method zrank which can
    allows us quickly find the index of an item. So we can reduce the query time complexity to Log(n).
    :param redis_handle:
    :param category: The category cache for auto_complete
    :param prefix: The user's input as prefix for auto complete
    :param count:  The number of the results that matches the prefix that are returned to uers
    :return: A list of the text that matches the prefix.
    '''
    auto_complete_set = category + "_compl"
    results = []
    rangelen = 200
    start = redis_handle.zrank(auto_complete_set, prefix)
    if not start:
        return []
    while (len(results) < count):
        range = redis_handle.zrange(auto_complete_set, start, start + rangelen - 1)
        start += rangelen
        if not range or len(range) == 0:
            break
        for entry in range:
            minlen = min(len(entry), len(prefix))
            if entry[0:minlen] != prefix[0:minlen]:
                count = len(results)
                break
            if entry[-1] == "*" and len(results) < count:
                results.append(entry[0:-1])
    return results

def save_movie_to_redis(redis_handle, movie):
    '''
    Saving each movie as a set in redis.
    :param redis_handle:
    :param movie: movie JSON object
    :return:
    '''
    redis_handle.sadd(movie["title"], json.dumps(movie))
    add_to_auto_complete_sorted_set(redis_handle, "title", movie["title"])
    return movie

def process_film_data(redis_handle, movie):
    '''
    Go through each movie. Store the movie into redis and process movie item to cache for auto complete.
    :param redis_handle:
    :param movie: movie json object.
    :return:
    '''
    if "locations" not in movie.keys():
        return
    address = '%s, San Francisco, CA' % movie['locations']
    address = address.encode('utf-8')
    google_map_api_url = GOOGLE_API_URL.format(address = address, sensor ='false', key = GOOGLE_API_KEY)
    api_response = requests.get(google_map_api_url)
    if api_response.status_code != 200:
        print "Failed to connect to geo code api"
        return
    map_json_response = api_response.json()
    if map_json_response['status'] == 'OK' and len(map_json_response['results']) > 0:
      movie['geocode'] = map_json_response['results'][0]
    else:
        print "cannot find the geo code for the item"
        return
    save_movie_to_redis(redis_handle, movie)
if __name__ == "__main__":
    response = requests.get(movie_api_url)
    if response.status_code != 200:
        print "Failed to connect to movie api"
    movie_json_response = response.json()
    url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL'))
    redis_handle = redis.Redis(host=url.hostname, port=url.port, password=url.password)
    for movie in movie_json_response:
        add_to_auto_complete_sorted_set(redis_handle, "title", movie["title"])
        process_film_data(redis_handle, movie)

