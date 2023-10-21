# When running python, it will generate python cache directories
# Run this script with -B option to remove all existing cache directories


"""
WILL NOT REMOVE PYTEST CACHE


py -B clear_pycache.py
python3 -B clear_pycache.py
"""

# Abusing __import__ to avoid generating cache file for running if not ran with -B
for p in __import__('pathlib').Path('.').rglob('*.py[co]'): p.unlink()
for p in __import__('pathlib').Path('.').rglob('__pycache__'): p.rmdir()