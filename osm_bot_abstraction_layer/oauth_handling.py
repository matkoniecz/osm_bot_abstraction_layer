# from https://github.com/metaodi/osmapi/blob/develop/examples/oauth2_backend.py
# GPL-3.0 license by metaodi
# This script shows how to authenticate with OAuth2 with a backend application
# The token is saved to disk in $HOME/.osmapi/token.json
# It can be reused until it's revoked or expired.

# install oauthlib for requests:  pip install oauthlib requests-oauthlib
from requests_oauthlib import OAuth2Session
import json
import webbrowser
import osmapi
from dotenv import load_dotenv, find_dotenv
import os
import sys

def get_token(client_id, client_secret):
    # Credentials you get from registering a new application
    # register here: https://master.apis.dev.openstreetmap.org/oauth2/applications
    # or on production: https://www.openstreetmap.org/oauth2/applications

    # special value for redirect_uri for non-web applications
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

    authorization_base_url = "https://api.openstreetmap.org/oauth2/authorize"
    token_url = "https://www.openstreetmap.org/oauth2/token"
    scope = ["write_api", "write_notes"]

    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
    )

    login_url, _ = oauth.authorization_url(authorization_base_url)

    print(f"Authorize user using this URL: {login_url}")
    webbrowser.open(login_url)

    authorization_code = input("Paste the authorization code here: ")

    token = oauth.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code=authorization_code,
    )

    return token
