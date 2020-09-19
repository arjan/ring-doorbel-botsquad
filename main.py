""""
Poll for latest Ring movie and broadcast it to a botsquad bot
"""

import json
import getpass
from pathlib import Path
from datetime import datetime, timezone
import time
import os
import requests
import logging

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

logging.basicConfig(level=logging.INFO)


def initialize_ring():
    cache_file = Path("token.cache")
    def token_updated(token):
        cache_file.write_text(json.dumps(token))


    def otp_callback():
        auth_code = input("2FA code: ")
        return auth_code

    if cache_file.is_file():
        auth = Auth("CamBot/1.0", json.loads(cache_file.read_text()), token_updated)
    else:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        auth = Auth("CamBot/1.0", None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, otp_callback())

    ring = Ring(auth)
    ring.update_data()
    return ring

def download_file(url, local_filename):
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def main():
    """ Poll the ring device and check for the last ding """
    ring = initialize_ring()
    devices = ring.devices()
    device = devices['doorbots'][0]
    logging.info("Using RING device: " + str(device))

    last_event = None

    while True:
        now = datetime.now(timezone.utc)
        event = None
        time.sleep(2)

        for event in device.history(limit=10, kind='ding'):
            break
        if not event or (type(last_event) == dict and event['id'] != last_event['id']):
            logging.debug("No events found...")
            continue

        delta = int((now - event['created_at']).total_seconds())
        if delta > 300:
            logging.debug("Too long since this event, skipping")
            continue

        snapshot_file = "/tmp/recording-%s.gif" % event['id']
        movie_file = "/tmp/recording-%s.mp4" % event['id']

        if os.path.exists(snapshot_file):
            logging.debug("Already processed this event")
            continue

        try:
            logging.info("Getting recording URL...")
            url = device.recording_url(event['id'])
            logging.info("Downloading...")
            download_file(url, movie_file)

            cmdline = "ffmpeg -t 3 -i %s -vf 'fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse' -loop 0 %s" % (movie_file, snapshot_file)
            logging.info("Converting...")
            os.system(cmdline)
        except Exception as e:
            logging.error(e)
            continue

        logging.info("Created: " + snapshot_file)
        last_event = event

        # break

if __name__ == "__main__":
    main()
