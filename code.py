import touchid
import curses
import hashlib
# import smtplib
import json
import os
import platform
from email.message import EmailMessage
from cryptography.fernet import Fernet
from getpass import getpass
from dotenv import load_dotenv

class PasswordManager:
    def __init__(self):
        self.passwords = {}
        self.secret_question = ""
        self.secret_answer = ""
        self.email = ""
        self.master_password = None
        self.load_master_password()
        
    def detect_os(self):
        return platform.system()

    def load_master_password(self):
        if os.path.exists("master.txt"):
            with open("master.txt", "r") as f:
                self.master_password = f.read().strip()
        else:
            self.master_password = hashlib.sha256(getpass("Set a master password: ").encode()).hexdigest()
            with open("master.txt", "w") as f:
                f.write(self.master_password)

    def verify_master_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest() == self.master_password

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_password(self, website, username, password):
        hashed_password = self.hash_password(password)
        if website not in self.passwords:
            self.passwords[website] = {'username': username, 'password': hashed_password, 'raw_password': password}
            print("Password added successfully!")
        else:
            print("Website already exists. Use update_password() to modify the password.")

    def retrieve_password(self, website):
        if (self.detect_os() == "Darwin"):
            try:
                touchid.authenticate()
                print("Touch ID authenticated!!")
            except Exception as e:
                print(f"Touch ID authentication failed: {e}")
        elif (self.detect_os() == "Windows"):
            print("INSERT WINDOWS PIN")

        if website in self.passwords:
            # if not self.secret_answer:
            #     print("Secret answer not set. Please set a secret question and answer first.")
            #     return
            # secret_input = getpass("Enter your secret answer: ")
            # if hashlib.sha256(secret_input.encode()).hexdigest() != self.secret_answer:
            #     print("Incorrect secret answer.")
            #     return
            data = self.passwords[website]
            print(f"Website: {website}\nUsername: {data['username']}\nPassword: {data['raw_password']} (Hashed: {data['password']})")
        else:
            print("Website not found in the password manager.")

    def update_password(self, website, new_password):
        if website in self.passwords:
            self.passwords[website]['password'] = self.hash_password(new_password)
            self.passwords[website]['raw_password'] = new_password
            print("Password updated successfully!")
        else:
            print("Website not found in the password manager.")

    def display_all_passwords(self):
        # if not self.secret_answer:
        #     print("Secret answer not set. Please set a secret question and answer first.")
        #     return
        # secret_input = getpass("Enter your secret answer to display all passwords: ")
        # if hashlib.sha256(secret_input.encode()).hexdigest() != self.secret_answer:
        #     print("Incorrect secret answer.")
        #     return

        if (self.detect_os() == "Darwin"):
            try:
                touchid.authenticate()
                print("Touch ID authenticated!!")
            except Exception as e:
                print(f"Touch ID authentication failed: {e}")
        elif (self.detect_os() == "Windows"):
            print("INSERT WINDOWS PIN")

        if not self.passwords:
            print("No passwords stored.")
        else:
            print("\nAll Stored Passwords:")
            for website, data in self.passwords.items():
                print(f"Website: {website}\nUsername: {data['username']}\nPassword: {data['raw_password']} (Hashed: {data['password']})\n")

    # def set_secret_question(self, email, question, answer):
    #     self.email = email
    #     self.secret_question = question
    #     self.secret_answer = hashlib.sha256(answer.encode()).hexdigest()
    #     self.send_email()

    # def send_email(self):
    #     sender_email = "dananderson0812@gmail.com"  # Replace with your Gmail address
    #     sender_password = "grdf vuae nccn ppcl"  # Use an app-specific password

    #     message = EmailMessage()
    #     message.set_content(f"Your secret question: {self.secret_question}")
    #     message["Subject"] = "Your Secret Question for VaultGuard"
    #     message["From"] = sender_email
    #     message["To"] = self.email

    #     try:
    #         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    #             server.login(sender_email, sender_password)
    #             server.send_message(message)
    #         print("Secret question sent to your email.")
    #     except Exception as e:
    #         print(f"Failed to send email: {e}")

    def export_passwords(self, file_name):
        try:
            secret_answer = getpass("Enter your secret answer: ")
            key = hashlib.sha256(secret_answer.encode()).digest()
            cipher = Fernet(Fernet.generate_key())
            encrypted_data = cipher.encrypt(json.dumps(self.passwords).encode())

            with open(file_name, "wb") as file:
                file.write(cipher.encrypt(key) + b"\n" + encrypted_data)

            print("Passwords exported and encrypted successfully!")
        except Exception as e:
            print(f"Failed to export passwords: {e}")

    def decrypt_passwords(self, file_name):
        try:
            if not os.path.exists(file_name):
                print("File not found.")
                return

            secret_answer = getpass("Enter your secret answer: ")
            key = hashlib.sha256(secret_answer.encode()).digest()

            with open(file_name, "rb") as file:
                lines = file.readlines()
            cipher_key = Fernet(lines[0]).decrypt(key)
            decrypted_data = Fernet(cipher_key).decrypt(lines[1]).decode()

            self.passwords = json.loads(decrypted_data)
            print("Passwords successfully decrypted and loaded.")
        except Exception as e:
            print(f"Failed to decrypt passwords: {e}")


def main():
    safe = PasswordManager()

    if (platform.system() == "Darwin"):
        try:
            touchid.authenticate()
            print("Touch ID authenticated!!")
        except Exception as e:
            print(f"Touch ID authentication failed: {e}")
            return
            # entered_password = getpass("Enter your master password: ")
            # if not safe.verify_master_password(entered_password):
            #     print("Incorrect master password.")
            #     return
    elif (platform.system() == "Windows"):
        print("INSERT WINDOWS PIN")

    while True:
        print("\nVaultGuard Password Manager")
        print("1. Add Password")
        print("2. Retrieve Password")
        print("3. Update Password")
        print("4. Display All Passwords")  # New option added
        # print("5. Set Secret Question and Email")
        print("6. Export and Encrypt Passwords")
        print("7. Decrypt and Load Passwords")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            website = input("Enter website: ")
            username = input("Enter username: ")
            password = getpass("Enter password: ")
            safe.add_password(website, username, password)
        elif choice == '2':
            website = input("Enter website: ")
            safe.retrieve_password(website)
        elif choice == '3':
            website = input("Enter website: ")
            new_password = getpass("Enter new password: ")
            safe.update_password(website, new_password)
        elif choice == '4':
            safe.display_all_passwords()  # New function call
        # elif choice == '5':
        #     email = input("Enter your email to save the secret question: ")
        #     question = input("Enter a secret question: ")
        #     answer = getpass("Enter the answer to the secret question: ")
        #     safe.set_secret_question(email, question, answer)
        elif choice == '6':
            file_name = input("Enter file name to save passwords (e.g., passwords.enc): ")
            safe.export_passwords(file_name)
        elif choice == '7':
            file_name = input("Enter file name to decrypt passwords (e.g., passwords.enc): ")
            safe.decrypt_passwords(file_name)
        elif choice == '8':
            print("Exiting VaultGuard. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
