""" Fuzzy vault experiment with fingerprint as biometric trait """


from fuzzy_vault_utils.Chaff_Points_Generator import ChaffPointsGenerator
from fuzzy_vault_utils.Minutia_Converter import MinutiaConverter
from fuzzy_vault_utils.Minutiae_Extractor import MinutiaeExtractor
from fuzzy_vault_utils.Polynomial_Generator import PolynomialGenerator
from fuzzy_vault_utils.Secret_generator import SecretGenerator
from fuzzy_vault_utils.Strings import *
from fuzzy_vault_utils.Constants import *

import random
import os
from PIL import Image
from subprocess import Popen, PIPE
from fuzzy_vault_utils.Vault import Vault

from fuzzy_vault_utils.Vault_Verifier import VaultVerifier

def capture_new_fp_xyt(capturing_fp, echo=False):
    """
    input fingerprint image of type .jpg
    Use mindtct to extract .xyt file from .jpg
    Check if there are enough minutiae detected according to MINUTIAE_POINTS_AMOUNT
    :return: True if enough minutiae detected, else False
    """
    # Tries to read image convert to 
    try:
        # Current image destination folder path and save to new image
        if not os.path.exists(FP_TEMP_FOLDER):
            os.mkdir(FP_TEMP_FOLDER)

        img = Image.open(capturing_fp)
        image_destination_jpg = FP_TEMP_FOLDER + FP_OUTPUT_NAME + '.jpg'
        img.save(image_destination_jpg)
        
        if echo:
            print('The image of %s was saved to %s.' % (FP_OUTPUT_NAME, FP_TEMP_FOLDER))
            print('Finished capturing fingerprint %s.\n' % FP_OUTPUT_NAME)

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        raise Exception('An internal error occurred.')
    
    run_mindtct(FP_TEMP_FOLDER + FP_OUTPUT_NAME + '.jpg')
    
    # amount of minutiae in .xyt
    num_lines = sum(1 for _ in open(FP_TEMP_FOLDER + FP_OUTPUT_NAME + '.xyt'))
    if num_lines >= MINUTIAE_POINTS_AMOUNT:
        if echo:
            print('{} minutiae were found...'.format(num_lines))
        return True
    else:
        if echo:
            print('Unfortunately, only {} minutiae were found...'.format(num_lines))
        return False

def run_mindtct(image_path):
    """ Runs mindtct on xyt file path"""
    
    if not os.path.exists(FP_TEMP_FOLDER):
            os.mkdir(FP_TEMP_FOLDER)
            
    mindtct = Popen(['mindtct', image_path, FP_TEMP_FOLDER + FP_OUTPUT_NAME], stdout=PIPE, stderr=PIPE)
    mindtct.communicate()

def enroll_new_fingerprint(xyt_path, secret):
    # calculate secret according to polynomial degree. secret has to be able to be encoded in bytes (*8)
    secret_bytes = SecretGenerator.generate_smallest_secret_with_predefined_secret(POLY_DEGREE, CRC_LENGTH, secret, min_size=128, echo=True)
    print(APP_FV_SECRET)

    fuzzy_vault = generate_vault(xyt_path, MINUTIAE_POINTS_AMOUNT, CHAFF_POINTS_AMOUNT, POLY_DEGREE,
                                 secret_bytes, CRC_LENGTH, GF_2_M, echo=False)
    
    fuzzy_vault.log_vault()
    
    print(APP_FV_GENERATED)

    print('\n')
    print(APP_ENROLL_SUCCESS)

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
        # print("Genuin minutiae : ", genuine_minutiae_list)
    for minutia in genuine_minutiae_list:
        vault.add_minutia_rep(m2b.get_uint_from_minutia(minutia))
    
    # create chaff points and add to vault
    chaff_points_list = ChaffPointsGenerator.generate_chaff_points_randomly(chaff_points_amount, genuine_minutiae_list,
                                                                            vault.get_smallest_original_minutia(), m2b)
    for chaff_point in chaff_points_list:
        vault.add_chaff_point_rep(m2b.get_uint_from_minutia(chaff_point))
    
    if echo:
        print("Amount of chaff points : ", len(chaff_points_list))
        # print("Chaff minutiae : ", chaff_points_list)
        
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

def verify_fingerprint(xyt_path):

    db_vault = Vault()
    db_vault.read_vault() # retrieve vault
    
    if db_vault:
        # calculating secret length according to poly degree and crc
        secret_length = SecretGenerator.get_smallest_secret_length(POLY_DEGREE, CRC_LENGTH, min_size=128, echo=False) * 8
            
        db_vault.create_geom_table()
        success = verify_secret(xyt_path, MINUTIAE_POINTS_AMOUNT, POLY_DEGREE, CRC_LENGTH, secret_length,
                                GF_2_M, db_vault, echo=False)
        
        db_vault.clear_vault()
        if success:
            print("Generated secret is : ", SecretGenerator.extract_secret_from_polynomial_for_predefined_secret(success, CRC_LENGTH, secret_length, POLY_DEGREE, min_size=128))
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

    
