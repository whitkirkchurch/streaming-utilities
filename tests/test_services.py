import unittest
from datetime import datetime
from unittest.mock import patch

from factories import serviceFactory

from services import AIRTABLE_MAP, DEFAULT_SERVICE_IMAGE, download_service_image


class testService(unittest.TestCase):
    def test_slug_field(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["slug"]: "test-service"})
        self.assertEqual(service.slug, "test-service")

    def test_type_field(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["type"]: "Regular Service"})
        self.assertEqual(service.type_field, "Regular Service")

    def test_service_name_field(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["name"]: "Test Service"})
        self.assertEqual(service.name_field, "Test Service")

    def test_liturgical_name_field_returns_if_present(self) -> None:
        service = serviceFactory(
            {AIRTABLE_MAP["liturgical_name"]: "Test Liturgical Name"}
        )
        self.assertEqual(service.liturgical_name_field, "Test Liturgical Name")

    def test_liturgical_name_field_returns_none_if_missing(self) -> None:
        service = serviceFactory({})
        self.assertIsNone(service.liturgical_name_field)

    def test_location(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["location"]: "Some Place"})
        self.assertEqual(service.location, "Some Place")

    def test_technician_field(self) -> None:
        service = serviceFactory(
            {AIRTABLE_MAP["technician"]: {"name": "Test Technician"}}
        )
        self.assertEqual(service.technician_field, {"name": "Test Technician"})

    def test_technician_name_field(self) -> None:
        service_with_technician = serviceFactory(
            {AIRTABLE_MAP["technician"]: {"name": "Test Technician"}}
        )

        service_without_technician = serviceFactory({})

        self.assertEqual(service_with_technician.technician_name, "Test Technician")

        self.assertIsNone(service_without_technician.technician_name)

    def test_churchsuite_category_id(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["churchsuite_category_id"]: "123"})
        self.assertEqual(service.churchsuite_category_id, "123")

    def test_order_of_service_id(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["oos_id"]: "1234"})
        self.assertEqual(service.order_of_service_id, "1234")

    def test_podcast_id(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["podcast_id"]: "2345"})
        self.assertEqual(service.podcast_id, "2345")

    def test_youtube_id(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["youtube_id"]: "a1-b2_c3"})
        self.assertEqual(service.youtube_id, "a1-b2_c3")

    def test_churchsuite_image_field(self) -> None:
        service = serviceFactory(
            {AIRTABLE_MAP["churchsuite_image"]: {"id": "tEsTiMaGeId"}}
        )
        self.assertEqual(service.churchsuite_image_field, {"id": "tEsTiMaGeId"})

    def test_wordpress_image_id(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["wp_image_id"]: "3456"})
        self.assertEqual(service.wordpress_image_id, "3456")

    def test_wordpress_image_last_uploaded_name(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["wp_image_last_uploaded_name"]: "3456"})
        self.assertEqual(service.wordpress_image_last_uploaded_name, "3456")

    def test_youtube_image_last_uploaded_name(self) -> None:
        service = serviceFactory(
            {AIRTABLE_MAP["youtube_image_last_uploaded_name"]: "thumbnail.jpg"}
        )
        self.assertEqual(service.youtube_image_last_uploaded_name, "thumbnail.jpg")

    def test_datetime_field(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z"})
        self.assertEqual(service.datetime_field, "2022-01-01T10:00:00.000Z")

    def test_datetime(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z"})
        self.assertIsInstance(service.datetime_localised, datetime)
        self.assertEqual(
            service.datetime_localised.isoformat(), "2022-01-01T10:00:00+00:00"
        )

        service_in_bst = serviceFactory(
            {AIRTABLE_MAP["datetime"]: "2022-08-01T09:00:00.000Z"}
        )
        self.assertEqual(
            service_in_bst.datetime_localised.isoformat(), "2022-08-01T10:00:00+01:00"
        )

    def test_datetime_as_naive_string(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z"})
        self.assertEqual(service.datetime_as_naive_string, "2022-01-01 10:00:00")

        service_in_bst = serviceFactory(
            {AIRTABLE_MAP["datetime"]: "2022-08-01T09:00:00.000Z"}
        )
        self.assertEqual(service_in_bst.datetime_as_naive_string, "2022-08-01 10:00:00")

    def test_datetime_to_publish_order_of_service(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-02T10:00:00.000Z"})
        self.assertEqual(
            service.datetime_to_publish_order_of_service.replace(tzinfo=None),
            datetime(2022, 1, 1, 10, 0, 0),
        )

    def test_datetime_to_publish_order_of_service_given_previous_service_is_none(
        self,
    ) -> None:
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-02T10:00:00.000Z"})
        self.assertEqual(
            service.datetime_to_publish_order_of_service_given_previous_service(
                None
            ).replace(tzinfo=None),
            datetime(2022, 1, 1, 10, 0, 0),
        )

    def test_datetime_to_publish_order_of_service_given_previous_service_is_over_24h(
        self,
    ) -> None:
        previous_service = serviceFactory(
            {AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z"}
        )
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-03T10:00:00.000Z"})
        self.assertEqual(
            service.datetime_to_publish_order_of_service_given_previous_service(
                previous_service
            ).replace(tzinfo=None),
            datetime(2022, 1, 2, 10, 0, 0),
        )

    def test_datetime_to_publish_order_of_service_given_previous_service_is_within_24h(
        self,
    ) -> None:
        previous_service = serviceFactory(
            {AIRTABLE_MAP["datetime"]: "2022-01-02T10:00:00.000Z"}
        )
        service = serviceFactory({AIRTABLE_MAP["datetime"]: "2022-01-02T18:00:00.000Z"})
        self.assertEqual(
            service.datetime_to_publish_order_of_service_given_previous_service(
                previous_service
            ).replace(tzinfo=None),
            datetime(2022, 1, 2, 11, 0, 0),
        )

    def test_streaming_field(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["streaming"]: "Yes"})
        self.assertEqual(service.streaming_field, "Yes")

    def test_is_streaming(self) -> None:
        service_streaming_yes = serviceFactory({AIRTABLE_MAP["streaming"]: "Yes"})

        service_streaming_no = serviceFactory({AIRTABLE_MAP["streaming"]: "No"})

        service_without_streaming = serviceFactory({})

        self.assertTrue(service_streaming_yes.is_streaming)

        self.assertFalse(service_streaming_no.is_streaming)

        self.assertFalse(service_without_streaming.is_streaming)

    def test_is_stream_public(self) -> None:
        service_public_yes = serviceFactory({AIRTABLE_MAP["stream_public"]: True})

        service_public_no = serviceFactory({})

        self.assertTrue(service_public_yes.is_stream_public)

        self.assertFalse(service_public_no.is_stream_public)

    def test_has_oos(self) -> None:
        service_oos_yes = serviceFactory({AIRTABLE_MAP["has_oos"]: True})

        service_oos_no = serviceFactory({})

        self.assertTrue(service_oos_yes.has_oos)

        self.assertFalse(service_oos_no.has_oos)

    def test_is_fee_payable(self) -> None:
        service_payable_yes = serviceFactory({AIRTABLE_MAP["fee_payable"]: True})

        service_payable_no = serviceFactory({})

        self.assertTrue(service_payable_yes.is_fee_payable)

        self.assertFalse(service_payable_no.is_fee_payable)

    def test_title_string(self) -> None:
        service_with_no_liturgical_name = serviceFactory(
            {AIRTABLE_MAP["name"]: "Test Service"}
        )

        service_with_liturgical_name = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Service",
                AIRTABLE_MAP["liturgical_name"]: "Test Liturgical Name",
            }
        )

        self.assertEqual(service_with_no_liturgical_name.title_string, "Test Service")

        self.assertEqual(
            service_with_liturgical_name.title_string, "Test Liturgical Name"
        )

    def test_title_string_with_date(self) -> None:
        service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Service",
                AIRTABLE_MAP["datetime"]: "2022-01-01T10:00:00.000Z",
            }
        )

        self.assertEqual(service.title_string_with_date, "Test Service: 1 January 2022")

    def test_described_as(self) -> None:
        standard_service = serviceFactory({AIRTABLE_MAP["name"]: "Test Service"})

        said_eucharist_service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Said Eucharist Service",
            }
        )

        sung_eucharist_service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Sung Eucharist Service",
            }
        )

        evensong_service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Choral Evensong Service",
                AIRTABLE_MAP["churchsuite_category_id"]: "34",
            }
        )

        self.assertEqual(standard_service.described_as, "service")
        self.assertEqual(said_eucharist_service.described_as, "service")
        self.assertEqual(sung_eucharist_service.described_as, "sung Eucharist")
        self.assertEqual(evensong_service.described_as, "service of Choral Evensong")

    def test_service_description(self) -> None:
        standard_service = serviceFactory({AIRTABLE_MAP["name"]: "Test Service"})

        standard_service_at_location = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Service",
                AIRTABLE_MAP["location"]: "Some Place",
            }
        )

        sung_eucharist_service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Sung Eucharist Service",
            }
        )

        sung_eucharist_with_liturgical_name_service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Sung Eucharist Service",
                AIRTABLE_MAP[
                    "liturgical_name"
                ]: "the eleventy-first Sunday after Trinity",
            }
        )

        sung_eucharist_with_liturgical_name_at_location_service = serviceFactory(
            {
                AIRTABLE_MAP["name"]: "Test Sung Eucharist Service",
                AIRTABLE_MAP["location"]: "Some Place",
                AIRTABLE_MAP[
                    "liturgical_name"
                ]: "the eleventy-first Sunday after Trinity",
            }
        )

        self.assertEqual(
            standard_service.description,
            "A service streamed live from St Mary's Church, Whitkirk.",
        )
        self.assertEqual(
            standard_service_at_location.description,
            "A service streamed live from Some Place.",
        )
        self.assertEqual(
            sung_eucharist_service.description,
            "A sung Eucharist streamed live from St Mary's Church, Whitkirk.",
        )
        self.assertEqual(
            sung_eucharist_with_liturgical_name_service.description,
            "A sung Eucharist streamed live from St Mary's Church, Whitkirk for the eleventy-first Sunday after Trinity.",
        )
        self.assertEqual(
            sung_eucharist_with_liturgical_name_at_location_service.description,
            "A sung Eucharist streamed live from Some Place for the eleventy-first Sunday after Trinity.",
        )

    def test_has_service_specific_image(self) -> None:
        service_with_specific_image = serviceFactory(
            {
                AIRTABLE_MAP["churchsuite_image"]: [
                    {"url": "https://example.com/1m4g3.jpg", "filename": "1m4g3.jpg"}
                ]
            }
        )

        service_without_specific_image = serviceFactory({})

        self.assertTrue(service_with_specific_image.has_service_specific_image)

        self.assertFalse(service_without_specific_image.has_service_specific_image)

    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {"456": {"default_thumbnail": "override.jpg"}},
    )
    def test_has_category_specific_image(self) -> None:
        service_without_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "123"}
        )
        service_with_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "456"}
        )

        self.assertFalse(service_without_override.has_category_specific_image)
        self.assertTrue(service_with_override.has_category_specific_image)

    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {"456": {"default_thumbnail": "override.jpg"}},
    )
    @patch("services.download_service_image")
    def test_service_image(self, download_image) -> None:
        service_with_specific_image_without_category = serviceFactory(
            {
                AIRTABLE_MAP["churchsuite_image"]: [
                    {"url": "https://example.com/1m4g31.jpg", "filename": "1m4g31.jpg"}
                ]
            }
        )
        service_with_specific_image_with_category = serviceFactory(
            {
                AIRTABLE_MAP["churchsuite_image"]: [
                    {"url": "https://example.com/1m4g32.jpg", "filename": "1m4g32.jpg"}
                ],
                AIRTABLE_MAP["churchsuite_category_id"]: "456",
            }
        )
        service_with_category = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "456"}
        )
        service_without_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "123"}
        )

        download_image.side_effect = [
            ("images/service_specific/1m4g31.jpg", []),
            ("images/service_specific/1m4g32.jpg", []),
        ]

        self.assertEqual(
            service_with_specific_image_without_category.service_image,
            "images/service_specific/1m4g31.jpg",
        )
        self.assertEqual(
            service_with_specific_image_with_category.service_image,
            "images/service_specific/1m4g32.jpg",
        )
        self.assertEqual(
            service_with_category.service_image,
            "images/default_thumbnails/override.jpg",
        )
        self.assertEqual(service_without_override.service_image, DEFAULT_SERVICE_IMAGE)

    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {"456": {"default_thumbnail": "test.jpg"}},
    )
    def test_has_category_behaviour_overrides(self) -> None:
        service_without_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "123"}
        )
        service_with_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "456"}
        )

        self.assertFalse(service_without_override.has_category_behaviour_overrides)
        self.assertTrue(service_with_override.has_category_behaviour_overrides)

    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {"456": {"default_thumbnail": "test.jpg"}},
    )
    def test_category_behaviour_overrides(self) -> None:
        service_without_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "123"}
        )
        service_with_override = serviceFactory(
            {AIRTABLE_MAP["churchsuite_category_id"]: "456"}
        )

        self.assertEqual(service_without_override.category_behaviour_overrides, {})
        self.assertEqual(
            service_with_override.category_behaviour_overrides,
            {"default_thumbnail": "test.jpg"},
        )

    @patch("services.YOUTUBE_DEFAULT_PLAYLIST_ID", "PlAyLiStId")
    def test_youtube_playlists_for_service_with_no_overrides(self) -> None:
        service = serviceFactory({})

        self.assertEqual(len(service.youtube_playlists_for_service), 1)
        self.assertIn("PlAyLiStId", service.youtube_playlists_for_service)

    @patch("services.YOUTUBE_DEFAULT_PLAYLIST_ID", "PlAyLiStId")
    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {"123": {"youtube_playlists": {"ExTrApLaYlIsT"}}},
    )
    def test_youtube_playlists_for_service_with_additional_category(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["churchsuite_category_id"]: "123"})

        self.assertEqual(len(service.youtube_playlists_for_service), 2)
        self.assertIn("PlAyLiStId", service.youtube_playlists_for_service)
        self.assertIn("ExTrApLaYlIsT", service.youtube_playlists_for_service)

    @patch("services.YOUTUBE_DEFAULT_PLAYLIST_ID", "PlAyLiStId")
    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {
            "123": {
                "exclude_youtube_playlists": {"PlAyLiStId"},
            }
        },
    )
    def test_youtube_playlists_for_service_with_exclude_category(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["churchsuite_category_id"]: "123"})

        self.assertEqual(len(service.youtube_playlists_for_service), 0)
        self.assertNotIn("PlAyLiStId", service.youtube_playlists_for_service)

    @patch("services.YOUTUBE_DEFAULT_PLAYLIST_ID", "PlAyLiStId")
    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {
            "123": {
                "youtube_playlists": {"ExTrApLaYlIsT"},
                "exclude_youtube_playlists": {"PlAyLiStId"},
            }
        },
    )
    def test_youtube_playlists_for_service_with_additional_and_exclude_category(
        self,
    ) -> None:
        service = serviceFactory({AIRTABLE_MAP["churchsuite_category_id"]: "123"})

        self.assertEqual(len(service.youtube_playlists_for_service), 1)
        self.assertNotIn("PlAyLiStId", service.youtube_playlists_for_service)
        self.assertIn("ExTrApLaYlIsT", service.youtube_playlists_for_service)

    @patch("services.YOUTUBE_DEFAULT_PLAYLIST_ID", "PlAyLiStId")
    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {
            "123": {
                "youtube_playlists": {"ExTrApLaYlIsT"},
                "exclude_youtube_playlists": {"ExTrApLaYlIsT"},
            }
        },
    )
    def test_youtube_playlists_for_service_exclude_takes_precedence(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["churchsuite_category_id"]: "123"})

        self.assertNotIn("ExTrApLaYlIsT", service.youtube_playlists_for_service)

    @patch("services.YOUTUBE_DEFAULT_PLAYLIST_ID", "PlAyLiStId")
    @patch(
        "services.CHURCHSUITE_CATEGORY_BEHAVIOUR_OVERRIDES",
        {"123": {"youtube_playlists": {"PlAyLiStId"}}},
    )
    def test_youtube_playlists_for_service_deduplicates(self) -> None:
        service = serviceFactory({AIRTABLE_MAP["churchsuite_category_id"]: "123"})

        self.assertEqual(len(service.youtube_playlists_for_service), 1)
        self.assertIn("PlAyLiStId", service.youtube_playlists_for_service)

    def test_youtube_is_embeddable(self) -> None:
        service_public_yes = serviceFactory({AIRTABLE_MAP["stream_public"]: True})

        service_public_no = serviceFactory({})

        self.assertTrue(service_public_yes.youtube_is_embeddable)

        self.assertFalse(service_public_no.youtube_is_embeddable)

    def test_youtube_privacy(self) -> None:
        service_public_yes = serviceFactory({AIRTABLE_MAP["stream_public"]: True})

        service_public_no = serviceFactory({})

        self.assertEqual(service_public_yes.youtube_privacy, "public")

        self.assertEqual(service_public_no.youtube_privacy, "unlisted")


class testServiceFunctions(unittest.TestCase):
    @patch("services.urllib.request.urlretrieve")
    def test_download_service_image(self, urlretrieve) -> None:
        download_service_image("https://example.com/test.jpg", "test.jpg")

        urlretrieve.assert_called_with(
            "https://example.com/test.jpg", "images/service_specific/test.jpg"
        )
