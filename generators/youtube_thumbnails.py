import hashlib
import json

from PIL import Image, ImageFont, ImageDraw, ImageFilter

FONT_LATO_BOLD_LG = ImageFont.truetype("fonts/Lato-Bold.ttf", 56)
FONT_LATO_REGULAR_MD = ImageFont.truetype("fonts/Lato-Regular.ttf", 42)

GENERATOR_VERSION = 3


class YoutubeThumbnail:
    def __init__(self, service):

        self.service = service

    @property
    def service_image_path(self):
        return self.service.service_image

    @property
    def generated_image_hash(self):

        data_hash_dict = {
            "image": self.service_image_path,
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

    def generate(self):

        with Image.open(self.service_image_path) as thumb_image:

            target_image_dimensions = (1280, 720)

            thumb_image.thumbnail(target_image_dimensions)

            sized_image = thumb_image.resize(target_image_dimensions)

            drawing_corner_offset_x = 30
            drawing_corner_offset_y = 90

            # Create piece of canvas to draw text on and blur
            blurred = Image.new("RGBA", sized_image.size)
            draw = ImageDraw.Draw(blurred)

            # Text we want to actually write
            main_text = self.service.title_string
            aux_text = self.service.datetime.strftime("%-d %B %Y")

            main_text_draw_coordinates = (
                drawing_corner_offset_x,
                target_image_dimensions[1] - 10 - drawing_corner_offset_y,
            )
            aux_text_draw_coordinates = (
                drawing_corner_offset_x,
                target_image_dimensions[1] - 70 - drawing_corner_offset_y,
            )

            draw.text(
                xy=main_text_draw_coordinates,
                text=main_text,
                fill="#030303",
                font=FONT_LATO_BOLD_LG,
                anchor="ls",
            )
            draw.text(
                xy=aux_text_draw_coordinates,
                text=aux_text,
                fill="#030303",
                font=FONT_LATO_REGULAR_MD,
                anchor="ls",
            )
            blurred = blurred.filter(ImageFilter.BoxBlur(7))

            # Paste soft text onto background
            sized_image.paste(blurred, blurred)

            # Draw on sharp text
            draw = ImageDraw.Draw(sized_image)
            draw.text(
                xy=main_text_draw_coordinates,
                text=main_text,
                fill="#FFF",
                font=FONT_LATO_BOLD_LG,
                anchor="ls",
            )
            draw.text(
                xy=aux_text_draw_coordinates,
                text=aux_text,
                fill="#FFF",
                font=FONT_LATO_REGULAR_MD,
                anchor="ls",
            )

            sized_image.save(
                self.generated_image_path,
                format="JPEG",
            )
