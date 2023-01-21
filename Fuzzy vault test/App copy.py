""" Fuzzy vault experiment with fingerprint as biometric trait """

from Chaff_Points_Generator import ChaffPointsGenerator
from Minutia_Converter import MinutiaConverter
from Minutiae_Extractor import MinutiaeExtractor
from Polynomial_Generator import PolynomialGenerator
from Secret_generator import SecretGenerator
from Strings import *
from Constants import *

import random
import os
from PIL import Image
from subprocess import Popen, PIPE
from Vault import Vault

from Vault_Verifier import VaultVerifier

def run_app():
    print('========================================================================')
    print(APP_WELCOME)
    print('========================================================================')
    print('\n')

    running = True
    vault = None
    while running:
        # list options for user
        print(APP_CHOOSE_FUNCTION)
        for key in APP_FUNCTIONAILTIES.keys():
            print("%s: %s" % (key, APP_FUNCTIONAILTIES[key]))
        print()

        # get input option from user
        correct_option = False
        input_option = ''
        while not correct_option:
            input_option = input(APP_DESIRED_OPTION)
            if input_option not in APP_FUNCTIONAILTIES.keys():
                print(APP_OPTION_FALSE)
            else:
                correct_option = True

        # Exit application
        if input_option == list(APP_FUNCTIONAILTIES.keys())[2]:
            running = False
            print(APP_BYE)
        # Enroll new fingerprint
        elif input_option == list(APP_FUNCTIONAILTIES.keys())[0]:
            print("Start Enrolling")
            new_id = get_id()

            good_fp = False

            while not good_fp:
                # good_fp = capture_new_fp_xyt(new_id)
                good_fp = capture_new_fp_xyt("fp_temp/temp2.jpg", new_id)
                if not good_fp:
                    print(APP_RETRY_FP)
                    retry_input = input(APP_RETRY_MESSAGE)
                    if(retry_input.lower()=="n"):
                        break
            enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + new_id + "/" +  FP_OUTPUT_NAME + new_id + '.xyt')
                    
        # Verify fingerprint
        elif input_option == list(APP_FUNCTIONAILTIES.keys())[1]:
            print("Start Verifying")
            id_to_verify = get_id()
            print(APP_SCAN_FP)
            
            # Scanning fingerprint, recapture if not enough good minutiae
            good_fp = False

            while not good_fp:
                # good_fp = capture_new_fp_xyt(id_to_verify)
                good_fp = capture_new_fp_xyt("fp_temp/temp2.jpg", id_to_verify)
                if not good_fp:
                    print(APP_RETRY_FP)
                    retry_input = input(APP_RETRY_MESSAGE)
                    if(retry_input.lower()=="n"):
                        break
                    
            # calculating secret length according to poly degree and crc
            secret_length = SecretGenerator.get_smallest_secret_length(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=True) * 8
            
            verify_fingerprint(id_to_verify, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_to_verify + "/" +  FP_OUTPUT_NAME + id_to_verify + '.xyt',
                               secret_length)
            print('\n')
        else:
            print(APP_ERROR)
        print('========================================================================')
        print('\n')

def enroll_fp(new_id):
    # Scanning fingerprint, recapture if not enough good minutiae
    good_fp = False
    
    while not good_fp:
        good_fp = capture_new_fp_xyt(new_id)
        if not good_fp:
            print(APP_RETRY_FP)
            retry_input = input(APP_RETRY_MESSAGE)
            if(retry_input.lower()=="n"):
                break
            
    enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + new_id + "/" +  FP_OUTPUT_NAME + new_id + '.xyt')
    
def verify_fp(id_to_verify):
    # Scanning fingerprint, recapture if not enough good minutiae
    good_fp = False
    
    while not good_fp:
        good_fp = capture_new_fp_xyt(id_to_verify)
        if not good_fp:
            print(APP_RETRY_FP)
            retry_input = input(APP_RETRY_MESSAGE)
            if(retry_input.lower()=="n"):
                break
            
    # calculating secret length according to poly degree and crc
    secret_length = SecretGenerator.get_smallest_secret_length(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=True) * 8
    
    return verify_fingerprint(id_to_verify, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_to_verify + "/" +  FP_OUTPUT_NAME + id_to_verify + '.xyt',
                        secret_length)

