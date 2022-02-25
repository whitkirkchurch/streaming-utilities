import re

from pyairtable import utils


AIRTABLE_MAP = {
    "churchsuite_category_id": "ChurchSuite Category ID",
    "datetime": "Date & time",
    "fee_payable": "Fee payable?",
    "liturgical_name": "Liturgical name",
    "name": "Name",
    "oos_id": "Order of Service ID",
    "slug": "Slug",
    "stream_public": "Stream public?",
    "streaming": "Streaming?",
    "technician": "Technician",
    "type": "Type",
    "youtube_id": "YouTube ID",
}


class Service:
    def __init__(self, airtable_object):
        self.id = airtable_object["id"]
        self.airtable_fields = airtable_object["fields"]

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
    def order_of_service_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["oos_id"])

    @property
    def youtube_id(self):
        return self.airtable_fields.get(AIRTABLE_MAP["youtube_id"])

    @property
    def datetime(self):
        return utils.datetime_from_iso_str(self.datetime_field)

    @property
    def technician_name(self):
        if self.technician_field:
            return self.airtable_fields.get(AIRTABLE_MAP["technician"])["Name"]

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

        return "A {service_description} streamed live from St Mary's Church, Whitkirk{liturgical_string}.".format(
            service_description=self.described_as,
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
