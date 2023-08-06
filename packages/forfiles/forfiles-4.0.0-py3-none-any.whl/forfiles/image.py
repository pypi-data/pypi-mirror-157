from PIL import Image  # py -m pip install Pillow


def resize_image(image_path: str, image_width: int, image_height: int):
    """
    Resizes an image

    Parameters:
        image_path (string): full path of the image that will be resized
        image_width (int): width of the desired output image in pixels
        image_height (int): height of the desired output image in pixels

    Returns:
        void
    """

    supported_file_types = (
        ".png",
        ".jpg",
        ".gif",
        ".webp",
        ".tiff",
        ".bmp",
        ".jpe",
        ".jfif",
        ".jif",
    )

    if image_path.endswith(supported_file_types):
        with Image.open(image_path) as image:
            # image_width, image_height = image.size

            image = image.resize(
                (image_width, image_height),
                resample=Image.NEAREST,
            )

            image.save(image_path)


def image_scaler(image_path, width_multiplier, height_multiplier):
    """
    Scales image with the given multiplier(s)

    Parameters:
        image_path (string): full path of the image that will be resized
        image_width (int): width of the desired output image in pixels
        image_height (int): height of the desired output image in pixels

    Returns:
        void
    """

    supported_file_types = (".png", ".jpg", ".gif", ".webp", ".tiff", ".bmp")

    if image_path.endswith(supported_file_types):
        with Image.open(image_path) as image:
            image_width, image_height = image.size

            image = image.resize(
                (image_width * width_multiplier, image_height * height_multiplier),
                resample=Image.NEAREST,
            )

            image.save(image_path)


if __name__ == "__main__":
    resize_image("C:\\Users\\ambl\\Downloads\\car.jpg", 1600, 1600)
    image_scaler("C:\\Users\\ambl\\Downloads\\car.jpg", 10, 10)
