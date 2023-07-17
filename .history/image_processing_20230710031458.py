import imageio.v3 as iio


class ImageDenoising(object):
    def __init__(self, imagePath: str, denoisingMethod: str):
        self.image = iio.imread(imagePath)
        self.denoisingMethod = denoisingMethod

    def denoise(self, *args, **kwargs):
        globals()[self.denoisingMethod](self, *args, **kwargs)

    def svd(self):
        print("svd")

    def fft(self):
        print("fft")

    def wavelet(self):
        print("wavelet")


class ImageProperties(object):
    @classmethod
    def get_image_size(cls, imagePath):
        ext = imagePath.split(".")[-1]
        if ext == "jpeg":
            ext = "jpg"
        props = iio.immeta(imagePath, extension=f".{ext}")
        return props["shape"]
