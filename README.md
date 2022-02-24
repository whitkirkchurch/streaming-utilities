# St Mary's Church Whitkirk Streaming Utilities

A collection of useful utilities which make the lives of our streaming team easier, by automating a bunch of stuff we used to do manually.

## Import from ChurchSuite

Check our upcoming public services list from ChurchSuite (ie events which are in one of the service categories listed in `CHURCHSUITE_CATEGORIES_TO_SYNC`, and which are visible for embedding) and import to Airtable. Creates new or updates where needed.

`$ bin/streaming-utilities import-from-churchsuite`

## Send summary email

Pulls services from Airtable to notify people about, and sends a summary email to the streaming team. The `--send-email` flag is necessary to actually send an email, otherwise the default behaviour is a dry run (see below).

`$ bin/streaming-utilities send-report --send-email`

### Dry run

If you're doing development, you can use the `--dry-run` flag to output the email's HTML to file (`email.html`) instead of sending the email.

`$ bin/send-streaming-reminder send-report --dry-run`

## Sync with YouTube

Push the upcoming services to YouTube. You'll need to authenticate with Google to make this happen.

`$ bin/streaming-utilities sync-with-youtube --update`

### Preview

If you use `--preview` instead of `--update`, the script won't actually hit the YouTube API.

## Sync with Wordpress

Synchronise upcoming service metadata with Wordpress, creating new posts as necessary.

`$ bin/streaming-utilities sync-with-wordpress --update`

### Preview

If you use `--preview` instead of `--update`, the script won't actually perform content updates.