from django.db import models
from django.contrib.auth.models import AbstractUser
import string
import random
# Create your models her
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    referral_code = models.CharField(max_length=20, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
# def save(self, *args, **kwargs):
#         # Generate referral code only if it's not set yet
#         if not self.referral_code:
#             self.generate_referral_code()
#         super(User, self).save(*args, **kwargs)
def generate_referral_code(self):
        # Generate a random code
        code_length = 6
        characters = string.ascii_letters + string.digits
        referral_code = ''.join(random.choice(characters) for _ in range(code_length))

        # Ensure the generated code is unique
        while User.objects.filter(referral_code=referral_code).exists():
            referral_code = ''.join(random.choice(characters) for _ in range(code_length))

        self.referral_code = referral_code
        self.save()
        return referral_code
           
    
class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by')
    timestamp = models.DateTimeField(auto_now_add=True)
    referral_code = models.CharField(max_length=100) 
