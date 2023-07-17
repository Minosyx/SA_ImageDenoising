import numpy as np
import imageio.v3 as iio
from scipy.fft import fftn, fftshift, ifftshift, ifftn
from skimage.restoration import denoise_wavelet, estimate_sigma
import pywt


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
        if len(image_shape) == 3:  # RGB image
            img = self.image.astype(np.float32)
            fft_dict = {}
            out_denoised = np.zeros(image_shape, dtype=np.float32)
            for i in range(3):
                channel = img[:, :, i]
                F = fftn(channel)
                F_mag = np.abs(F)
                F_mag = fftshift(F_mag)

                M, N = channel.shape
                F_mag[M // 2 - K : M // 2 + K, N // 2 - K : N // 2 + K] = 0

                peaks = F_mag < np.percentile(F_mag, percentile)
                peaks = ifftshift(peaks)

                F_dim = F.copy()
                F_dim *= peaks.astype(np.complex)
                denoised_channel = np.real(ifftn(F_dim))
                out_denoised[:, :, i] = denoised_channel
                fft_dict[f"fft_channel_{i}"] = F_mag
            self.image = (
                out_denoised.round().clip(0, 255).astype(np.uint8)
            )  # Clip values to valid range
            return fft_dict
        else:  # Grayscale image
            img = self.image.astype(np.float32)
            F = fftn(img)
            F_mag = np.abs(F)
            F_mag = fftshift(F_mag)

            M, N = img.shape
            F_mag[M // 2 - K : M // 2 + K, N // 2 - K : N // 2 + K] = 0

            peaks = F_mag < np.percentile(F_mag, percentile)
            peaks = ifftshift(peaks)

            F_dim = F.copy()
            F_dim *= peaks.astype(np.complex)
            denoised_img = np.real(ifftn(F_dim))
            self.image = (
                denoised_img.round().clip(0, 255).astype(np.uint8)
            )  # Clip values to valid range
            return {"fft_img": F_mag}

    def wavelet(
        self,
        method: str,
        mode: str,
        wavelet_levels: int,
        wavelet: str,
        rescale_sigma: bool,
        sigma_reduction: float,
    ):
        print("wavelet")
        image_shape = self.image.shape
        if len(image_shape) == 3:  # RGB image
            if method == "BayesShrink":
                denoised_img = denoise_wavelet(
                    self.image,
                    method=method,
                    mode=mode,
                    wavelet_levels=wavelet_levels,
                    wavelet=wavelet,
                    rescale_sigma=rescale_sigma,
                    channel_axis=-1,
                    convert2ycbcr=True,
                )
            elif method == "VisuShrink":
                sigma_est = estimate_sigma(
                    self.image, channel_axis=-1, average_sigmas=True
                )
                denoised_img = denoise_wavelet(
                    self.image,
                    method=method,
                    mode=mode,
                    wavelet_levels=wavelet_levels,
                    wavelet=wavelet,
                    rescale_sigma=rescale_sigma,
                    sigma=sigma_est / sigma_reduction,
                    channel_axis=-1,
                    convert2ycbcr=True,
                )
        else:  # Grayscale image
            if method == "BayesShrink":
                denoised_img = denoise_wavelet(
                    self.image,
                    method=method,
                    mode=mode,
                    wavelet_levels=wavelet_levels,
                    wavelet=wavelet,
                    rescale_sigma=rescale_sigma,
                )
            elif method == "VisuShrink":
                sigma_est = estimate_sigma(self.image, average_sigmas=True)
                denoised_img = denoise_wavelet(
                    self.image,
                    method=method,
                    mode=mode,
                    wavelet_levels=wavelet_levels,
                    wavelet=wavelet,
                    rescale_sigma=rescale_sigma,
                    sigma=sigma_est / sigma_reduction,
                )
        self.image = denoised_img.round().clip(0, 255).astype(np.uint8)


class ImageProperties(object):
    @classmethod
    def get_image_size(cls, image_path):
        ext = image_path.split(".")[-1]
        if ext == "jpeg":
            ext = "jpg"
        props = iio.immeta(image_path, extension=f".{ext}")
        return props["shape"]

    @classmethod
    def get_wavelets(cls):
        families = pywt.families(short=False)
        short_families = pywt.families(short=True)

        wavelets = {}
        for family in zip(families, short_families):
            wavelist = pywt.wavelist(family[1])
            wavelets[family[0]] = {wave: wave for wave in wavelist}

        # print(wavelets)
        return wavelets
