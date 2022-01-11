# St Mary's Church Whitkirk Comms Team Utilities

Some useful things to make the lives of the Comms Team a bit easier.

## Import from ChurchSuite

Pulls events from ChurchSuite's featured events feed and tries to sync them up with Airtable.

`$ bin/comms-utils import-from-churchsuite`

## Send summary email

Pulls items from Airtable to talk about, and sends a summary email to the Comms Team. The `--send-email` flag is necessary to actually send an email, otherwise the default behaviour is a dry run (see below).

`$ bin/comms-utils send-report --send-email`

### Dry run

If you're doing development, you can use the `--dry-run` flag to output the email's HTML to file (`email.html`) instead of sending the email.

`$ bin/comms-utils send-report --dry-run`