import imageio.v3 as iio

from PIL import JpegImagePlugin

JpegImagePlugin._getmp = lambda: None


class ImageDenoising(object):
    def __init__(self, imagePath):
        self.image = iio.imread(imagePath)

    def denoise(self):
        return self.image


class ImageProperties(object):
    @classmethod
    def get_image_size(cls, imagePath):
        ext = imagePath.split(".")[-1]
        props = iio.improps(imagePath, extension=f".{ext}")
        print(props)
        height, width, _ = props.shape
        return height, width
