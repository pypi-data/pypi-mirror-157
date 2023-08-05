import hashlib
import jwt
import base64
import os

def salt(text):
    """
    Generates A reel44 based Salt For Double Security Of Your Confidential Data..
    """
    reel44_salt_0 = base64.b64encode(base64.b64encode(bytes(text.encode('utf-8'))))
    hash = hashlib.sha256(reel44_salt_0)
    reel44_salt_1 = str(jwt.encode({"":str(hash.hexdigest())}, 'reel44-keshriinfotech394859', algorithm="HS256"))
    
    return reel44_salt_1

def encrypt(encrypt, salt):
    
    """
    This Function Encrypts The Data That Is Provided. A Salt Is Important For This Function To Work Properly and Encrypt The Data.
    """
    
    encrypt_pass = encrypt.encode('utf-8')
    hash = hashlib.new('sha256',encrypt_pass)
    hash = hashlib.new('sha1',encrypt_pass)
    hash = hashlib.new('sha224',encrypt_pass)
    #hash = hashlib.new('shake_256',encrypt_pass)
    
    encrypted_text_0 = str(jwt.encode({"":str(hash.hexdigest())}, str(salt), algorithm="HS256"))
    #(salt))
    
    return f'{encrypted_text_0}??{salt}'

def match(match_with, match_to):
    """
    Match-With and Match-To Should Both Be In Encrypted Form.
    The Encrypted Form Should Be Generated From reel44 Only.
    If Not Done So, Exception Would Be Throwed.
    """
    try:
        salt_with = match_with.split('??', 1)[1]
        salt_to = match_to.split('??', 1)[1]
        
        match_1 = match_with
        match_2 = match_to
        

        if match_1 == match_2:
            if salt_with == salt_to:
                return True
            else:
                return False, 'Salt Of Both Match-With and Match-To Must Match, Which In This Case Does Not.'
        
        elif match_1 != match_2:
            return False
        
        elif len(int(salt_with))<=5 or len(int(salt_to))>=5:
            return f'Invalid Salt'
        
    except TypeError:
        raise TypeError("Match-With and Match-To are Both The Parameters That Are Required For This Function")
    except IndexError:
        raise IndexError('''Either Match-With or Match-To Is Not Encrypted From Our Library Or Has Been Wrongly Modified.
To Fix This Issue Again Encrypt The Data And Then Try To Match.
If Still Not Works, Write To Us.''')