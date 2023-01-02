import os
import re
import datetime
import pytz

from interfaces import airtable
from pyairtable import utils

AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_SERVICES_TABLE_ID = os.environ["AIRTABLE_SERVICES_TABLE_ID"]

AIRTABLE_MAP = {
    "churchsuite_category_id": "ChurchSuite Category ID",
    "churchsuite_id": "ChurchSuite ID",
    "churchsuite_image": "ChurchSuite Image",
    "churchsuite_public_identifier": "ChurchSuite public identifier",
    "datetime": "Date & time",
    "location": "Location",
    "fee_payable": "Fee payable?",
    "has_oos": "Has order of service?",
    "liturgical_name": "Liturgical name",
    "name": "Name",
    "oos_id": "Order of Service ID",
    "podcast_id": "Podcast ID",
    "slug": "Slug",
    "stream_public": "Stream public?",
    "streaming": "Streaming?",
    "technician": "Technician",
    "type": "Type",
    "wp_image_id": "Wordpress featured image ID",
    "wp_image_last_uploaded_name": "Last uploaded Wordpress image name",
    "youtube_id": "YouTube ID",
    "youtube_image_last_uploaded_name": "Last uploaded YouTube thumbnail name",
}

YOUTUBE_DEFAULT_PLAYLIST_ID = "PLQl3S_pmB65sll8wZSQY-c5BXFzrygV1P"

CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES = {
    "9": {
        "default_thumbnail": "wedding.jpg",
        "exclude_youtube_playlists": {YOUTUBE_DEFAULT_PLAYLIST_ID},
    },
    "10": {
        "default_thumbnail": "funeral.jpg",
        "exclude_youtube_playlists": {YOUTUBE_DEFAULT_PLAYLIST_ID},
    },
    "34": {
        "default_thumbnail": "evensong.jpg",
        "default_featured_image_id": "6899",
        "describe_service_as": "service of Choral Evensong",
        "show_bcp_reproduction_notice": True,
        "youtube_playlists": {"PLQl3S_pmB65s3xbLEPgxkm9y-96UY6NrA"},
    },
    "35": {
        "default_thumbnail": "compline.jpg",
        "default_featured_image_id": "9435",
        "describe_service_as": "service of compline",
        "youtube_playlists": {"PLQl3S_pmB65smkQbbFoGSITxQVtuqKXu3"},
    },
}

TZ_GMT = pytz.timezone("Etc/GMT")
TZ_LONDON = pytz.timezone("Europe/London")


def upcoming_streaming_services():

    return airtable.services_table().all(
        formula="AND({"
        + AIRTABLE_MAP["datetime"]
        + "} >= TODAY(),{"
        + AIRTABLE_MAP["streaming"]
        + "} = 'Yes')",
        sort=[AIRTABLE_MAP["datetime"]],
    )


def upcoming_services_with_oos():

    return airtable.services_table().all(
        formula="AND({"
        + AIRTABLE_MAP["datetime"]
        + "} >= TODAY(),{"
        + AIRTABLE_MAP["has_oos"]
        + "} = TRUE())",
        sort=[AIRTABLE_MAP["datetime"]],
    )


def upcoming_services_with_undecided_stream_status():
    return airtable.services_table().all(
        formula="AND({"
        + AIRTABLE_MAP["datetime"]
        + "} >= TODAY(),{"
        + AIRTABLE_MAP["streaming"]
        + "} = '')",
        sort=[AIRTABLE_MAP["datetime"]],
    )


