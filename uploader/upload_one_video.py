#!/usr/bin/python

import argparse
# import httplib
import http.client
import httplib2
import os
import random
import time
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient import _auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
from oauth2client.client import OAuth2Credentials

httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = 'client_secrets.json'
AUTHENTICATED_SERVICE_FILE = 'authenticated_youtube.json'

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')


def read_credentials(fname):
    """Reads JSON with credentials from file."""
    if os.path.isfile(fname):
        with open(fname, "r") as file:

            credentials = OAuth2Credentials.from_json(file.read())
    else:
        credentials = None

    return credentials


def write_credentials(fname, credentials):
    """Writes credentials as JSON to file."""
    with open(fname, 'w') as file:
        print(credentials.__dict__.keys())
        # json_file += credentials.json

        file.write('{"access_token":"' + credentials.token + '", ')
        file.write('"token_expiry":"' + str(credentials.expiry) + '", ')  # datetime
        file.write('"scopes":"' + str(credentials._scopes) + '", ')  # list
        file.write('"refresh_token":"' + credentials._refresh_token + '", ')
        file.write('"id_token":"' + str(credentials._id_token) + '", ')  # nonetype
        file.write('"token_uri":"' + credentials._token_uri + '", ')
        file.write('"client_id":"' + credentials._client_id + '", ')
        file.write('"user_agent":"", ')
        file.write('"invalid":"", ')

        file.write('"client_secret":"' + credentials._client_secret + '"}')


# Authorize the request and store authorization credentials.

def get_authenticated_service(auth_root):
    auth_name = os.path.join(auth_root, AUTHENTICATED_SERVICE_FILE)
    secrets_name = os.path.join(auth_root, CLIENT_SECRETS_FILE)
    if os.path.isfile(auth_name):
        credentials = read_credentials(auth_name)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(secrets_name, SCOPES)
        credentials = flow.run_console()
        write_credentials(auth_name, credentials)

    # The credentials need to be scoped.
    credentials = _auth.with_scopes(credentials, SCOPES)

    # Create an authorized http instance
    http = _auth.authorized_http(credentials)

    # return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    return build(API_SERVICE_NAME, API_VERSION, http=http)


def perform_upload(youtube, options):
    # print(str(options))
    tags = None
    if options.keywords:
        tags = options.keywords.split(',')

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting 'chunksize' equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request):
    response = None
    error = None
    retry = 0
    result_id = None
    # We want to quit the loop (but not 'exit' the code) if any one of the following occur
    # - we get a response
    # - we get a non-retriable error (a 'fatal' error)
    # - we exceed   our max retries
    # TODO: The logic of this loop is now a bit messed up and needs tidying to make it clearer
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' % response['id'])
                    result_id = response['id']
                else:
                    print('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
            else:
                # Do this so we force quit the loop
                # TODO: Need to tidy the logic
                response = 'Fatal error'
                print('A non-retriable HTTP error %d occurred\n%s' % (e.resp.status, e.content))
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred:\n%s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                # Do this so we force quit the loop
                # TODO: Need to tidy the logic
                response = 'Retries exceeded'
                print('No longer attempting to retry.')
            else:
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print('Sleeping %f seconds and then retrying...' % sleep_seconds)
                time.sleep(sleep_seconds)
            error = None
    return result_id


def upload_video(youtube_service, args):
    youtube_id = None
    e = None
    try:
        youtube_id = perform_upload(youtube_service, args)
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    return youtube_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Video file to upload')
    parser.add_argument('--title', help='Video title', default='Test Title')
    parser.add_argument('--description', help='Video description',
                        default='Test Description')
    parser.add_argument('--category', default='22',
                        help='Numeric video category. ' +
                             'See https://developers.google.com/youtube/v3/docs/videoCategories/list')
    parser.add_argument('--keywords', help='Video keywords, comma separated',
                        default='')
    parser.add_argument('--privacyStatus', choices=VALID_PRIVACY_STATUSES,
                        default='private', help='Video privacy status.')
    parser.add_argument('--auth_root', required=True, help='Auth directory')
    args = parser.parse_args()

    # print(str(args))

    youtube = get_authenticated_service()
    # with open('../../yt.json', 'w') as file:
    #  file.write(youtube)

    upload_video(youtube, args)
