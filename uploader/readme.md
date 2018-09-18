# Uploader

## Run this
`python3 upload_completed_videos.py --root /usr/local/src/pycon/videos`

This will repeatedly call the functions in `upload_one_video.py`.

The following files are not needed:
```
uploader_not_needed.py
```
## Requirements
### Python dependencies
`python3` with everything in `requirements.txt`, as shown below. *NOTE* There are some items that are *not* currently required, but if you `pip install requirements.txt` you will have everything you need.
```
beautifulsoup4==4.6.3
bs4==0.0.1
cachetools==2.1.0
certifi==2018.8.24
chardet==3.0.4
google-api-python-client==1.7.4
google-auth==1.5.1
google-auth-httplib2==0.0.3
google-auth-oauthlib==0.2.0
httplib2==0.11.3
idna==2.7
oauth2client==4.1.3
oauthlib==2.1.0
pyasn1==0.4.4
pyasn1-modules==0.2.2
requests==2.19.1
requests-oauthlib==1.0.0
rsa==3.4.2
six==1.11.0
uritemplate==3.0.0
urllib3==1.23

```

### File system
Uploader requires a root path to use for the uploader functions, for example
`/usr/local/src/pycon/videos/`

This directory will be created on first run, if it does not already exist.
The code will create several directories below this directory, as follows:
```
../auth
../ready_for_upload
../could_not_start_upload
../completed_upload
../failed_upload
```

All videos for uploading need to be placed into the `ready_for_upload` directory. Depending on the operation outcome, the file will be moved into one of the other three directories.
The `auth` directory is where you store the credentials files.

Currently, the program is looking for the `mp4` file extension. This can be changed in the code by changing `VIDEO_FILE_EXTENSION`.

### Program parameters
Only three parameters

`--root` *required* = an absolute path to the video file root, example `/usr/local/src/pycon/videos/`

`--category` = the Youtube category (default = `22`)

`--privacy` = the Youtube privacy setting (default = `private`) and you *must* change this if you want to upload directly as `public` 

## Program First Run and OAuth
On first run on a new machine, Google will go through the authorisation routine, as follows:
* The first part of the code will execute, using the `client_secrets.json` file in the `auth` directory.
* A url will be printed to `stdout`.
* Navigate to this url
* You will be prompted to log in to the PyCon Uk Video account if you are not already logged in.
* Google will ask which account to use: select the *BRAND* account *NOT* the email account.
* Google will ask for confirmation that you want to allow the program to access your account.
* Google will then provide an authorisation token.
* Copy this token from the browse and paste it into the terminal.
* The authorisation will complete, and write an `authenticated_youtube.json` file to `auth` for subsequent use.

## Video Upload
Then the program will continue and look for videos to upload:
* It makes a list of ready videos.
* It expects the first 4 characters of the file name to contain the id (case insensitive).
* For each video, it attempts to fetch the session metadata, using the id.
* If the session is a break, or does not exist, no session data is used, and the video is moved to the `could_not_start_upload` directory.
* For valid sessions, it formats the metadata and uploads the video.
* The video file is moved to either the `completed_upload` or `failed_upload` directory, depending on the outcome.
* The program attempts to retry if possible.
* Once the original list of files is exhausted, the program quits - it does not (yet) look for new files.

## Outputs
1. The video files are moved as described above. No files are deleted.
2. Various   status and progress messages are printed on `stdout`, but no log files are created (yet).
2. The Youtube video id *is* returned, and currently printed *only* to `stdout`. It is not saved anywhere (yet).