class Service:
    def __init__(self, airtable_object):
        self.id = airtable_object["id"]
        self.airtable_fields = airtable_object["fields"]

        if self.churchsuite_category_id in CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES:

            self.category_overrides = CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES[
                self.churchsuite_category_id
            ]

        else:

            self.category_overrides = {}

    @property
    def datetime_field(self):
        return self.airtable_fields[AIRTABLE_MAP["datetime"]]

    @property
    def name_field(self):
        return self.airtable_fields[AIRTABLE_MAP["name"]]

    @property
    def slug(self):
        return self.airtable_fields[AIRTABLE_MAP["slug"]]

    @property
    def type_field(self):
        return self.airtable_fields[AIRTABLE_MAP["type"]]

    @property
    def liturgical_name_field(self):
        return self.airtable_fields.get(AIRTABLE_MAP["liturgical_name"])

    @property
    def technician_field(self):
        return self.airtable_fields.get(AIRTABLE_MAP["technician"])

    @property
    def churchsuite_category_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["churchsuite_category_id"])

    @property
    def churchsuite_image_field(self):
        return self.airtable_fields.get(AIRTABLE_MAP["churchsuite_image"])

    @property
    def order_of_service_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["oos_id"])

    @property
    def podcast_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["podcast_id"])

    @property
    def wordpress_image_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["wp_image_id"])

    @property
    def wordpress_image_last_uploaded_name(self):
        return self.airtable_fields.get(AIRTABLE_MAP["wp_image_last_uploaded_name"])

    @property
    def youtube_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["youtube_id"])

    @property
    def youtube_image_last_uploaded_name(self):
        return self.airtable_fields.get(
            AIRTABLE_MAP["youtube_image_last_uploaded_name"]
        )

    @property
    def datetime(self):
        return TZ_GMT.localize(
            utils.datetime_from_iso_str(self.datetime_field)
        ).astimezone(TZ_LONDON)

    @property
    def datetime_as_naive_string(self):
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def datetime_to_publish_order_of_service(self):
        return self.datetime - datetime.timedelta(days=1)

    @property
    def location(self):
        return self.airtable_fields.get(AIRTABLE_MAP["location"])

    @property
    def technician_name(self):
        if self.technician_field:
            return self.airtable_fields.get(AIRTABLE_MAP["technician"])["name"]

        return None

    @property
    def streaming_field(self):
        return self.airtable_fields.get(AIRTABLE_MAP["streaming"])

    @property
    def is_streaming(self):
        if self.streaming_field and self.streaming_field == "Yes":
            return True

        return False

    @property
    def is_stream_public(self):
        if self.airtable_fields.get(AIRTABLE_MAP["stream_public"]):
            return True

        return False

    @property
    def has_oos(self):
        if self.airtable_fields.get(AIRTABLE_MAP["has_oos"]):
            return True

        return False

    @property
    def is_fee_payable(self):
        if self.airtable_fields.get(AIRTABLE_MAP["fee_payable"]):
            return True

        return False

    @property
    def title_string(self):

        title_string = (
            self.liturgical_name_field
            if self.liturgical_name_field
            else self.name_field
        )

        # This is a hack to force a capital on the first letter of the first word, but leave the rest of the string intact.
        return title_string[:1].upper() + title_string[1:]

    @property
    def title_string_with_date(self):

        return self.title_string + ": {date}".format(
            date=self.datetime.strftime("%-d %B %Y"),
        )

    @property
    def described_as(self):

        if "describe_service_as" in self.category_overrides:
            return self.category_overrides["describe_service_as"]

        if re.search("sung eucharist", self.name_field, re.IGNORECASE):
            return "sung Eucharist"

        return "service"

    @property
    def description(self):
        if self.liturgical_name_field:
            liturgical_name_description_string = " for {}".format(
                self.liturgical_name_field
            )
        else:
            liturgical_name_description_string = ""

        if self.location:
            service_location = self.location
        else:
            service_location = "St Mary's Church, Whitkirk"

        return "A {service_description} streamed live from {service_location}{liturgical_string}.".format(
            service_description=self.described_as,
            service_location=service_location,
            liturgical_string=liturgical_name_description_string,
        )

    @property
    def service_data(self):

        return {
            "url": "https://airtable.com/{base_id}/{table_id}/{item_id}".format(
                base_id=AIRTABLE_BASE_ID,
                table_id=AIRTABLE_SERVICES_TABLE_ID,
                item_id=self.id,
            ),
            "title": self.name_field,
            "type": self.type_field,
            "datetime": self.datetime.strftime("%A %-d %B %Y at %-I.%M %p"),
            "technician": self.technician_name,
            "streaming": self.is_streaming,
            "fee_payable": self.is_fee_payable,
        }

    def datetime_to_publish_order_of_service_given_previous_service(
        self, previous_service=None
    ):

        if previous_service:
            return max(
                self.datetime_to_publish_order_of_service,
                previous_service.datetime + datetime.timedelta(hours=1),
            )

        return self.datetime_to_publish_order_of_service

    @property
    def has_category_behaviour_overrides(self):
        if self.churchsuite_category_id in CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES:
            return True
        return False

    @property
    def category_behaviour_overrides(self):
        if self.has_category_behaviour_overrides:
            return CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES[
                self.churchsuite_category_id
            ]
        return None

    @property
    def youtube_playlists_for_service(self):
        playlists = {
            YOUTUBE_DEFAULT_PLAYLIST_ID,
        }

        if self.has_category_behaviour_overrides:

            if "youtube_playlists" in self.category_behaviour_overrides:
                playlists = playlists.union(
                    self.category_behaviour_overrides["youtube_playlists"]
                )

            if "exclude_youtube_playlists" in self.category_behaviour_overrides:
                playlists = playlists.difference(
                    self.category_behaviour_overrides["exclude_youtube_playlists"]
                )

        return playlists

    @property
    def youtube_is_embeddable(self):
        if self.is_stream_public:
            return True
        else:
            return False

    @property
    def youtube_privacy(self):
        if self.is_stream_public:
            return "public"
        else:
            return "unlisted"
