from fileinput import filename
import cv2
import numpy as np
import os

from utils.poincare import calculate_singularities
from utils.segmentation import create_segmented_and_variance_images
from utils.normalization import normalize
from utils.gabor_filter import gabor_filter
from utils.frequency import ridge_freq
from utils import orientation
from utils.crossing_number import calculate_minutiaes
from tqdm import tqdm
from utils.skeletonize import skeletonize

def run_app():
    fingerprint_image = cv2.imread("Fingerprints samples/Altered/1__M_Left_index_finger_CR hard.BMP")
    
    resized_fingerprint_image = cv2.resize(fingerprint_image, None, fx=2.5, fy=2.5)
    # cv2.imshow("Original", resized_fingerprint_image)
    
    gray_scale_image = cv2.cvtColor(resized_fingerprint_image, cv2.COLOR_BGR2GRAY)

    # cv2.imshow("Gray scale", gray_scale_image)

    thin_image = fingerprint_pipline(gray_scale_image, echo=True, topic="Checking Image")
    
    # cv2.imshow("Thin Image", thin_image)
    
    verify_fingerprint(thin_image)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def verify_fingerprint(originla_fingerprint_image):
    best_score = 0
    filename = None
    image = None
    kp1, kp2, mp = None, None, None
    count = 0
    for file in [file for file in os.listdir("Fingerprints samples/test")]:
        fingerprint_image = cv2.imread("Fingerprints samples/test/"+file)
        
        fingerprint_image = cv2.cvtColor(fingerprint_image, cv2.COLOR_BGR2GRAY)
        fingerprint_image = cv2.resize(fingerprint_image, None, fx=2.5, fy=2.5)
        # cv2.imshow("Original 2", fingerprint_image)
        fingerprint_image = fingerprint_pipline(fingerprint_image, echo=True, topic=file)
        
        # cv2.imshow("Thin Image 2", fingerprint_image)
        
        sift = cv2.SIFT_create()
        keypoints_1, descriptors_1 = sift.detectAndCompute(originla_fingerprint_image, None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(fingerprint_image, None)
        
        # output_image_2 = cv2.drawKeypoints(fingerprint_image, keypoints_2, 0, (0, 0, 255),
        #                          flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
        # output_image_2 = cv2.resize(output_image_2, None, fx=2.5, fy=2.5)
        # cv2.imshow("output_image_2", output_image_2)
        
        matches = cv2.FlannBasedMatcher(dict(algorithm=1, trees=10), 
                    dict()).knnMatch(descriptors_1, descriptors_2, k=2)
        
        match_points = []

        for p, q in matches:
            if p.distance < 0.1*q.distance:
                match_points.append(p)

        keypoints = len(keypoints_2) 
        print(len(keypoints_1))
        print(len(keypoints_2))
        print(len(match_points))
        # if len(keypoints_1) <= len(keypoints_2):
        #     keypoints = len(keypoints_1)            
        # else:
        #     keypoints = len(keypoints_2)
            
        print(count, "  ", file, "  ", (len(match_points) / keypoints * 100))
        
        if (len(match_points) / keypoints * 100)>best_score:
            best_score = len(match_points) / keypoints * 100
            filename = file
            image = fingerprint_image
            
            kp1, kp2, mp = keypoints_1, keypoints_2, match_points
        count = count + 1
        
    print("BEST MATCH: ", filename)
    print("SCORE : ", best_score)
    result = cv2.drawMatches(originla_fingerprint_image, kp1, image, kp2, mp, None) 
    # result = cv2.resize(result, None, fx=2.5, fy=2.5)
    cv2.imshow("result", result)

def fingerprint_pipline(input_img,echo=False, topic=""):
    block_size = 16

    # normalization -> orientation -> frequency -> mask -> filtering

    # normalization - removes the effects of sensor noise and finger pressure differences.
    normalized_img = normalize(input_img.copy(), float(100), float(100))

    # color threshold
    # threshold_img = normalized_img
    # _, threshold_im = cv.threshold(normalized_img,127,255,cv.THRESH_OTSU)
    # cv.imshow('color_threshold', normalized_img); cv.waitKeyEx()

    # normalisation
    (segmented_img, normim, mask) = create_segmented_and_variance_images(normalized_img, block_size, 0.2)

    # # orientations
    angles = orientation.calculate_angles(normalized_img, W=block_size, smoth=False)
    orientation_img = orientation.visualize_angles(segmented_img, mask, angles, W=block_size)

    # find the overall frequency of ridges in Wavelet Domain
    freq = ridge_freq(normim, mask, angles, block_size, kernel_size=5, minWaveLength=5, maxWaveLength=15)

    # create gabor filter and do the actual filtering
    gabor_img = gabor_filter(normim, angles, freq)

    # thinning oor skeletonize
    thin_image = skeletonize(gabor_img)

    # # minutias
    # minutias = calculate_minutiaes(thin_image)

    # # singularities
    # singularities_img = calculate_singularities(thin_image, angles, 1, block_size, mask)
    
    # visualize pipeline stage by stage
    output_imgs = [input_img, normalized_img, segmented_img, orientation_img, gabor_img, thin_image]
    for i in range(len(output_imgs)):
        # cv2.imshow("1", output_imgs[i])
        if len(output_imgs[i].shape) == 2:
            output_imgs[i] = cv2.cvtColor(output_imgs[i], cv2.COLOR_GRAY2RGB)
    results = np.concatenate([np.concatenate(output_imgs[:2], 1), np.concatenate(output_imgs[2:4], 1), np.concatenate(output_imgs[4:6], 1)]).astype(np.uint8)
    if echo:
        cv2.imshow(topic, results)
    return thin_image

if __name__ == '__main__':
    run_app()