import imageio.v3 as iio


def __tag_function(tag):
    def decorator(func):
        if not hasattr(decorator, "tagged_functions"):
            decorator.tagged_functions = {}

        decorator.tagged_functions[tag] = func

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def __call_tagged_function(tag, *args, **kwargs):
    decorator = getattr(__call_tagged_function, "decorator", None)
    if decorator and hasattr(decorator, "tagged_functions"):
        func = decorator.tagged_functions.get(tag)
        if func:
            return func(*args, **kwargs)

    raise ValueError(f"No function found with tag '{tag}'.")


class ImageDenoising(object):
    def __init__(self, imagePath, denoisingMethod):
        self.image = iio.imread(imagePath)
        self.denoisingMethod = denoisingMethod

    def denoise(self):
        return self.image

    @__tag_function("svd")
    def svd(self):
        pass

    @__tag_function("fft")
    def fft(self):
        pass

    @__tag_function("wavelet")
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
