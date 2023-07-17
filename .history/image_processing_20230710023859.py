import imageio.v3 as iio


class ImageDenoising(object):
    functions = {
        "svd": 
    }
    
    def __init__(self, imagePath, denoisingMethod):
        self.image = iio.imread(imagePath)
        self.denoisingMethod = self.functions[denoisingMethod]

    def denoise(self):
        return self.image
    
    def svd(self):
        pass
    
    def fft(self):
        pass
    
    def wavelet(self):
        pass


class ImageProperties(object):
    @classmethod
    def get_image_size(cls, imagePath):
        ext = imagePath.split(".")[-1]
        if ext == "jpeg":
            ext = "jpg"
        props = iio.immeta(imagePath, extension=f".{ext}")
        return props["shape"]
