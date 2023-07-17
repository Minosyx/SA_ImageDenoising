import numpy as np
import imageio.v3 as iio
from scipy.fft import fft2, ifft2, fftn, fftshift, ifftshift, ifftn


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

    def fft(self, K: int, percentile: int):
        image_shape = self.image.shape
        F = fftn(self.image)
        F_mag = np.abs(F)
        F_mag = fftshift(F_mag)

        M, N = image_shape
        F_mag[M // 2 - K : M // 2 + K, N // 2 - K : N // 2 + K] = 0

        peaks = F_mag < np.percentile(F_mag, percentile)
        peaks = ifftshift(peaks)

        F_dim = F.copy()
        F_dim *= peaks.astype(np.int)
        denoised = np.real(ifftn(F_dim))
        self.image = denoised.round().astype(np.uint8)

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