def get_id():
    """ Take a input from the user which is:
        - only a integer number """
        
    correct_id = False
    new_id = 0
    while not correct_id:
        new_id = input(APP_NEW_ID)
        if new_id.isdigit():
            new_id = int(new_id)
            correct_id = True
        else:
            print(APP_ID_ERROR)
    return str(new_id)

def capture_new_fp_xyt(opening_image, id_number, echo=False):
    """
    input fingerprint image of type .bmp
    Use mindtct to extract .xyt file from .jpg
    Check if there are enough minutiae detected according to MINUTIAE_POINTS_AMOUNT
    :return: True if enough minutiae detected, else False
    """
    # Tries to read image convert to 
    try:
        image_name = FP_OUTPUT_NAME + str(id_number)

        # Current image destination folder path and save to new image
        folder_path = FP_TEMP_FOLDER
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        if image_name is None:
            image_name = 'fingerprint_' + str(len(os.listdir(folder_path)))
        
        # # open as bitmap
        # image_destination_bmp = folder_path + image_name + '.bmp'
        # print(image_destination_bmp)
        # # save as jpg
        img = Image.open(opening_image)
        # rgb_im = img.convert('L')
        image_destination_jpg = folder_path + image_name + '.jpg'
        img.save(image_destination_jpg)
        if echo:
            print('The image of %s was saved to %s.' % (image_name, folder_path))
            print('Finished capturing fingerprint %s.\n' % image_name)

    except Exception as e:
        print('Operation failed!')
        # print('Exception message: ' + str(e))
        raise Exception('An internal error occurred.')
    
    run_mindtct(FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + '.jpg', id_number)
    
    # amount of minutiae in .xyt
    num_lines = sum(1 for _ in open(FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + "/" + FP_OUTPUT_NAME + id_number + '.xyt'))
    if num_lines >= MINUTIAE_POINTS_AMOUNT:
        print('{} minutiae were found...'.format(num_lines))
        return True
    else:
        print('Unfortunately, only {} minutiae were found...'.format(num_lines))
        return False

def run_mindtct(jpg_path, id_number):
    """ Runs mindtct on xyt file path"""
    
    folder_path = FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + "/"
    
    if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            
    mindtct = Popen(['mindtct', jpg_path, FP_TEMP_FOLDER + FP_OUTPUT_NAME + id_number + "/" +  FP_OUTPUT_NAME + id_number], stdout=PIPE, stderr=PIPE)
    mindtct.communicate()

def enroll_new_fingerprint(xyt_path):
    # calculate secret according to polynomial degree. secret has to be able to be encoded in bytes (*8)
    secret_bytes = SecretGenerator.generate_generate_smallest_secret(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=True)
    print(APP_FV_SECRET)

    fuzzy_vault = generate_vault(xyt_path, MINUTIAE_POINTS_AMOUNT, CHAFF_POINTS_AMOUNT, POLY_DEGREE,
                                 secret_bytes, CRC_LENGTH, GF_2_M, echo=False)
    
    fuzzy_vault.log_vault()
    
    print(fuzzy_vault.vault_final_elements_pairs)
    
    print(APP_FV_GENERATED)

    # send vault to database
    # try:
    #     # store_in_cosmos_db(db_handler, fuzzy_vault, vault_id)
    #     print("Amount of vault value pairs : ", len(fuzzy_vault.vault_final_elements_pairs))
    # except Exception as e:
    #     print('Exception message: ' + str(e))
    #     print('Error occurred during database handling.')
    #     return
    print('\n')
    print(APP_ENROLL_SUCCESS)
    return fuzzy_vault

