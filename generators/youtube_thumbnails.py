import hashlib
import json

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_LATO_BOLD_LG = ImageFont.truetype("fonts/Lato-Bold.ttf", 56)
FONT_LATO_REGULAR_MD = ImageFont.truetype("fonts/Lato-Regular.ttf", 42)

GENERATOR_VERSION = 3

TARGET_THUMBNAIL_DIMENSIONS = (1280, 720)
LEFT_MARGIN = 30
RIGHT_MARGIN = 120
BOTTOM_MARGIN = 90
SPACING_BETWEEN_TEXT = 8


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

            # Thumbnail the image, which handles cropping and resizing down (but not up)
            thumb_image.thumbnail(TARGET_THUMBNAIL_DIMENSIONS)

            # Resize the image, which scales it back up if necessary
            sized_image = thumb_image.resize(TARGET_THUMBNAIL_DIMENSIONS)

            # Create piece of canvas to draw text on and blur
            blurred = Image.new("RGBA", sized_image.size)
            draw = ImageDraw.Draw(blurred)

            # Text we want to actually write
            main_text = self.service.title_string
            aux_text = self.service.datetime.strftime("%-d %B %Y")

            main_text_draw_coordinates = (
                LEFT_MARGIN,
                TARGET_THUMBNAIL_DIMENSIONS[1] - 10 - BOTTOM_MARGIN,
            )

            # Figure out the bounding boxes for our main text
            main_text_bounding = draw.textbbox(
                main_text_draw_coordinates,
                main_text,
                anchor="ld",
                font=FONT_LATO_BOLD_LG,
            )

            main_text_max_width = (
                TARGET_THUMBNAIL_DIMENSIONS[0] - LEFT_MARGIN - RIGHT_MARGIN
            )

            # Is the text wider than our margins? If not, rock on. If it is, we need to do some wrapping.
            if main_text_bounding[2] > main_text_max_width:
                # Start with an empty string
                main_text_with_breaks = ""

                for word in main_text.split():
                    # Figure out the size of the box with the new word
                    text_to_test = main_text_with_breaks + word
                    main_text_bounding = draw.multiline_textbbox(
                        main_text_draw_coordinates,
                        text_to_test,
                        anchor="ld",
                        font=FONT_LATO_BOLD_LG,
                    )

                    if main_text_bounding[2] > main_text_max_width:
                        # It's too big, throw in a break
                        main_text_with_breaks += "\n"

                    main_text_with_breaks += word + " "

                # We're done calculating breakpoints, move the broken text to the main variable
                # and recalculate bounding box
                main_text = main_text_with_breaks
                main_text_bounding = draw.multiline_textbbox(
                    main_text_draw_coordinates,
                    main_text,
                    anchor="ld",
                    font=FONT_LATO_BOLD_LG,
                )

            aux_text_draw_coordinates = (
                LEFT_MARGIN,
                main_text_bounding[1] - SPACING_BETWEEN_TEXT,
            )

            draw.multiline_text(
                xy=main_text_draw_coordinates,
                text=main_text,
                fill="#030303",
                font=FONT_LATO_BOLD_LG,
                anchor="ld",
            )
            draw.text(
                xy=aux_text_draw_coordinates,
                text=aux_text,
                fill="#030303",
                font=FONT_LATO_REGULAR_MD,
                anchor="ld",
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
                anchor="ld",
            )
            draw.text(
                xy=aux_text_draw_coordinates,
                text=aux_text,
                fill="#FFF",
                font=FONT_LATO_REGULAR_MD,
                anchor="ld",
            )

            sized_image.save(
                self.generated_image_path,
                format="JPEG",
            )
