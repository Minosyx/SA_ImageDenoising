import imageio.v3 as iio


class ImageDenoising(object):
    def __init__(self, imagePath):
        self.image = iio.imread(imagePath)

    @classmethod
    def get_image_size(cls, imagePath):
        props = iio.improps(imagePath)
        height, width, _ = props.shape
        return height, width

    def denoise(self):
        return self.image