def generate_vault(xyt_input_path, minutiae_points_amount, chaff_points_amount, poly_degree, secret, crc_length,
                   gf_exp, echo=False):
    # extract minutiae from template
    nbis_minutiae_extractor = MinutiaeExtractor()
    minutiae_list = nbis_minutiae_extractor.extract_minutiae_from_xyt(xyt_input_path)
    if len(minutiae_list) < minutiae_points_amount:
        if echo:
            print('Not enough minutiae in template to proceed for generation of vault...')
        
        return None

    vault = Vault()
    m2b = MinutiaConverter()

    # Cut low quality minutiae and convert all minutiae to uint and add to vault
    genuine_minutiae_list = []
    for candidate in minutiae_list:
        if len(genuine_minutiae_list) == minutiae_points_amount:
            break
        too_close = False
        for minutia in genuine_minutiae_list:
            if candidate.distance_to(minutia) <= POINTS_DISTANCE:
                too_close = True
                break
        if not too_close:
            genuine_minutiae_list.append(candidate)
    if echo:
        print("Amount of genuin minutiae : ", len(genuine_minutiae_list))
        # print("genuin minutiae : ", genuine_minutiae_list)
    for minutia in genuine_minutiae_list:
        vault.add_minutia_rep(m2b.get_uint_from_minutia(minutia))
    
    # create chaff points and add to vault
    chaff_points_list = ChaffPointsGenerator.generate_chaff_points_randomly(chaff_points_amount, genuine_minutiae_list,
                                                                            vault.get_smallest_original_minutia(), m2b)
    for chaff_point in chaff_points_list:
        vault.add_chaff_point_rep(m2b.get_uint_from_minutia(chaff_point))
    
    if echo:
        print("Amount of chaff points : ", len(chaff_points_list))
        # print("chaff minutiae : ", chaff_points_list)
        
    # generate secret polynomial
    secret_poly_generator = PolynomialGenerator(secret, poly_degree, crc_length, gf_exp)
    if echo:
        print('Coefficients of secret polynomial: {}'.format(secret_poly_generator.coefficients))

    # evaluate polynomial at all vault minutiae points (not at chaff points)
    vault.evaluate_polynomial_on_minutiae(secret_poly_generator, echo=echo)

    # generate random evaluation for chaff points
    vault.evaluate_random_on_chaff_points(secret_poly_generator, gf_exp)

    # finalize vault (delete information on vault creation except vault_final_elements_pairs)
    vault.finalize_vault()

    return vault

def verify_fingerprint(vault_id, xyt_path, secret_length):

    db_vault = Vault()
    db_vault.read_vault() # retrieve vault
    
    if db_vault:
        db_vault.create_geom_table()
        success = verify_secret(xyt_path, MINUTIAE_POINTS_AMOUNT, POLY_DEGREE, CRC_LENGTH, secret_length,
                                GF_2_M, db_vault, echo=False)
        
        db_vault.clear_vault()
        if success:
            print("Generated secret is : ", SecretGenerator.extract_secret_from_polynomial(success, CRC_LENGTH, secret_length, POLY_DEGREE))
            print(APP_VERIFY_SUCCESS)
            return True
        else:
            print("Secret generation failed!")
            print(APP_VERIFY_FAILURE)
            return False
        
    else:
        print(APP_VERIFY_FAILURE)
        return False

def verify_secret(xyt_input_path, minutiae_points_amount, poly_degree, crc_length, secret_length, gf_exp, vault: Vault,
                  echo=False):
    """
    :returns: True if match is found, False otherwise
    """
    # extract minutiae from template
    nbis_minutiae_extractor = MinutiaeExtractor()
    minutiae_list = nbis_minutiae_extractor.extract_minutiae_from_xyt(xyt_input_path)

    if len(minutiae_list) < minutiae_points_amount:
        if echo:
            print('Not enough minutiae in template to proceed for extraction of secret...')
        return False

    # extract and restore minutiae from vault using minutiae list from probe, only good quality points taken
    return VaultVerifier.unlock_vault_geom(vault, minutiae_list[0:minutiae_points_amount], poly_degree, gf_exp,
                                           crc_length, secret_length, echo=echo)

