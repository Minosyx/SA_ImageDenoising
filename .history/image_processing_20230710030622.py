import imageio.v3 as iio


def _tag_function(tag: str) -> callable:
    def decorator(func: callable) -> callable:
        if not hasattr(decorator, "tagged_functions"):
            decorator.tagged_functions = {}

        decorator.tagged_functions[tag] = func

        def wrapper(*args, **kwargs) -> callable:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _call_tagged_function(tag: str, *args, **kwargs) -> callable:
    decorator = getattr(_call_tagged_function, "decorator", None)
    if decorator and hasattr(decorator, "tagged_functions"):
        func = decorator.tagged_functions.get(tag)
        if func:
            return func(*args, **kwargs)

    raise ValueError(f"No function found with tag '{tag}'.")


class ImageDenoising(object):
    def __init__(self, imagePath: str, denoisingMethod: str):
        self.image = iio.imread(imagePath)
        self.denoisingMethod = denoisingMethod

    def denoise(self, *args, **kwargs):
        _call_tagged_function(self.denoisingMethod)

    @_tag_function("svd")
    def svd(self):
        print("svd")

    @_tag_function("fft")
    def fft(self):
        print("fft")

    @_tag_function("wavelet")
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
