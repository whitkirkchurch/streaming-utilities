import unittest
from unittest.mock import patch

from interfaces.youtube import Playlist, PlaylistManager


class testYoutubePlaylist(unittest.TestCase):
    @patch("interfaces.youtube.Api")
    def test_load_items(self, api):

        api.client.playlistItems().list().execute.return_value = {
            "items": [
                {
                    "snippet": {
                        "resourceId": {"kind": "youtube#video", "videoId": "OnE"}
                    }
                },
                {
                    "snippet": {
                        "resourceId": {"kind": "youtube#video", "videoId": "tWo"}
                    }
                },
                {
                    "snippet": {
                        "resourceId": {"kind": "youtube#video", "videoId": "ThReE"}
                    }
                },
            ]
        }

        playlist = Playlist(api, "PlAyLiSt")

        api.client.playlistItems().list().execute.assert_called_once()

        self.assertEqual(playlist.videos_in_list, ["OnE", "tWo", "ThReE"])

    @patch("interfaces.youtube.Api")
    def test_load_items_over_multiple_pages(self, api):

        api.client.playlistItems().list().execute.side_effect = [
            {
                "items": [
                    {
                        "snippet": {
                            "resourceId": {"kind": "youtube#video", "videoId": "OnE"}
                        }
                    },
                    {
                        "snippet": {
                            "resourceId": {"kind": "youtube#video", "videoId": "tWo"}
                        }
                    },
                    {
                        "snippet": {
                            "resourceId": {"kind": "youtube#video", "videoId": "ThReE"}
                        }
                    },
                ],
                "nextPageToken": "NeXtPaGe",
            },
            {
                "items": [
                    {
                        "snippet": {
                            "resourceId": {"kind": "youtube#video", "videoId": "fOuR"}
                        }
                    },
                    {
                        "snippet": {
                            "resourceId": {"kind": "youtube#video", "videoId": "fIvE"}
                        }
                    },
                ],
            },
        ]

        playlist = Playlist(api, "PlAyLiSt")

        self.assertEqual(api.client.playlistItems().list().execute.call_count, 2)

        self.assertEqual(
            playlist.videos_in_list, ["OnE", "tWo", "ThReE", "fOuR", "fIvE"]
        )

    @patch("interfaces.youtube.Api")
    def test_items(self, api):

        playlist = Playlist(api, "PlAyLiSt")

        playlist.videos_in_list = ["OnE", "tWo", "ThReE"]

        self.assertEqual(playlist.items, ["OnE", "tWo", "ThReE"])


class testYoutubePlaylistManager(unittest.TestCase):
    @patch("interfaces.youtube.Api")
    def test_returns_playlist(self, *args):

        manager = PlaylistManager()

        self.assertIsInstance(manager.get("PlAyLiSt"), Playlist)

    @patch("interfaces.youtube.Api")
    def test_returns_existing_instance_for_list_where_present(self, *args):

        manager = PlaylistManager()

        playlist_1 = manager.get("PlAyLiSt")
        playlist_2 = manager.get("PlAyLiSt")

        self.assertEqual(id(playlist_1), id(playlist_2))


if __name__ == "__main__":
    unittest.main()
