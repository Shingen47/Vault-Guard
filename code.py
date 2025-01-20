import hashlib
import smtplib
from email.message import EmailMessage
from cryptography.fernet import Fernet
import os

class PasswordManager:
    def __init__(self):
        self.passwords = {}
        self.secret_question = ""
        self.secret_answer = ""
        self.email = ""

    def hash_password(self, password):
        # Hash the password using SHA-256
        return hashlib.sha256(password.encode()).hexdigest()

    def add_password(self, website, username, password):
        hashed_password = self.hash_password(password)
        if website not in self.passwords:
            self.passwords[website] = {'username': username, 'password': hashed_password}
            print("Password added successfully!")
        else:
            print("Website already exists. Use update_password() to modify the password.")

    def retrieve_password(self, website):
        if website in self.passwords:
            username = self.passwords[website]['username']
            password = self.passwords[website]['password']
            print(f"Website: {website}\nUsername: {username}\nPassword (hashed): {password}")
        else:
            print("Website not found in the password manager.")

    def update_password(self, website, new_password):
        if website in self.passwords:
            self.passwords[website]['password'] = self.hash_password(new_password)
            print("Password updated successfully!")
        else:
            print("Website not found in the password manager.")

    def set_secret_question(self, email, question, answer):
        self.email = email
        self.secret_question = question
        self.secret_answer = answer
        self.send_email()

    def send_email(self):
        sender_email = "dananderson0812@gmail.com"  # Replace with your Gmail address
        sender_password = "grdf vuae nccn ppcl"  # Replace with your Gmail app password

        message = EmailMessage()
        message.set_content(f"Your secret question: {self.secret_question}")
        message["Subject"] = "Your Secret Question for Password Manager"
        message["From"] = sender_email
        message["To"] = self.email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(message)
            print("Secret question sent to your email.")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def export_passwords(self, file_name):
        try:
            key = hashlib.sha256(self.secret_answer.encode()).digest()
            cipher = Fernet(Fernet.generate_key())
            encrypted_data = cipher.encrypt(str(self.passwords).encode())

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

            secret_answer = input("Enter your secret answer: ")
            key = hashlib.sha256(secret_answer.encode()).digest()

            with open(file_name, "rb") as file:
                lines = file.readlines()
            cipher_key = Fernet(lines[0]).decrypt(key)
            decrypted_data = Fernet(cipher_key).decrypt(lines[1]).decode()

            self.passwords = eval(decrypted_data)
            print("Passwords successfully decrypted and loaded.")
        except Exception as e:
            print(f"Failed to decrypt passwords: {e}")

def main():
    safe = PasswordManager()

    while True:
        print("\nWelcome to The Safe - Password Manager")
        print("1. Add Password")
        print("2. Retrieve Password")
        print("3. Update Password")
        print("4. Set Secret Question and Email")
        print("5. Export and Encrypt Passwords")
        print("6. Decrypt and Load Passwords")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            website = input("Enter website: ")
            username = input("Enter username: ")
            password = input("Enter password: ")
            safe.add_password(website, username, password)
        elif choice == '2':
            website = input("Enter website: ")
            safe.retrieve_password(website)
        elif choice == '3':
            website = input("Enter website: ")
            new_password = input("Enter new password: ")
            safe.update_password(website, new_password)
        elif choice == '4':
            email = input("Enter your email to save the secret question: ")
            question = input("Enter a secret question: ")
            answer = input("Enter the answer to the secret question: ")
            safe.set_secret_question(email, question, answer)
        elif choice == '5':
            file_name = input("Enter file name to save passwords (e.g., passwords.enc): ")
            safe.export_passwords(file_name)
        elif choice == '6':
            file_name = input("Enter file name to decrypt passwords (e.g., passwords.enc): ")
            safe.decrypt_passwords(file_name)
        elif choice == '7':
            print("Exiting The Safe. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
