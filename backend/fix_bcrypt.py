"""
Fix bcrypt compatibility with passlib
Passlib 1.7.4 expects bcrypt.__about__.__version__ but bcrypt 4.x doesn't have it
This module must be imported before passlib
"""
import warnings

# Suppress warnings first
warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

try:
    import bcrypt
    if not hasattr(bcrypt, '__about__'):
        # Create a mock __about__ module with version
        class MockAbout:
            __version__ = getattr(bcrypt, '__version__', '4.1.3')
        bcrypt.__about__ = MockAbout()
except ImportError:
    pass
