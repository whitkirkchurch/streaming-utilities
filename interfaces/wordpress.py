import base64
import os
import urllib.request

import click
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from services import AIRTABLE_MAP

WORDPRESS_BASE_URL = "https://whitkirkchurch.org.uk"
WORDPRESS_USER = os.environ["WORDPRESS_USER"]
WORDPRESS_APPLICATION_PASSWORD = os.environ["WORDPRESS_APPLICATION_PASSWORD"]

WORDPRESS_DEFAULT_FEATURED_IMAGE_ID = os.environ["WORDPRESS_DEFAULT_FEATURED_IMAGE_ID"]

url = "{base_url}/wp-json/wp/v2/whitkirk_oos".format(base_url=WORDPRESS_BASE_URL)
media_url = "{base_url}/wp-json/wp/v2/media".format(base_url=WORDPRESS_BASE_URL)
podcast_url = "{base_url}/wp-json/wp/v2/podcast".format(base_url=WORDPRESS_BASE_URL)


def auth_header():
    user = WORDPRESS_USER
    password = WORDPRESS_APPLICATION_PASSWORD
    credentials = user + ":" + password
    token = base64.b64encode(credentials.encode())
    return {"Authorization": "Basic " + token.decode("utf-8")}


def create_or_update_oos_entry(
    service_object, previous_service, services_table, update
):
    # Establish service defaults

    service_image = None
    show_bcp_reproduction_notice = False
    featured_image_id = WORDPRESS_DEFAULT_FEATURED_IMAGE_ID

    # Apply category-specific overrides

    if service_object.has_category_behaviour_overrides:
        print("Overriding service defaults for category")

        if "default_featured_image_id" in service_object.category_behaviour_overrides:
            featured_image_id = service_object.category_behaviour_overrides[
                "default_featured_image_id"
            ]

        if (
            "show_bcp_reproduction_notice"
            in service_object.category_behaviour_overrides
        ):
            show_bcp_reproduction_notice = service_object.category_behaviour_overrides[
                "show_bcp_reproduction_notice"
            ]

    resource_body = {
        "title": service_object.title_string,
        "slug": service_object.slug,
        "date": service_object.datetime_to_publish_order_of_service_given_previous_service(
            previous_service
        ).isoformat(),
        "acf": {
            "datetime": service_object.datetime_as_naive_string,
            "physical": True,
            "show_bcp_reproduction_notice": show_bcp_reproduction_notice,
        },
        "excerpt": service_object.description,
    }

    if service_object.is_streaming:
        if service_object.youtube_id:
            resource_body["acf"]["youtube"] = service_object.youtube_id
            resource_body["acf"]["streamed"] = True
    else:
        resource_body["acf"]["streamed"] = False

    if service_object.wordpress_image_id:
        featured_image_id = service_object.wordpress_image_id

    if service_object.churchsuite_image_field:
        click.echo(click.style("Service-specific image found...", fg="blue"))
        image_data = service_object.churchsuite_image_field[0]
        image_url = image_data["url"]
        image_save_location = "images/service_specific/{}".format(
            image_data["filename"]
        )
        urllib.request.urlretrieve(image_url, image_save_location)

        service_image = image_save_location

    media_resource_body = {
        "title": "Featured image for {}".format(service_object.title_string_with_date),
    }

    if service_object.order_of_service_id:
        media_resource_body["post"] = service_object.order_of_service_id

    if featured_image_id:
        click.echo("Featured image known!")

        # Is this a service-specific image?
        if service_object.churchsuite_image_field:
            click.echo("Featured image is service-specific")

            # Get the resource metadata, so we can compare the filename

            last_uploaded_file = service_object.wordpress_image_last_uploaded_name
            image_filename_from_airtable = service_object.churchsuite_image_field[0][
                "filename"
            ]

            if last_uploaded_file == image_filename_from_airtable:
                # This is the same image idenfitier, so just poke the metadata
                click.echo("WP and CS identifiers for image match")
                if update:
                    requests.post(
                        media_url + "/{}".format(featured_image_id),
                        headers=auth_header(),
                        json=media_resource_body,
                    )
                else:
                    click.echo(
                        click.style(
                            "In preview mode, skipping metadata update",
                            fg="yellow",
                        )
                    )
            else:
                # This is a different image, nuke the old one and replace

                click.echo("Image has changed, replacing")

                fileName = os.path.basename(service_image)

                with open(service_image, "rb") as service_image_file:
                    media_resource_body["file"] = (
                        fileName,
                        service_image_file,
                        "image/jpg",
                    )

                    multipart_data = MultipartEncoder(media_resource_body)

                    if update:
                        requests.delete(
                            media_url + "/{}".format(featured_image_id),
                            headers=auth_header(),
                        )
                        response = requests.post(
                            media_url,
                            data=multipart_data,
                            headers={"Content-Type": multipart_data.content_type},
                            auth=(WORDPRESS_USER, WORDPRESS_APPLICATION_PASSWORD),
                        ).json()
                        services_table.update(
                            service_object.id,
                            {
                                AIRTABLE_MAP["wp_image_id"]: str(response["id"]),
                                AIRTABLE_MAP[
                                    "wp_image_last_uploaded_name"
                                ]: image_filename_from_airtable,
                            },
                        )
                        resource_body["featured_media"] = response["id"]
                    else:
                        click.echo(
                            click.style("In preview mode, skipping upload", fg="yellow")
                        )

        else:
            # This featured image ID comes from a default somewhere.
            # Just push it to Airtable.

            click.echo("Image using default featured image ID")

            services_table.update(
                service_object.id,
                {
                    AIRTABLE_MAP["wp_image_id"]: str(featured_image_id),
                },
            )

            resource_body["featured_media"] = int(featured_image_id)

    elif service_image:
        click.echo("No featured image ID known, uploading!")

        fileName = os.path.basename(service_image)

        with open(service_image, "rb") as service_image_file:
            media_resource_body["file"] = (
                fileName,
                service_image_file,
                "image/jpg",
            )

            media_resource_body["slug"] = service_object.churchsuite_image_field[0][
                "filename"
            ].split(".")[0]

            multipart_data = MultipartEncoder(media_resource_body)

            if update:
                response = requests.post(
                    media_url,
                    data=multipart_data,
                    headers={"Content-Type": multipart_data.content_type},
                    auth=(WORDPRESS_USER, WORDPRESS_APPLICATION_PASSWORD),
                ).json()
                services_table.update(
                    service_object.id,
                    {
                        AIRTABLE_MAP["wp_image_id"]: str(response["id"]),
                        AIRTABLE_MAP["wp_image_last_uploaded_name"]: fileName,
                    },
                )
                resource_body["featured_media"] = response["id"]
            else:
                click.echo(click.style("In preview mode, skipping upload", fg="yellow"))

    if service_object.order_of_service_id:
        click.echo("Order of Service ID found, updating!")

        if update:
            response = requests.post(
                url + "/{}".format(service_object.order_of_service_id),
                headers=auth_header(),
                json=resource_body,
            ).json()
            services_table.update(
                service_object.id,
                {AIRTABLE_MAP["oos_id"]: str(response["id"])},
            )
        else:
            click.echo(click.style("In preview mode, skipping creation", fg="yellow"))

    else:
        click.echo(click.style("No Order of Service ID found, creating!", fg="green"))

        resource_body["status"] = "draft"

        if update:
            response = requests.post(
                url, headers=auth_header(), json=resource_body
            ).json()
            print("New OOS created with ID {id}!".format(id=response["id"]))
            services_table.update(
                service_object.id, {AIRTABLE_MAP["oos_id"]: str(response["id"])}
            )
        else:
            click.echo(click.style("In preview mode, skipping creation", fg="yellow"))


def create_or_update_podcast_entry(service_object, services_table, update):
    podcast_resource_body = {
        "title": service_object.title_string,
        "slug": service_object.slug,
        "date": service_object.datetime_localised.isoformat(),
        "content": "<p>{}</p>".format(service_object.description),
    }

    if service_object.podcast_id:
        click.echo("Podcast ID found, updating!")

        if update:
            response = requests.post(
                podcast_url + "/{}".format(service_object.podcast_id),
                headers=auth_header(),
                json=podcast_resource_body,
            ).json()
            services_table.update(
                service_object.id,
                {AIRTABLE_MAP["podcast_id"]: str(response["id"])},
            )
        else:
            click.echo(click.style("In preview mode, skipping creation", fg="yellow"))

    else:
        click.echo(click.style("No Podcast ID found, creating!", fg="green"))

        podcast_resource_body["status"] = "draft"

        if update:
            response = requests.post(
                podcast_url, headers=auth_header(), json=podcast_resource_body
            ).json()
            print("New Podcast created with ID {id}!".format(id=response["id"]))
            services_table.update(
                service_object.id, {"Podcast ID": str(response["id"])}
            )
        else:
            click.echo(click.style("In preview mode, skipping creation", fg="yellow"))
