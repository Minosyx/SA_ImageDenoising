import numpy as np
import imageio.v3 as iio
from PIL import Image


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

    def convert_to_float(self):
        if self.image.dtype == np.uint8:
            self.image = self.image.astype(np.float32) / 255.0

    def convert_to_uint8(self):
        if self.image.dtype == np.float32:
            self.image = (self.image * 255.0).astype(np.uint8)

    def svd(self, k: int):
        image_shape = self.image.shape
        if len(image_shape) == 3:  # RGB image
            img = self.image.astype(np.float32)
            out_denoised = np.zeros(image_shape, dtype=np.float32)
            for i in range(3):
                U, S, V = np.linalg.svd(img[:, :, i], full_matrices=False)
                T = np.copy(S)
                T[k:] = 0
                T = np.diag(T)
                denoised = U @ T @ V
                denoised = np.clip(denoised, 0, 255)  # Clip values to valid range
                out_denoised[:, :, i] = denoised
            self.image = out_denoised.round().astype(
                np.uint8
            )  # Round and convert to uint8
        else:  # Grayscale image
            img = self.image.astype(np.float32)
            U, S, V = np.linalg.svd(img, full_matrices=False)
            T = np.copy(S)
            T[k:] = 0
            T = np.diag(T)
            denoised = U @ T @ V
            self.image = denoised.round().astype(np.uint8)  # Round and convert to uint8

        # image_shape = self.image.shape

        # if len(image_shape) == 3:
        #     iter = image_shape[2]
        # else:
        #     iter = 1

        # for i in range(iter):
        #     if iter == 3:
        #         img = self.image[:, :, i]
        #         out_denoised = np.zeros(image_shape)
        #     else:
        #         img = self.image
        #         out_denoised = np.zeros(image_shape)

        #     U, S, V = np.linalg.svd(img, full_matrices=False)

        #     print(k)

        #     T = np.copy(S)
        #     T[k:] = 0
        #     T = np.diag(T)

        #     denoised = U @ T @ V

        #     if iter == 3:
        #         out_denoised[:, :, i] = denoised
        #     else:
        #         out_denoised = denoised

        # self.image = out_denoised.astype(np.uint8)

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
