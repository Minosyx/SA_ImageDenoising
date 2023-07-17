# import imageio.v3 as iio
import numpy as np
import imageio.v3 as iio


class ImageDenoising(object):
    def __init__(self, image_path: str, denoising_method: str):
        self.available_methods = self.get_available_methods()
        self.image = iio.imread(image_path)
        self.denoising_method = denoising_method

    def get_available_methods(self):
        return {
            "svd": self.svd,
            "fft": self.fft,
            "wavelet": self.wavelet,
        }

    def denoise(self):
        mth = self.available_methods.get(self.denoising_method, None)
        if mth is not None:
            mth()
        return self.image

    def svd(self):
        U, S, V = np.linalg.svd(self.image, full_matrices=False)

        # take the first 50 singular values
        k = 50
        T = S[:k]
        T = np.diag(T)

        denoised = U @ T @ V
        self.image = denoised

    def fft(self):
        print("fft")

    def wavelet(self):
        print("wavelet")


class ImageProperties(object):
    @classmethod
    def get_image_size(cls, image_path):
        ext = image_path.split(".")[-1]
        if ext == "jpeg":
            ext = "jpg"
        props = iio.immeta(image_path, extension=f".{ext}")
        return props["shape"]
