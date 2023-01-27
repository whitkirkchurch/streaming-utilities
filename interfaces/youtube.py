import os

import boto3
import botocore
import click
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

GOOGLE_OAUTH_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"
GOOGLE_CREDENTIALS_FILE = "token.json"

AWS_S3_BUCKET_NAME = os.environ["AWS_S3_BUCKET_NAME"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET = os.environ["AWS_SECRET"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class Api:  # pragma: no cover
    def __init__(self):
        api_service_name = "youtube"

        api_version = "v3"

        creds = None
        # The file GOOGLE_CREDENTIALS_FILE stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.

        s3 = boto3.resource(
            "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET
        )
        bucket = s3.Bucket(AWS_S3_BUCKET_NAME)

        try:
            bucket.download_file(GOOGLE_CREDENTIALS_FILE, GOOGLE_CREDENTIALS_FILE)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                click.echo(click.style("Could not find credential file", fg="red"))
            else:
                # Something else has gone wrong.
                raise
        else:
            click.echo(click.style("Loaded credential file", fg="green"))
            creds = google.oauth2.credentials.Credentials.from_authorized_user_file(
                GOOGLE_CREDENTIALS_FILE, GOOGLE_OAUTH_SCOPES
            )

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            else:
                bucket.download_file(
                    GOOGLE_CLIENT_SECRET_FILE, GOOGLE_CLIENT_SECRET_FILE
                )
                flow = (
                    google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        GOOGLE_CLIENT_SECRET_FILE, GOOGLE_OAUTH_SCOPES
                    )
                )
                creds = flow.run_console()
            # Save the credentials for the next run
            with open(GOOGLE_CREDENTIALS_FILE, "w") as token:
                token.write(creds.to_json())

        # Send the new/updated token back to S3
        bucket.upload_file(GOOGLE_CREDENTIALS_FILE, GOOGLE_CREDENTIALS_FILE)

        self.client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=creds
        )


class Playlist:

    videos_in_list = []

    def __init__(self, youtube, playlist_id):
        self.youtube = youtube
        self.playlist_id = playlist_id

        self.load_list_items()

    def load_list_items(self, pagination_token=None):

        items_to_load = True
        video_list = []

        while items_to_load:

            request = self.youtube.client.playlistItems().list(
                part="snippet",
                maxResults=50,
                playlistId=self.playlist_id,
                pageToken=pagination_token,
            )

            response = request.execute()

            for item in response["items"]:
                resource = item["snippet"]["resourceId"]

                if resource["kind"] == "youtube#video":
                    video_list.append(resource["videoId"])

            if "nextPageToken" in response:
                pagination_token = response["nextPageToken"]
            else:
                items_to_load = False

        self.videos_in_list = video_list

    @property
    def items(self):
        return self.videos_in_list


class PlaylistManager:

    playlists = {}

    def __init__(self):

        self.youtube = Api()

    def get(self, playlist_id):
        if playlist_id not in self.playlists:

            self.playlists[playlist_id] = Playlist(self.youtube, playlist_id)

        return self.playlists[playlist_id]


def video_in_playlist(video_id, playlist_id):
    playlist = PlaylistManager().get(playlist_id)

    click.echo(click.style(f"Checking if {video_id} in {playlist_id}", fg="blue"))

    return video_id in playlist.items
