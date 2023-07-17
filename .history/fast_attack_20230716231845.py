import skimage.io
from skimage.util import random_noise

img = skimage.io.imread("images/peppers.png")

sigma = 0.15
noisy = random_noise(img, var=sigma**2)

skimage.io.imsave("images/lena_noisy.png", noisy)
