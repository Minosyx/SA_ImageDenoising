import imageio.v3 as iio


class ImageDenoising(object):
    def __init__(self, imagePath):
        self.image = iio.imread(imagePath)

    def denoise(self):
        return self.image


class ImageProperties(object):
    @classmethod
    def get_image_size(cls, imagePath):
        ext = imagePath.split(".")[-1]
        if ext == "jpeg":
            ext = "jpg"
        print(ext)
        iio.immeta
        props = iio.immeta(imagePath, extension=f".{ext}")
        print(props)
        return props["shape"]
