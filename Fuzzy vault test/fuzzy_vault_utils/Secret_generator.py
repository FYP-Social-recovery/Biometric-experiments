import random
from bitstring import BitArray
import secrets


class SecretGenerator:
    @staticmethod
    def get_smallest_secret_length(poly_degree, crc_length, min_size=0, echo=False):
        """ Helper function to return length of smallest secret where secret is:
            - divisible by 8, so that it can be encoded to bytes
            - candidtae secret length + crc_length is divisible by poly_degree + 1
                to be able to split secret into coefficients for polynomial
            :param poly_degree: polynomial degree as int
            :param crc_length: CRC length as int
            :param min_size: minimum bit size as int
            :param echo: if True, printing intermediate messages to console
            :returns a number """

        secret_bytes = SecretGenerator.smallest_secret_bytes(poly_degree, crc_length, min_size, echo=echo)

        return len(secret_bytes)
    
    @staticmethod
    def generate_smallest_secret(poly_degree, crc_length, min_size=0, echo=False):
        """ Helper function to generate smallest secret which is:
            - divisible by 8, so that it can be encoded to bytes
            - candidtae secret length + crc_length is divisible by poly_degree + 1
                to be able to split secret into coefficients for polynomial
            :param poly_degree: polynomial degree as int
            :param crc_length: CRC length as int
            :param min_size: minimum bit size as int
            :param echo: if True, printing intermediate messages to console
            :returns bytes """

        secret_bytes = SecretGenerator.smallest_secret_bytes(poly_degree, crc_length, min_size, echo=echo)
        
        return secret_bytes
    
    @staticmethod
    def smallest_secret_bytes(poly_degree, crc_length, min_size=0, echo=False):
        """ Helper function to generate smallest secret:
            :param poly_degree: polynomial degree as int
            :param crc_length: CRC length as int
            :param min_size: minimum bit size as int
            :param echo: if True, printing intermediate messages to console
            :returns bytes """

        if min_size % 8 == 0:
            candidate_size = min_size
        else:
            candidate_size = min_size + (8 - (min_size % 8))
        assert candidate_size % 8 == 0
        while not ((candidate_size + crc_length) % (poly_degree + 1) == 0):
            candidate_size += 8
        
        # generate random secret
        secret_int = random.randint(0, 2 ** candidate_size - 1)
        assert candidate_size % 8 == 0
        secret_bytes = secret_int.to_bytes(candidate_size // 8, byteorder='big')
        if echo:
            print('Secret int', secret_int)
            print('Secret size is {} bits'.format(candidate_size))
            print('Secret bytes are {}'.format(secret_bytes))
        return secret_bytes
    
    @staticmethod
    def generate_smallest_secret_with_predefined_secret(poly_degree, crc_length, secret, min_size=0, echo=False):
        """ Helper function to generate smallest secret which is:
            - divisible by 8, so that it can be encoded to bytes
            - candidtae secret length + crc_length is divisible by poly_degree + 1
                to be able to split secret into coefficients for polynomial
            :param poly_degree: polynomial degree as int
            :param crc_length: CRC length as int
            :param min_size: minimum bit size as int
            :param echo: if True, printing intermediate messages to console
            :returns bytes """

        secret_bytes = SecretGenerator.smallest_secret_bytes_with_predefined_secret(poly_degree, crc_length, secret, min_size, echo=echo)
        
        return secret_bytes
    
    @staticmethod
    def smallest_secret_bytes_with_predefined_secret(poly_degree, crc_length, secret, min_size=0, echo=False):
        """ Helper function to generate smallest secret:
            :param poly_degree: polynomial degree as int
            :param crc_length: CRC length as int
            :param min_size: minimum bit size as int
            :param echo: if True, printing intermediate messages to console
            :returns bytes """

        if min_size % 8 == 0:
            candidate_size = min_size
        else:
            candidate_size = min_size + (8 - (min_size % 8))
        assert candidate_size % 8 == 0
        while not ((candidate_size + crc_length) % (poly_degree + 1) == 0):
            candidate_size += 8
        
        secret_length = min_size
        
        # Generate a random n-bit integer number (candidate_size - secret_length)
        random_number = secrets.randbits(candidate_size - secret_length)

        # convert the decimal numbers to hex numbers
        secret = hex(secret)
        random_number = hex(random_number)

        #remove the '0x' prefix from the hex numbers
        secret = int(secret,16)
        random_number = int(random_number,16)

        #concatenate secret and random_number using bitwise left shift and bitwise OR
        concatenated_secret_int = (secret << (candidate_size-secret_length)) | random_number
        
        # # generate random secret
        # secret_int = random.randint(0, 2 ** candidate_size - 1)
        
        assert candidate_size % 8 == 0
        secret_bytes = concatenated_secret_int.to_bytes(candidate_size // 8, byteorder='big')
        if echo:
            print('Secret int', concatenated_secret_int)
            print('Secret size is {} bits'.format(candidate_size))
            print('Secret bytes are {}'.format(secret_bytes))
        return secret_bytes
    
    @staticmethod
    def extract_secret_from_polynomial(poly, crc_length, secret_length, degree):
        """ Extract bitstring from polynomial coefficients and checks if CRC is correct
            :param poly: list of coefficients of polynomial
            :param degree: degree of the polynomial
            :param crc_length: length of the CRC in bits as int
            :param secret_length: length of the secret in bits as int
            :returns if CRC in polynomial encoding (secret) is correct as boolean"""
        # strip leading coefficients that are greater than degree + 1
        poly = poly[len(poly) - (degree + 1):]
        result = BitArray()
        assert (crc_length + secret_length) % (degree + 1) == 0
        coefficient_length = (crc_length + secret_length) // (degree + 1)
        for coefficient in poly:
            # if coefficient is bigger than supposed to CRC is definitely not correct
            if coefficient.bit_length() > coefficient_length:
                return False
            result.append(BitArray(uint=coefficient, length=coefficient_length))

        secret = result[:-crc_length].uint

        return secret
    
    @staticmethod
    def extract_secret_from_polynomial_for_predefined_secret(poly, crc_length, secret_length, degree, min_size=0):
        """ Extract bitstring from polynomial coefficients and checks if CRC is correct
            :param poly: list of coefficients of polynomial
            :param degree: degree of the polynomial
            :param crc_length: length of the CRC in bits as int
            :param secret_length: length of the secret in bits as int
            :returns if CRC in polynomial encoding (secret) is correct as boolean"""
        # strip leading coefficients that are greater than degree + 1
        poly = poly[len(poly) - (degree + 1):]
        result = BitArray()
        assert (crc_length + secret_length) % (degree + 1) == 0
        coefficient_length = (crc_length + secret_length) // (degree + 1)
        for coefficient in poly:
            # if coefficient is bigger than supposed to CRC is definitely not correct
            if coefficient.bit_length() > coefficient_length:
                return False
            result.append(BitArray(uint=coefficient, length=coefficient_length))

        secret = result[:-crc_length].uint

        secret = secret >> (secret_length-min_size)
        
        return secret