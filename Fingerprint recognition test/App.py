import cv2
from finger_print_pipelne import fingerprint_pipline

if __name__ == '__main__':
    input_image = "1__M_Left_index_finger.BMP"
    output_path = "1__M_Left_index_finger.jpg"
    
    # Open fingerprint image
    fingerprint_image = cv2.imread(input_image)

    thin_image = fingerprint_pipline(fingerprint_image, save_image=True, save_path=output_path)
    
    
    