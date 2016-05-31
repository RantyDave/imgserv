# Copyright David Preece (2016), CDDL license
# With great thanks to Ira Cooper https://github.com/ilc/imgserv (LICENSE included in repo)
# Set up with 'pip install bottle requests'

# Put the server:port this is running on into imgadm sources...
# imgadm sources -a http://whatever.com:6502

import os
import re
import logging
import datetime
import requests
from bottle import get, post, put, delete, run, response, HTTPError, request
try:
    import json
except ImportError:
    import simplejson as json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-11s %(levelname)-8s %(message)s',
                    datefmt='%m%d%H%M%S')


def is_uuid(uuid):
    return re.search("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", uuid) is not None


def get_images():
    imgs = []
    for filename in os.listdir("."):
        if os.path.isfile(filename[:-5]+".json") and os.path.isfile(filename[:-5]+".zfs.bz2"):
            imgs += (filename[:-5],)
    return imgs


def manifest_for(uuid):
    return json.load(open(uuid+".json", 'r'))

# ----------------Getting


@get('/ping')
def index():
    return {"ping": "pong", "version": "1.0.0", "imgapi": True}


@get('/images')
def index():
    response.content_type='application/json'
    return json.dumps(map(manifest_for,get_images()))


@get('/images/:uuid')
def index(uuid):
    if not is_uuid(uuid):
        return HTTPError(status=404)
    if not os.path.isfile(uuid+".json"):
        r = requests.get('https://images.joyent.com/images/'+uuid)
        if r.status_code != 200:
            return HTTPError(status=r.status_code)
        return r.text
    return manifest_for(uuid)


@get('/images/:uuid/file')
def index(uuid):
    if not is_uuid(uuid):
        return HTTPError(status=404)
    if not os.path.isfile(uuid+".zfs.bz2"):
        return HTTPError(status=404)
    logging.info("Sending file for UUID=" + uuid)
    response.headers['Content-Length'] = os.stat(uuid+".zfs.bz2").st_size
    return open(uuid+".zfs.bz2", 'r')

# ----------------Putting


@post('/images/:uuid')
def create_image_record(uuid):
    if not is_uuid(uuid):
        return HTTPError(status=400, body="Passed UUID is not a UUID")
    if 'action' not in request.params:
        return HTTPError(status=400, body="Missing action parameter")
    if request.params['action'] == 'activate':
        return activate_image_record(uuid)
    if request.params['action'] != 'import':
        return HTTPError(status=400, body="Unknown action parameter")

    manifest = json.loads(request.body.getvalue())
    try:
        manifest['name']
        manifest['owner']
        manifest['version']
        manifest['type']
        manifest['os']
        manifest['uuid']
    except KeyError:
        return HTTPError(status=400, body="Incomplete request, see https://images.joyent.com/docs/#CreateImage")
    if not is_uuid(manifest['uuid']):
        return HTTPError(status=400, body="Passed UUID is not a UUID")
    if uuid != manifest['uuid']:
        return HTTPError(status=400, body="Manifest UUID and query UUID are not identical")

    with open(manifest['uuid']+".json", "w") as f:
        f.write(json.dumps(manifest))
    logging.info("Created image record for UUID=" + uuid)


@put('/images/:uuid/file')
def receive(uuid):
    if not is_uuid(uuid):
        return HTTPError(status=400, body="Passed UUID is not a UUID")

    logging.info("Receiving file for UUID=" + uuid)
    stream_inwards = request['wsgi.input']
    remaining = request.content_length
    with open(uuid+".zfs.bz2", "w") as f:
        while remaining > 0:
            block = stream_inwards.read(remaining if remaining < 131072 else 131072)
            f.write(block)
            remaining -= 131072

    return manifest_for(uuid)


def activate_image_record(uuid):  # UUID is checked above
    try:
        os.stat(uuid+'.zfs.bz2')
    except OSError:
        return HTTPError(status=400, body="Tried to activate an image before it's uploaded")

    try:
        manifest = manifest_for(uuid)
    except OSError:
        return HTTPError(status=400, body="Image not found")

    manifest['state'] = 'active'
    manifest['disabled'] = False
    manifest['public'] = True
    manifest['published_at'] = datetime.datetime.utcnow().isoformat()+'Z'

    with open(uuid+".json", "w") as f:
        f.write(json.dumps(manifest))
    logging.info("Activated image record for UUID=" + uuid)
    return manifest


@delete('/images/:uuid')
def delete(uuid):
    if not is_uuid(uuid):
        return HTTPError(status=400, body="Passed UUID is not a UUID")
    logging.info("Deleting " + uuid)
    os.remove(uuid+".json")
    os.remove(uuid+".zfs.bz2")


run(host='0.0.0.0', port=6502)
