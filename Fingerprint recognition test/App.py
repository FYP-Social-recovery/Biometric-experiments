from fileinput import filename
import cv2
import numpy as np
import os
from PIL import Image

from utils.poincare import calculate_singularities
from utils.segmentation import create_segmented_and_variance_images
from utils.normalization import normalize
from utils.gabor_filter import gabor_filter
from utils.frequency import ridge_freq
from utils import orientation
from utils.crossing_number import calculate_minutiaes
from tqdm import tqdm
from utils.skeletonize import skeletonize

    
def run_app(input_image, output_path):
    # Open fingerprint image
    fingerprint_image = cv2.imread(input_image)

    
    thin_image = fingerprint_pipline(fingerprint_image)
    
    # save image as a jpg
    im = Image.fromarray(thin_image)
    im.save(output_path)

def fingerprint_pipline(input_img):
    block_size = 16

    # grey scale transformation -> normalization -> orientation -> frequency -> mask -> filtering
    
    resized_fingerprint_image = cv2.resize(input_img, None, fx=2.5, fy=2.5)
    
    # rgb image to grey scale transformation
    gray_scale_image = cv2.cvtColor(resized_fingerprint_image, cv2.COLOR_BGR2GRAY)

    # normalization - removes the effects of sensor noise and finger pressure differences.
    normalized_img = normalize(gray_scale_image.copy(), float(100), float(100))

    # normalisation
    (segmented_img, normim, mask) = create_segmented_and_variance_images(normalized_img, block_size, 0.2)
 
    # orientations
    angles = orientation.calculate_angles(normalized_img, W=block_size, smoth=False)
    orientation_img = orientation.visualize_angles(segmented_img, mask, angles, W=block_size)

    # find the overall frequency of ridges in Wavelet Domain
    freq = ridge_freq(normim, mask, angles, block_size, kernel_size=5, minWaveLength=5, maxWaveLength=15)

    # create gabor filter and do the actual filtering
    gabor_img = gabor_filter(normim, angles, freq)
    
    # thinning or skeletonize
    thin_image = skeletonize(gabor_img)

    return thin_image
    
if __name__ == '__main__':
    run_app("1__M_Left_index_finger.BMP", "1__M_Left_index_finger.jpg")
    
    
    