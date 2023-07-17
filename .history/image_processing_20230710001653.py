import imageio.v3 as iio


class ImageDenoising(object):
    def __init__(self, imagePath):
        self.image = iio.imread(imagePath)

    def denoise(self):
        return self.image
