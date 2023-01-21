
from PIL import Image, ImageDraw
import math

from PIL import Image, ImageDraw
import argparse

import copy

import numpy as np

# def flatten(ls):
#     return reduce(lambda x, y: x + y, ls, [])

def apply_to_each_pixel(pixels, f):
    for i in range(0, len(pixels)):
        for j in range(0, len(pixels[i])):
            pixels[i][j] = f(pixels[i][j])

def transpose(ls):
    return map(list, zip(*ls))

def gauss(x, y):
    ssigma = 1.0
    return (1 / (2 * math.pi * ssigma)) * math.exp(-(x * x + y * y) / (2 * ssigma))

def kernel_from_function(size, f):
    kernel = [[] for i in range(0, size)]
    for i in range(0, size):
        for j in range(0, size):
            kernel[i].append(f(i - size / 2, j - size / 2))
    return kernel

def gauss_kernel(size):
    return kernel_from_function(size, gauss)

def apply_kernel(pixels, kernel):
    apply_kernel_with_f(pixels, kernel, lambda old, new: new)

def apply_kernel_with_f(pixels, kernel, f):
    size = len(kernel)
    for i in range(int(size / 2), int(len(pixels) - size / 2)):
        for j in range(int(size / 2), int(len(pixels[i]) - size / 2)):
            i = int(i)
            j = int(j)
            pixels[i][j] = f(pixels[i][j], apply_kernel_at(lambda x, y: pixels[x][y], kernel, i, j))

def load_image(im):
    (x, y) = im.size
    im_load = im.load()

    result = []
    for i in range(0, x):
        result.append([])
        for j in range(0, y):
            result[i].append(im_load[i, j])

    return result

def load_pixels(im, pixels):
    (x, y) = im.size
    im_load = im.load()

    for i in range(0, x):
        for j in range(0, y):
            im_load[i, j] = pixels[i][j]

def apply_kernel_at(get_value, kernel, i, j):
    kernel_size = len(kernel)
    result = 0
    for k in range(0, kernel_size):
        for l in range(0, kernel_size):
            pixel = get_value(int(i + k - kernel_size / 2), int(j + l - kernel_size / 2))
            result += pixel * kernel[k][l]
    return result

def calculate_angles(im, W, f, g):
    (x, y) = im.size
    im_load = im.load()
    get_pixel = lambda x, y: im_load[x, y]
    
    sobelOperator = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]

    ySobel = np.array(sobelOperator).astype(int)
    xSobel = np.transpose(ySobel).astype(int)

    result = [[] for i in range(1, x, W)]

    for i in range(1, x, W):
        for j in range(1, y, W):
            nominator = 0
            denominator = 0
            for k in range(i, min(i + W , x - 1)):
                for l in range(j, min(j + W, y - 1)):
                    Gx = apply_kernel_at(get_pixel, xSobel, k, l)
                    Gy = apply_kernel_at(get_pixel, ySobel, k, l)
                    nominator += f(Gx, Gy)
                    denominator += g(Gx, Gy)
            angle = (math.pi + math.atan2(nominator, denominator)) / 2
            result[int((i - 1) / W)].append(angle)

    return result

def get_line_ends(i, j, W, tang):
    if -1 <= tang and tang <= 1:
        begin = (i, (-W/2) * tang + j + W/2)
        end = (i + W, (W/2) * tang + j + W/2)
    else:
        begin = (i + W/2 + W/(2 * tang), j + W/2)
        end = (i + W/2 - W/(2 * tang), j - W/2)
    return (begin, end)

def draw_lines(im, angles, W):
    (x, y) = im.size
    result = im.convert("RGB")

    draw = ImageDraw.Draw(result)

    for i in range(1, x, W):
        for j in range(1, y, W):
            tang = math.tan(angles[int((i - 1) / W)][int((j - 1) / W)])

            (begin, end) = get_line_ends(i, j, W, tang)
            draw.line([begin, end], fill='red', width=1)
    del draw
    

    return result

def smooth_angles(angles):
    cos_angles = copy.deepcopy(angles)
    sin_angles = copy.deepcopy(angles)
    apply_to_each_pixel(cos_angles, lambda x: math.cos(2 * x))
    apply_to_each_pixel(sin_angles, lambda x: math.sin(2 * x))

    kernel = gauss_kernel(5)
    apply_kernel(cos_angles, kernel)
    apply_kernel(sin_angles, kernel)

    for i in range(0, len(cos_angles)):
        for j in range(0, len(cos_angles[i])):
            cos_angles[i][j] = (math.atan2(sin_angles[i][j], cos_angles[i][j])) / 2

    return cos_angles

#-------------------------------------------------------------------------------------

# python3 Orientation.py 1__M_Left_index_finger.BMP 8 --smooth

parser = argparse.ArgumentParser(description="Rao's and Chinese algorithms")
parser.add_argument("image", nargs=1, help = "Path to image")
parser.add_argument("block_size", nargs=1, help = "Block size")
parser.add_argument('--smooth', "-s", action='store_true', help = "Use Gauss for smoothing")
parser.add_argument('--chinese', "-c", action='store_true', help = "Use Chinese alg. instead of Rao's")
args = parser.parse_args()

im = Image.open(args.image[0])
im = im.resize((300, 300))
im = im.convert("L")  # covert to grayscale

W = int(args.block_size[0])

f = lambda x, y: 2 * x * y
g = lambda x, y: x ** 2 - y ** 2

if args.chinese:
    normalizator = 255.0
    f = lambda x, y: 2 * x * y / (normalizator ** 2)
    g = lambda x, y: ((x ** 2) * (y ** 2)) / (normalizator ** 4)

angles = calculate_angles(im, W, f, g)
angles_image = draw_lines(im, angles, W)
angles_image.show()
angles_image.save("angles_image.jpg")

if args.smooth:
    smoothed_angles = smooth_angles(angles)
    smooth_angles_image = draw_lines(im, smoothed_angles, W)
    smooth_angles_image.show()
    smooth_angles_image.save("smooth_angles_image.jpg")
