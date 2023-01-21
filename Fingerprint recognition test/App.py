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

def run_app_gui(image):
    fingerprint_image = cv2.imread(image) # get checking image in RBG 3d format
    
    resized_fingerprint_image = cv2.resize(fingerprint_image, None, fx=2.5, fy=2.5) # resize image checking image by 2.5x
    # cv2.imshow("Original", resized_fingerprint_image)
    
    gray_scale_image = cv2.cvtColor(resized_fingerprint_image, cv2.COLOR_BGR2GRAY) # convert 3d RGB image to grayscale 2d image

    # cv2.imshow(S"Gray scale", gray_scale_image)

    thin_image = fingerprint_pipline(gray_scale_image, echo=True, topic="Checking Image") 
    
    # cv2.imshow("Thin Image", thin_image)
    
    result = verify_fingerprint(thin_image)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return result
    
def run_app(image, path):
    fingerprint_image = cv2.imread(image)
    # fingerprint_image = cv2.imread("Fingerprints samples/test/1__M_Left_index_finger.BMP")
    
    resized_fingerprint_image = cv2.resize(fingerprint_image, None, fx=2.5, fy=2.5)
    # cv2.imshow("Original", resized_fingerprint_image)
    
    gray_scale_image = cv2.cvtColor(resized_fingerprint_image, cv2.COLOR_BGR2GRAY)

    # cv2.imshow("Gray scale", gray_scale_image)
    thin_image = fingerprint_pipline(gray_scale_image, echo=True, topic="Checking Image")
    im = Image.fromarray(thin_image)
    im.save(path)
    # cv2.imshow("Thin Image", thin_image)
    
    # verify_fingerprint(thin_image)
    
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
        # im = Image.fromarray(fingerprint_image)
        # im.save("temp01.jpg")
        # cv2.imshow("Thin Image 2", fingerprint_image)
        
        sift = cv2.SIFT_create()
        keypoints_1, descriptors_1 = sift.detectAndCompute(originla_fingerprint_image, None)
        keypoints_2, descriptors_2 = sift.detectAndCompute(fingerprint_image, None)
        print(len(keypoints_1))
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
    
    return [filename, best_score]

def fingerprint_pipline(input_img,echo=False, topic=""):
    print(input_img.shape)
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
    # thinning or skeletonize
    thin_image = skeletonize(gabor_img)

    # # minutias
    # minutias = calculate_minutiaes(thin_image)

    # singularities
    # singularities_img = calculate_singularities(thin_image, angles, 1, block_size, mask)
    # cv2.imshow("Singular points", singularities_img)
    # visualize pipeline stage by stage
    # output_imgs = [input_img, normalized_img, segmented_img, orientation_img, gabor_img, thin_image]
    # for i in range(len(output_imgs)):
    #     # cv2.imshow("1", output_imgs[i])
    #     if len(output_imgs[i].shape) == 2:
    #         output_imgs[i] = cv2.cvtColor(output_imgs[i], cv2.COLOR_GRAY2RGB)
    # results = np.concatenate([np.concatenate(output_imgs[:2], 1), np.concatenate(output_imgs[2:4], 1), np.concatenate(output_imgs[4:6], 1)]).astype(np.uint8)
    # if echo:
    #     cv2.imshow(topic, results)
    return thin_image

def convert_fp_db(database_path, saving_path):
    # convert files in  database_path
    folder_path = database_path
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    # folder_path = "FP dataset/Real"
    # if not os.path.exists(folder_path):
    #     os.mkdir(folder_path)
    
    # folder_path = folder_path + "/"
    
    count = 1
        
    for file in os.listdir(database_path):
        file_name = file.split(".")[0]
        
        input_name = database_path + file
        dest_name = saving_path + file_name + ".jpg"

        if os.path.isfile(dest_name):
            print(count, "C",input_name, dest_name)
        else:
            print(count, "NC", input_name, dest_name)
            run_app(input_name, dest_name)

        count = count + 1

    print("Total : " + str(count - 1))

