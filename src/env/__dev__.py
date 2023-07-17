"""
DEVELOPMENT ENVIRONMENT FLAG
"""
import sys

# Disable development flag if building executable release
development = True if not hasattr(sys, '_MEIPASS') else False
