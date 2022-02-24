import re

from pyairtable import utils


AIRTABLE_MAP = {
    "datetime": "Date & time",
    "liturgical_name": "Liturgical name",
    "name": "Name",
    "slug": "Slug",
}


class Service:
    def __init__(self, airtable_object):
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
    def liturgical_name_field(self):
        return self.airtable_fields.get(AIRTABLE_MAP["liturgical_name"], None)

    @property
    def datetime(self):
        return utils.datetime_from_iso_str(self.datetime_field)

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