def convert_bmp_to_jpg():
    # convert files in  SOCOFing/real
    folder_path = "FP dataset"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = "FP dataset/Real"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = folder_path + "/"
    
    count = 1
        
    for file in os.listdir("SOCOFing/Real"):
        file_name = file.split(".")[0]
        
        input_name = "SOCOFing/Real/" + file
        dest_name = folder_path + file_name + ".jpg"

        if os.path.isfile(dest_name):
            print(count, "C",input_name, dest_name)
        else:
            print(count, "NC", input_name, dest_name)
            run_app(input_name, dest_name)

        count = count + 1
    
    print("Real : " + str(count))
    # convert files in  SOCOFing/Altered/Altered-Easy
    folder_path = "FP dataset"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = "FP dataset/Altered"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        
    folder_path = "FP dataset/Altered/Altered-Easy"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = folder_path + "/"
    
    count = 1
    for file in [file for file in os.listdir("SOCOFing/Altered/Altered-Easy")]:
        file_name = file.split(".")[0]
        
        input_name = "SOCOFing/Altered/Altered-Easy/" + file
        dest_name = folder_path + file_name + ".jpg"

        if os.path.isfile(dest_name):
            print(count, "C",input_name, dest_name)
        else:
            print(count, "NC", input_name, dest_name)
            run_app(input_name, dest_name)
        count = count + 1
    
    print("Altered-Easy : " + str(count))
    # convert files in  SOCOFing/Altered/Altered-Medium
    folder_path = "FP dataset"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = "FP dataset/Altered"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        
    folder_path = "FP dataset/Altered/Altered-Medium"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = folder_path + "/"
    
    count = 1
    for file in [file for file in os.listdir("SOCOFing/Altered/Altered-Medium")]:
        file_name = file.split(".")[0]
        
        input_name = "SOCOFing/Altered/Altered-Medium/" + file
        dest_name = folder_path + file_name + ".jpg"

        if os.path.isfile(dest_name):
            print(count, "C",input_name, dest_name)
        else:
            print(count, "NC", input_name, dest_name)
            run_app(input_name, dest_name)
        count = count + 1
        
    print("Altered-Medium : " + str(count))
    # convert files in  SOCOFing/Altered/Altered-Hard
    folder_path = "FP dataset"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = "FP dataset/Altered"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        
    folder_path = "FP dataset/Altered/Altered-Hard"
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    folder_path = folder_path + "/"
    
    count = 1
    for file in [file for file in os.listdir("SOCOFing/Altered/Altered-Hard")]:
        file_name = file.split(".")[0]
        
        input_name = "SOCOFing/Altered/Altered-Hard/" + file
        dest_name = folder_path + file_name + ".jpg"

        if os.path.isfile(dest_name):
            print(count, "C",input_name, dest_name)
        else:
            print(count, "NC", input_name, dest_name)
            run_app(input_name, dest_name)
        count = count + 1
    
    print("Altered-Hard : " + str(count))



def helper_data_generation():
    fingerprint_image = cv2.imread("1__M_Left_index_finger.BMP") # get checking image in RBG 3d format
    
    resized_fingerprint_image = cv2.resize(fingerprint_image, None, fx=3.5, fy=3.5) # resize image checking image by 2.5x
    # cv2.imshow("Original", resized_fingerprint_image)
    
    gray_scale_image = cv2.cvtColor(resized_fingerprint_image, cv2.COLOR_BGR2GRAY) # convert 3d RGB image to grayscale 2d image

    # cv2.imshow(S"Gray scale", gray_scale_image)
    # im = Eight_field_Direction(gray_scale_image)
    block_size = 16

    # normalization -> orientation -> frequency -> mask -> filtering

    # normalization - removes the effects of sensor noise and finger pressure differences.
    normalized_img = gray_scale_image.copy()
    # color threshold
    # threshold_img = normalized_img
    # _, threshold_im = cv.threshold(normalized_img,127,255,cv.THRESH_OTSU)
    # cv.imshow('color_threshold', normalized_img); cv.waitKeyEx()

    # normalisation
    (segmented_img, normim, mask) = create_segmented_and_variance_images(normalized_img, block_size, 0.2)

    # # orientations
    angles = orientation.calculate_angles(normalized_img, W=block_size, smoth=False)
    orientation_img = orientation.visualize_angles(segmented_img, mask, angles, W=block_size)
    
    output_imgs = [gray_scale_image, orientation_img]
    for i in range(len(output_imgs)):
        # cv2.imshow("1", output_imgs[i])
        if len(output_imgs[i].shape) == 2:
            output_imgs[i] = cv2.cvtColor(output_imgs[i], cv2.COLOR_GRAY2RGB)
    results = np.concatenate([np.concatenate(output_imgs[:2], 1)]).astype(np.uint8)
    cv2.imshow("topic", results)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    # run_app("SOCOFing/Real/170__M_Right_thumb_finger.BMP", "FP dataset/Real/170__M_Right_thumb_finger.jpg")
    
    # convert_bmp_to_jpg()
    
    convert_fp_db("DB1_B/", "DB1_B_Converted/")
    
    # run_app("SOCOFing/Real/3__M_Right_middle_finger.BMP", "")
    # helper_data_generation()
    
    
    