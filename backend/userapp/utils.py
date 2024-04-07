
import string
import random
from .models import User

def generate_referral_code(user):
    # Generate a random code
    code_length = 6
    characters = string.ascii_letters + string.digits
    referral_code = ''.join(random.choice(characters) for _ in range(code_length))

    # Ensure the generated code is unique
    while User.objects.filter(referral_code=referral_code).exists():
        referral_code = ''.join(random.choice(characters) for _ in range(code_length))

    return referral_code