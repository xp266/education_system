
"""
后端模块
"""
from .core import EducationAssistant
from .config import SECRET_KEY, PORT, FRONTEND_URL, DEBUG

__all__ = [
    'EducationAssistant',
    'SECRET_KEY',
    'PORT',
    'FRONTEND_URL',
    'DEBUG'
]

