"""
Simple test to verify authentication is configured correctly
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from chats.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class Command(BaseCommand):
    help = 'Test JWT authentication configuration'
    
    def handle(self, *args, **options):
        self.stdout.write("Testing JWT Authentication Configuration...")
        self.stdout.write("=" * 50)
        
        # Test JWT settings
        self.stdout.write("\n1. Checking JWT Settings...")
        if hasattr(settings, 'SIMPLE_JWT'):
            self.stdout.write(self.style.SUCCESS("✅ SIMPLE_JWT settings found"))
            self.stdout.write(f"   Access Token Lifetime: {settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')}")
            self.stdout.write(f"   Refresh Token Lifetime: {settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')}")
        else:
            self.stdout.write(self.style.ERROR("❌ SIMPLE_JWT settings not found"))
            return
        
        # Test DRF settings
        self.stdout.write("\n2. Checking DRF Authentication Settings...")
        auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        if 'rest_framework_simplejwt.authentication.JWTAuthentication' in auth_classes:
            self.stdout.write(self.style.SUCCESS("✅ JWT Authentication configured in DRF"))
        else:
            self.stdout.write(self.style.ERROR("❌ JWT Authentication not configured in DRF"))
        
        # Test creating a user and token
        self.stdout.write("\n3. Testing Token Creation...")
        try:
            # Create or get test user
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User',
                    'role': 'guest'
                }
            )
            
            if created:
                user.set_password('testpassword123')
                user.save()
                self.stdout.write(self.style.SUCCESS("✅ Test user created"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ Test user already exists"))
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            self.stdout.write(self.style.SUCCESS("✅ Tokens generated successfully"))
            self.stdout.write(f"   User ID: {user.user_id}")
            self.stdout.write(f"   Access Token: {access_token[:50]}...")
            
            # Test token payload
            payload = refresh.access_token.payload
            self.stdout.write(f"   Token User ID: {payload.get('user_id')}")
            self.stdout.write(f"   Token Type: {payload.get('token_type')}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Token creation failed: {e}"))
            return
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("✅ JWT Authentication configuration test completed successfully!"))
        self.stdout.write("\nYou can now:")
        self.stdout.write("1. Start the server: python manage.py runserver")
        self.stdout.write("2. Register: POST /api/auth/register/")
        self.stdout.write("3. Login: POST /api/auth/login/")
        self.stdout.write("4. Access protected endpoints with Bearer token")