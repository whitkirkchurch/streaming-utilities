import os

from pyairtable import Table

AIRTABLE_API_KEY = os.environ["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]
AIRTABLE_SERVICES_TABLE_ID = os.environ["AIRTABLE_SERVICES_TABLE_ID"]


def services_table():
    return Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_SERVICES_TABLE_ID)