def genuin_acceptance_test():
    # calculating secret length according to poly degree and crc
    secret_length = SecretGenerator.get_smallest_secret_length(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=True) * 8
    
    ## veryfying with Hard test set
    # Enroll each FP in FP dataset/Real
    enrolling_folder_path = "FP dataset/Real/"
    # Veryfy each FP in FP dataset/Test/Hard 
    verifying_folder_path = "FP dataset/Test/Hard/"
    
    logging_file_name = "Hard result"
    
    count = 0
    success_count = 0
    
    hard_count = 0
    
    logged_list = []
    if os.path.isfile(logging_file_name + "list"):
        with open(logging_file_name + "list", 'r') as file:
            lines = file.readlines()
            for line in lines:
                file_name = line.strip("\n")
                logged_list.append(file_name)

    for enrolling_file in os.listdir(enrolling_folder_path):
        enrolling_file_name = enrolling_file.split(".")[0]
        
        # enroll FP
        good_fp = False
        
        good_fp = capture_new_fp_xyt(enrolling_folder_path + enrolling_file, "0")

        if not good_fp:
            break
        
        vault = enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + "0" + "/" +  FP_OUTPUT_NAME + "0" + '.xyt')
        
        if vault == None:
            break
        
        if(enrolling_file in logged_list):
            continue
        else:
            with open(logging_file_name + "list", 'a') as file:
                file.write('{}\n'.format(enrolling_file))   
        
        for verifying_file in os.listdir(verifying_folder_path):
            verifying_file_name = verifying_file.split("finger_")[0] + "finger"
            
            if(enrolling_file_name==verifying_file_name):
                count = count + 1
                
                result = "Fail"
                
                # veryfy FP
                good_fp = False
    
                good_fp = capture_new_fp_xyt(verifying_folder_path + verifying_file, "1")

                if not good_fp:
                    break
                
                output = verify_fingerprint("1", FP_TEMP_FOLDER + FP_OUTPUT_NAME + "1" + "/" +  FP_OUTPUT_NAME + "1" + '.xyt',
                                secret_length)
                
                if output:
                    result = "Success"
                else:
                    result = "Fail"
                print(result)
                if result == "Success":
                    success_count = success_count + 1
                with open(logging_file_name, 'a') as file:
                    file.write('{} {} {} {}\n'.format(count, enrolling_file, verifying_file, result))
                  
        # if hard_count == 0:
        #     break
        hard_count += 0  
                        
    print("success_count : " + str(success_count))

        
def total_test():
    # calculating secret length according to poly degree and crc
    secret_length = SecretGenerator.get_smallest_secret_length(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=True) * 8
    
    ## veryfying with Hard test set
    # Enroll each FP in FP dataset/Real
    enrolling_folder_path = "FP dataset/Real/"
    # Veryfy each FP in FP dataset/Test/Hard 
    verifying_folder_path = "FP dataset/Test/Hard/"
    
    logging_file_name = "Hard result"
    
    count = 0
    tot_gac = 0
    tot_fac = 0
    
    hard_count = 0
    
    logged_list = []
    if os.path.isfile(logging_file_name + "list"):
        with open(logging_file_name + "list", 'r') as file:
            lines = file.readlines()
            for line in lines:
                file_name = line.strip("\n")
                logged_list.append(file_name)

    for enrolling_file in os.listdir(enrolling_folder_path):
        enrolling_file_name = enrolling_file.split(".")[0]
        
        # enroll FP
        good_fp = False
        
        good_fp = capture_new_fp_xyt(enrolling_folder_path + enrolling_file, "0")

        if not good_fp:
            break
        
        vault = enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + "0" + "/" +  FP_OUTPUT_NAME + "0" + '.xyt')
        
        if vault == None:
            break
        
        if(enrolling_file in logged_list):
            continue
        else:
            with open(logging_file_name + "list", 'a') as file:
                file.write('{}\n'.format(enrolling_file))   
        fac = 0
        gac = 0
        tot = 0
        for verifying_file in os.listdir(verifying_folder_path):
            verifying_file_name = verifying_file.split("finger_")[0] + "finger"
            
            if(enrolling_file_name==verifying_file_name):
                count = count + 1
                tot = tot + 1
                
                result = "Fail"
                
                # veryfy FP
                good_fp = False
    
                good_fp = capture_new_fp_xyt(verifying_folder_path + verifying_file, "1")

                if not good_fp:
                    break
                
                output = verify_fingerprint("1", FP_TEMP_FOLDER + FP_OUTPUT_NAME + "1" + "/" +  FP_OUTPUT_NAME + "1" + '.xyt',
                                secret_length)
                
                if output:
                    result = "Success"
                else:
                    result = "Fail"

                if result == "Success":
                    tot_gac = tot_gac + 1
                    gac = gac + 1
                with open(logging_file_name+" GA", 'a') as file:
                    file.write('{} {} {} {}\n'.format(count, enrolling_file, verifying_file, result))
            else:
                
                tot = tot + 1
                
                result = "Fail"
                
                # veryfy FP
                good_fp = False
    
                good_fp = capture_new_fp_xyt(verifying_folder_path + verifying_file, "1")

                if not good_fp:
                    break
                
                output = verify_fingerprint("1", FP_TEMP_FOLDER + FP_OUTPUT_NAME + "1" + "/" +  FP_OUTPUT_NAME + "1" + '.xyt',
                                secret_length)
                
                if output:
                    result = "Success"
                else:
                    result = "Fail"
                
                if result == "Success":
                    fac = fac + 1
        with open(logging_file_name + " FA", 'a') as file:
            file.write('{} {} {}\n'.format(count, enrolling_file, str(tot)+"/"+str(fac)))
        tot_fac = tot_fac + fac
        print(str(fac))
                  
        # if hard_count == 0:
        #     break
        hard_count += 0  
                        
    print("tot_gac : " + str(tot_gac))
    print("tot_fac : " + str(tot_fac))

