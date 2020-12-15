from bs4 import BeautifulSoup 
from flask import Blueprint, render_template, jsonify, request
from flask import current_app as app
import json
import os.path
import requests

bp = Blueprint(
    'home',
    'routes',
    url_prefix="/"
)

# globals
library_file = os.path.join(os.path.dirname(app.instance_path), app.config['LIBRARY_FILENAME'])
catalog_file = os.path.join(os.path.dirname(app.instance_path), app.config['CATALOG_FILENAME'])

@bp.route("/")
def home():
    global library
    return render_template('home.html', list=library)

def find_by_id(id):
    global library
    if isinstance(id, str):
        id = int(id)

    for item in library:
        if item['id'] == id:
            return item
    return {}

@bp.route("/_update/item", methods=["POST"])
def update_book_status():
    id = request.json['id']
    status = request.json['status']
    if isinstance(status, str):
        status = int(status)

    item = find_by_id(id)
    if len(item) > 0:
        item['status'] = status
        save_library()
        return id
    return {}

# TODO
# consider removing catalog, 
# compare length of library to latest catalog
# need some ui work to inform about updates
# not liking the use of a nav link for this 
# maybe use a new icon to show it is new
# 'sunshine' icon require clicking to 
# accept into 
@bp.route("/_update/catalog")
def update_catalog():
    catalog = load_catalog()
    latest = get_latest_catalog()
    assert(len(latest) > 0)
    diff = get_list_diff(latest, catalog)

    if len(diff) > 0:
        # latest is authoritative so overwrite the catalog
        save_catalog(latest)
        # add new items to library
        update_library_with(diff)
    return jsonify({"count": len(diff)})

def get_latest_catalog():
    ''' webscrape to create a list of LoA titles ''' 
    url = app.config['LOA_COLLECTION_URL']
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    books = soup.find_all('li', class_='content-listing--book')
    result = []

    for book in books:
        id = int(book.find('i', class_='book-listing__number').text)
        title = book.find('b', class_='content-listing__title').text
        link = app.config['LOA_BASE_URL'] + book.find('a')['href']
        book = {"id": id, "title": title, "link": link, "status": 3}
        result.append(book)
    return result

# List Helpers
def get_list_diff(list1, list2):
    diff = [i for i in list1 + list2 if i not in list1 or i not in list2]
    return diff

def empty_list(id=0, title='NA', link=''):
    return [{'id': id, 'title': title, 'link': link}]

def write_list_to_file(lst, fname):
    json.dump(lst, open(fname, 'w'))

def read_list_from_file(fname):
    return json.load(open(fname, 'r'))

# Library helpers
def save_library():
    write_list_to_file(library, library_file)
    load_library()

def load_library():
    global library 
    try:
        library = read_list_from_file(library_file)
    except:
        library = create_library()

def create_library():
    global library
    library = []
    catalog = get_latest_catalog()
    save_catalog(catalog)
    update_library_with(catalog)
    return library

def update_library_with(items):
    for item in items:
        book = find_by_id(item['id'])
        if len(book) > 0:
            for key in item.keys():
                book[key] = item[key]
        else:
            item['status'] = 3
            library.append(item)
    save_library()


# Catalog helpers
def save_catalog(obj):
    write_list_to_file(obj, catalog_file)

def load_catalog():
    try:
        catalog = read_list_from_file(catalog_file)
    except:
        catalog = []
    return catalog

