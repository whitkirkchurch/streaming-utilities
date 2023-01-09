import hashlib
import json


GENERATOR_VERSION = 3


class YoutubeThumbnail:
    def __init__(self, service):

        self.service = service

    @property
    def service_image_name(self):
        return self.service.service_image

    @property
    def generated_image_hash(self):

        data_hash_dict = {
            "image": self.service_image_name,
            "title": self.service.title_string,
            "datetime": self.service.datetime.strftime("%-d %B %Y"),
            "version": GENERATOR_VERSION,
        }

        return hashlib.md5(
            json.dumps(data_hash_dict, sort_keys=True).encode("utf-8")
        ).hexdigest()

    @property
    def generated_image_path(self):
        return "images/youtube_generated_thumbnails/{hash}.jpg".format(
            hash=self.generated_image_hash
        )
