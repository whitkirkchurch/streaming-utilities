import os

from unittest.mock import patch

from services import AIRTABLE_MAP, Service

from generators.youtube_thumbnails import YoutubeThumbnail


def serviceFactory(fields, id="a1b2c3d4"):

    return Service({"id": id, "fields": fields})


def test_service_image_path():
    service = serviceFactory({})
    youtube_thumbnail = YoutubeThumbnail(service)

    assert (
        youtube_thumbnail.service_image_path == "images/default_thumbnails/service.jpg"
    )


@patch(
    "generators.youtube_thumbnails.GENERATOR_VERSION",
    1,
)
def test_generated_image_hash():
    service = serviceFactory(
        {
            AIRTABLE_MAP["name"]: "Test Service",
            AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z",
        }
    )
    youtube_thumbnail = YoutubeThumbnail(service)

    assert youtube_thumbnail.generated_image_hash == "98e95ba1746fb2c670edbb639d50c585"


@patch(
    "generators.youtube_thumbnails.GENERATOR_VERSION",
    1,
)
def test_generated_image_path():
    service = serviceFactory(
        {
            AIRTABLE_MAP["name"]: "Test Service",
            AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z",
        }
    )
    youtube_thumbnail = YoutubeThumbnail(service)

    assert (
        youtube_thumbnail.generated_image_path
        == "images/youtube_generated_thumbnails/98e95ba1746fb2c670edbb639d50c585.jpg"
    )


@patch(
    "generators.youtube_thumbnails.GENERATOR_VERSION",
    1,
)
def test_generate_saves_image_with_single_line_title():

    service = serviceFactory(
        {
            AIRTABLE_MAP["name"]: "Test Service",
            AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z",
        }
    )
    youtube_thumbnail = YoutubeThumbnail(service)

    youtube_thumbnail.generate()

    assert os.path.isfile(
        "images/youtube_generated_thumbnails/98e95ba1746fb2c670edbb639d50c585.jpg"
    )


@patch(
    "generators.youtube_thumbnails.GENERATOR_VERSION",
    1,
)
def test_generate_saves_image_with_multi_line_title():

    service = serviceFactory(
        {
            AIRTABLE_MAP[
                "name"
            ]: "Test Service with an unusually long title designed to test multi-line behaviour",
            AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z",
        }
    )
    youtube_thumbnail = YoutubeThumbnail(service)

    youtube_thumbnail.generate()

    assert os.path.isfile(
        "images/youtube_generated_thumbnails/c55ed34a5c26be1fa6723d7afdb1a036.jpg"
    )
