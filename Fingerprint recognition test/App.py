from finger_print_pipelne import FingerPrintController

if __name__ == '__main__':
    input_image = "1__M_Left_index_finger.BMP"
    
    fingerprint_image = FingerPrintController.read_image(input_image)
    output_path = "1__M_Left_index_finger.jpg"

    thin_image = FingerPrintController.fingerprint_pipline(fingerprint_image, save_image=True, save_path=output_path)
    
    
    