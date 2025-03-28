import datetime
import os
import re
import urllib.request
from http.client import HTTPMessage
from typing import Any, NotRequired, Optional, TypedDict

import pytz
from pyairtable import utils

from interfaces import airtable

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
    "cancelled": "Cancelled?",
}

YOUTUBE_DEFAULT_PLAYLIST_ID = "PLQl3S_pmB65sll8wZSQY-c5BXFzrygV1P"

DEFAULT_SERVICE_IMAGE = "images/default_thumbnails/service.jpg"


class CategoryOverridesDict(TypedDict):
    default_thumbnail: NotRequired[str]
    youtube_playlists: NotRequired[set[str]]
    exclude_youtube_playlists: NotRequired[set[str]]
    default_featured_image_id: NotRequired[str]
    describe_service_as: NotRequired[str]
    show_bcp_reproduction_notice: NotRequired[bool]


CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES: dict[str, CategoryOverridesDict] = {
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


airtable_fields_dict = dict[str, Any]
airtable_field_map_dict = dict[str, str]


class AirtableObjectDict(TypedDict):
    id: str
    fields: airtable_fields_dict


class AirtableEntity:
    airtable_object: AirtableObjectDict
    airtable_map: airtable_field_map_dict

    def airtable_field_exists(self, field: str) -> bool:
        return field in self.airtable_object["fields"]

    def get_airtable_field(self, field: str) -> Any:
        return self.airtable_object["fields"].get(field)

    def mapped_field_name(self, field: str) -> str:
        return self.airtable_map[field]

    def mapped_airtable_field_exists(self, field: str) -> bool:
        if field in self.airtable_map:
            return self.airtable_field_exists(self.mapped_field_name(field))
        return False

    def get_mapped_airtable_field(self, field: str) -> Any:
        return self.get_airtable_field(self.mapped_field_name(field))

    @property
    def airtable_id(self) -> str:
        return self.airtable_object["id"]


class ServiceDataDict(TypedDict):
    url: str
    type: str
    title: str
    datetime: str
    technician: Optional[str]
    streaming: bool
    fee_payable: bool


class Service(AirtableEntity):
    category_overrides: CategoryOverridesDict

    def __init__(self, airtable_object: AirtableObjectDict) -> None:
        self.id = airtable_object["id"]

        self.airtable_map = AIRTABLE_MAP
        self.airtable_object = airtable_object
        self.airtable_fields = airtable_object["fields"]

        if self.churchsuite_category_id in CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES:
            self.category_overrides = CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES[
                self.churchsuite_category_id
            ]

        else:
            self.category_overrides = {}

    @property
    def datetime_field(self) -> str:
        return self.get_mapped_airtable_field("datetime")

    @property
    def name_field(self) -> str:
        return self.get_mapped_airtable_field("name")

    @property
    def slug(self) -> str:
        return self.get_mapped_airtable_field("slug")

    @property
    def type_field(self) -> str:
        return self.get_mapped_airtable_field("type")

    @property
    def liturgical_name_field(self) -> str:
        return self.get_mapped_airtable_field("liturgical_name")

    @property
    def technician_field(self) -> str:
        return self.get_mapped_airtable_field("technician")

    @property
    def churchsuite_category_id(self) -> str:
        return self.get_mapped_airtable_field("churchsuite_category_id")

    @property
    def churchsuite_image_field(self) -> list:
        return self.get_mapped_airtable_field("churchsuite_image")

    @property
    def order_of_service_id(self) -> str:
        return self.get_mapped_airtable_field("oos_id")

    @property
    def podcast_id(self) -> str:
        return self.get_mapped_airtable_field("podcast_id")

    @property
    def wordpress_image_id(self) -> str:
        return self.get_mapped_airtable_field("wp_image_id")

    @property
    def wordpress_image_last_uploaded_name(self) -> str:
        return self.get_mapped_airtable_field("wp_image_last_uploaded_name")

    @property
    def youtube_id(self) -> str:
        return self.get_mapped_airtable_field("youtube_id")

    @property
    def youtube_image_last_uploaded_name(self) -> str:
        return self.get_mapped_airtable_field("youtube_image_last_uploaded_name")

    @property
    def datetime_localised(self) -> datetime.datetime:
        return TZ_GMT.localize(
            utils.datetime_from_iso_str(self.datetime_field)
        ).astimezone(TZ_LONDON)

    @property
    def datetime_as_naive_string(self) -> str:
        return self.datetime_localised.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def datetime_to_publish_order_of_service(self) -> datetime.datetime:
        return self.datetime_localised - datetime.timedelta(days=1)

    @property
    def location(self) -> str:
        return self.get_mapped_airtable_field("location")

    @property
    def technician_name(self) -> Optional[str]:
        if self.mapped_airtable_field_exists("technician"):
            return self.get_mapped_airtable_field("technician")["name"]

        return None

    @property
    def streaming_field(self) -> str:
        return self.get_mapped_airtable_field("streaming")

    @property
    def is_streaming(self) -> bool:
        if (
            self.mapped_airtable_field_exists("streaming")
            and self.get_mapped_airtable_field("streaming") == "Yes"
        ):
            return True

        return False

    @property
    def is_stream_public(self) -> bool:
        if self.mapped_airtable_field_exists("stream_public"):
            return True

        return False

    @property
    def has_oos(self) -> bool:
        if self.mapped_airtable_field_exists("has_oos"):
            return True

        return False

    @property
    def is_fee_payable(self) -> bool:
        if self.mapped_airtable_field_exists("fee_payable"):
            return True

        return False

    @property
    def title_string(self) -> str:
        title_string = (
            self.liturgical_name_field
            if self.liturgical_name_field
            else self.name_field
        )

        # This is a hack to force a capital on the first letter of the first word, but leave the rest of the string intact.
        return title_string[:1].upper() + title_string[1:]

    @property
    def title_string_with_date(self) -> str:
        return self.title_string + ": {date}".format(
            date=self.datetime_localised.strftime("%-d %B %Y"),
        )

    @property
    def described_as(self) -> str:
        if "describe_service_as" in self.category_overrides:
            return self.category_overrides["describe_service_as"]

        if re.search("sung eucharist", self.name_field, re.IGNORECASE):
            return "sung Eucharist"

        return "service"

    @property
    def description(self) -> str:
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
    def service_data(self) -> ServiceDataDict:
        return {
            "url": "https://airtable.com/{base_id}/{table_id}/{item_id}".format(
                base_id=AIRTABLE_BASE_ID,
                table_id=AIRTABLE_SERVICES_TABLE_ID,
                item_id=self.id,
            ),
            "title": self.name_field,
            "type": self.type_field,
            "datetime": self.datetime_localised.strftime("%A %-d %B %Y at %-I.%M %p"),
            "technician": self.technician_name,
            "streaming": self.is_streaming,
            "fee_payable": self.is_fee_payable,
        }

    @property
    def has_service_specific_image(self) -> bool:
        return bool(self.churchsuite_image_field)

    @property
    def has_category_specific_image(self) -> bool:
        return (
            self.has_category_behaviour_overrides
            and "default_thumbnail" in self.category_behaviour_overrides
        )

    @property
    def service_image(self) -> str:
        # Service-specific image squashes category defaults
        if self.has_service_specific_image:
            image_data = self.churchsuite_image_field[0]
            image_url = image_data["url"]
            image_save_location, _ = download_service_image(
                image_url, image_data["filename"]
            )

            return image_save_location

        # Category defaults squash master default image
        if self.has_category_specific_image:
            return "images/default_thumbnails/{}".format(
                self.category_behaviour_overrides["default_thumbnail"]
            )

        # Fall back to the default
        return DEFAULT_SERVICE_IMAGE

    def datetime_to_publish_order_of_service_given_previous_service(
        self, previous_service: Optional["Service"] = None
    ) -> datetime.datetime:
        if previous_service:
            return max(
                self.datetime_to_publish_order_of_service,
                previous_service.datetime_localised + datetime.timedelta(hours=1),
            )

        return self.datetime_to_publish_order_of_service

    @property
    def has_category_behaviour_overrides(self) -> bool:
        if self.churchsuite_category_id in CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES:
            return True
        return False

    @property
    def category_behaviour_overrides(self) -> CategoryOverridesDict:
        if self.has_category_behaviour_overrides:
            return CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES[
                self.churchsuite_category_id
            ]
        return {}

    @property
    def youtube_playlists_for_service(self) -> set[str]:
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
    def youtube_is_embeddable(self) -> bool:
        if self.is_stream_public:
            return True
        else:
            return False

    @property
    def youtube_privacy(self) -> str:
        if self.is_stream_public:
            return "public"
        else:
            return "unlisted"


def upcoming_streaming_services() -> list[Service]:
    return [
        Service(service)
        for service in airtable.services_table().all(
            formula="AND({"
            + AIRTABLE_MAP["datetime"]
            + "} >= TODAY(),{"
            + AIRTABLE_MAP["streaming"]
            + "} = 'Yes')",
            sort=[AIRTABLE_MAP["datetime"]],
        )
    ]


def upcoming_services_with_oos() -> list[Service]:
    return [
        Service(service)
        for service in airtable.services_table().all(
            formula="AND({"
            + AIRTABLE_MAP["datetime"]
            + "} >= TODAY(),{"
            + AIRTABLE_MAP["has_oos"]
            + "} = TRUE())",
            sort=[AIRTABLE_MAP["datetime"]],
        )
    ]


def upcoming_services_with_undecided_stream_status() -> list[Service]:
    return [
        Service(service)
        for service in airtable.services_table().all(
            formula="AND({"
            + AIRTABLE_MAP["datetime"]
            + "} >= TODAY(),{"
            + AIRTABLE_MAP["streaming"]
            + "} = '')",
            sort=[AIRTABLE_MAP["datetime"]],
        )
    ]


def download_service_image(url: str, filename: str) -> tuple[str, HTTPMessage]:
    image_save_location = "images/service_specific/{}".format(filename)
    return urllib.request.urlretrieve(url, image_save_location)
