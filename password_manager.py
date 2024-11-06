import json, hashlib, getpass, os, pyperclip, sys
from cryptography.fernet import Fernet

# function for hashing the master password
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    return sha256.hexdigest()

# generate the secret key, done only once
def generate_key():
    return Fernet.generate_key()

# initialize Fernet cipher with the provided key
def initialize_cipher(key):
    return Fernet(key)

# function to encrypt the password
def encrypt_password(cipher, password):
    return cipher.encrypt(password.encode()).decode()

# function to decrypt password
def decrypt_password(cipher, encrypted_password):
    return cipher.decrypt(encrypted_password.encode()).decode()

# function for owner registration
def register(username, master_password):
    # encrypt master password before storing it
    hashed_master_password = hash_password(master_password)
    user_data = {
        'username': username,
        'master_password': hashed_master_password
    }
    file_name = 'user_data.json'
    if os.path.exists(file_name) and os.path.getsize(file_name) == 0:
        with open(file_name, 'w') as file:
            json.dump(user_data, file)
            print('\n[+] Registration complete!\n')
    else:
        with open(file_name, 'x') as file:
            json.dump(user_data, file)
            print('\n[+] Registration complete!\n')

# function to log in
def login(username, entered_password):
    try:
        with open('user_data.json', 'r') as file:
            user_data = json.load(file)
        stored_password_hash = user_data.get('master_password')
        entered_password_hash = hash_password(entered_password)
        if entered_password_hash == stored_password_hash and username == user_data.get('username'):
            print('\n[+] Login successful\n')
        else:
            print('\n[-] Invalid Login credentials. Please use the credentials you used to register\n')
            sys.exit()
    except Exception:
        print('\n[-] You have not registered yet\n')
        sys.exit()

# function to view saved websites
def view_websites():
    try:
        with open('passwords.json', 'r') as data:
            view = json.load(data)
            print('\nThe websites you saved...\n')
            for x in view:
                print(x['website'])
            print('\n')
    except FileNotFoundError:
        print('\n[-] You have not saved any passwords\n')

# load or generate the encryption key
key_filename = 'encryption_key.key'
if os.path.exists(key_filename):
    with open(key_filename, 'rb') as key_file:
        key = key_file.read()
else:
    key = generate_key()
    with open(key_filename, 'wb') as key_file:
        key_file.write(key)

cipher = initialize_cipher(key)

# function to add passwords
def add_password(website, password):
    # check if password exists
    if not os.path.exists('passwords.json'):
        data = []
    else:
        # load existing passwords
        try:
            with open('passwords.json', 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            # handle the case if file is empty or invalid
            data = []
    # encrypt the password
    encrypted_password = encrypt_password(cipher, password)
    # create a dictionary to store website and a password
    password_entry = {
        'website': website,
        'password': encrypted_password
    }
    data.append(password_entry)
    # save the updated list to passwords.json
    with open('passwords.json', 'w') as file:
        json.dump(data, file, indent=4)

# function to retrieve the password
def get_password(website):
    # check if passwords.json exists
    if not os.path.exists('passwords.json'):
        return None
    # load existing data from passwords.json
    try:
        with open('passwords.json', 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = []
    #looop through all websites and show them
    for entry in data:
        if entry['website'] == website:
            decrypted_password = decrypt_password(cipher, entry['password'])
            return decrypted_password
    return None

# infinite looop

while True:
    print('1. Register')
    print('2. Login')
    print('3. Quit')
    choice = input('Enter your choice: ')
    if choice == '1':
        file = 'user_data.json'
        if os.path.exists(file) and os.path.getsize(file) != 0:
            print('\n[-] Master user exists!!\n')
            sys.exit
        else:
            username = input('Enter your username: ')
            master_password = getpass.getpass('Enter your master password')
            register(username, master_password)
    elif choice == '2':
        file = 'user_data.json'
        if os.path.exists(file):
            username = input('Enter your username: ')
            master_password = getpass.getpass('Enter your master password')
            login(username, master_password)
        else:
            print('\n[-] You have not registered. Please do that\n')
            sys.exit()

        # various options after login
        while True:
            print('1. Add password')
            print('2. Get password')
            print('3. View saved password')
            print('4. Quit')
            password_choice = input('Enter your choice: ')
            if password_choice == '1': 
                website = input('Enter website: ')
                password = getpass.getpass('Enter your password: ')
                add_password(website, password)
                print('\n[+] Password added!!\n')
            elif password_choice == '2': 
                website = input('Enter website: ')
                decrypted_password = get_password(website)
                if website and decrypted_password:
                    # copy password to clipboard for convenience
                    pyperclip.copy(decrypted_password)
                    print(f'\n[+] Password for {website}: {decrypted_password}. Password copied to clipboard\n')
                else:
                    print('\n[-] Password not found! Did you save the password for this website?')
                    print('[-] Use option 3 to see the websites you saved\n')
            elif password_choice == '3':
                view_websites()
            elif password_choice == '4':
                break
    elif choice == '3':
        break
    else:
        print('\nInvalid response!! Please provide a valid choice number\n')




