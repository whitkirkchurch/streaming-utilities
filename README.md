# St Mary's Church Whitkirk Streaming Summary Robot

A useful tool to make the lives of the service streaming a bit easier.

## Send summary email

Pulls services from Airtable to notify people about, and sends a summary email to the streaming team. The `--send-email` flag is necessary to actually send an email, otherwise the default behaviour is a dry run (see below).

`$ bin/send-streaming-reminder --send-email`

### Dry run

If you're doing development, you can use the `--dry-run` flag to output the email's HTML to file (`email.html`) instead of sending the email.

`$ bin/send-streaming-reminder --dry-run`