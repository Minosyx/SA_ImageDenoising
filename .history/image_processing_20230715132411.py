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

    def denoise(self, kwargs):
        print(kwargs)
        mth = self.available_methods.get(self.denoising_method, None)
        if mth is not None:
            mth(**kwargs)
        return self.image

    def svd(self, k: int):
        image_shape = self.image.shape

        if len(image_shape) == 3:
            iter = image_shape[2]
        else:
            iter = 1

        for i in range(iter):
            if iter == 3:
                img = self.image[:, :, i]
                out_denoised = np.zeros(image_shape)
            else:
                img = self.image
                out_denoised = np.zeros(image_shape)

            U, S, V = np.linalg.svd(img, full_matrices=False)

            print(k)

            T = np.copy(S)
            T[k:] = 0
            T = np.diag(T)

            denoised = U @ T @ V

            if iter == 3:
                print("iter")
                out_denoised[:, :, i] = denoised.astype(np.uint8)
            else:
                out_denoised = denoised.astype(np.uint8)

        self.image = out_denoised

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
