import random
import string

def generate_random_password(length):
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation

    password_chars = letters + digits + special_chars
    password = ''.join(random.choice(password_chars) for i in range(length))
    
    return password
if __name__ == '__main__':
    pass
