from App import capture_new_fp_xyt, enroll_new_fingerprint, verify_fingerprint

from fuzzy_vault_utils.Strings import *
from fuzzy_vault_utils.Constants import *

if __name__ == '__main__':
    
    enroll = False
    
    secret = 81985529216486895
    
    enrolling_fp = "FP dataset/Real/1__M_Left_index_finger.jpg"
    verifying_fp = "FP dataset/Test/Easy/1__M_Left_index_finger_CR.jpg"
    
    
    if enroll:
        print("Start Enrolling")
        #  Enroll a enrolling fingerprint
        good_fp = False
        
        ## Capture a new fingerprint
        good_fp = capture_new_fp_xyt(enrolling_fp)
        
        ## If good fp enroll
        ## else error
        if not good_fp:
            print(APP_RETRY_FP)
        else:
            enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + '.xyt', secret)
    else:
        print("Start Verifying")
        #  Enroll a verifying fingerprint
        good_fp = False
        
        ## Capture a new fingerprint
        good_fp = capture_new_fp_xyt(verifying_fp)
        
        ## If good fp enroll
        ## else error
        if not good_fp:
            print(APP_RETRY_FP)
        else:            
            verify_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + '.xyt')
    
    
    
    