def false_match_test():
    # calculating secret length according to poly degree and crc
    secret_length = SecretGenerator.get_smallest_secret_length(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=True) * 8
    
    ## veryfying with Hard test set
    # Enroll each FP in FP dataset/Real
    enrolling_folder_path = "FP dataset/Real/"
    # Veryfy each FP in FP dataset/Test/Hard 
    verifying_folder_path = enrolling_folder_path #"FP dataset/Test/Hard/"
    
    logging_file_name = "False match result"#"Hard result"
    
    count = 0
    success_count = 0
    
    hard_count = 0
    
    logged_list = []
    if os.path.isfile(logging_file_name + "list"):
        with open(logging_file_name + "list", 'r') as file:
            lines = file.readlines()
            for line in lines:
                file_name = line.strip("\n")
                logged_list.append(file_name)

    for enrolling_file in os.listdir(enrolling_folder_path):
        enrolling_file_name = enrolling_file.split(".")[0]
        
        # enroll FP
        good_fp = False
        
        good_fp = capture_new_fp_xyt(enrolling_folder_path + enrolling_file, "0")

        if not good_fp:
            break
        
        vault = enroll_new_fingerprint(FP_TEMP_FOLDER + FP_OUTPUT_NAME + "0" + "/" +  FP_OUTPUT_NAME + "0" + '.xyt')
        
        if vault == None:
            break
        
        if(enrolling_file in logged_list):
            continue
        else:
            with open(logging_file_name + "list", 'a') as file:
                file.write('{}\n'.format(enrolling_file))   
        
        verify_finger_count = 0
        for verifying_file in os.listdir(enrolling_folder_path):
            # verifying_file_name = verifying_file.split("finger_")[0] + "finger"
            verifying_file_name = verifying_file.split(".")[0]
            
            if verify_finger_count == 20:
                break
            
            if(enrolling_file_name!=verifying_file_name):
                count = count + 1
                
                result = "Fail"
                
                # veryfy FP
                good_fp = False
    
                good_fp = capture_new_fp_xyt(verifying_folder_path + verifying_file, "1")

                if not good_fp:
                    break
                
                output = verify_fingerprint("1", FP_TEMP_FOLDER + FP_OUTPUT_NAME + "1" + "/" +  FP_OUTPUT_NAME + "1" + '.xyt',
                                secret_length)
                
                if output:
                    result = "Success"
                else:
                    result = "Fail"
                print(result)
                if result == "Success":
                    success_count = success_count + 1
                with open(logging_file_name, 'a') as file:
                    file.write('{} {} {} {}\n'.format(count, enrolling_file, verifying_file, result))
                verify_finger_count = verify_finger_count + 1
                  
        if hard_count == 14:
            break
        hard_count = hard_count + 1  
                        
    print("success_count : " + str(success_count))
    
