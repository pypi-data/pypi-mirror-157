from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


VERSION = '0.1.3'
DESCRIPTION = 'A simple screenshot application.'
LONG_DESCRIPTION = 'A simple screenshot application which captures the screen on a key press.'

# Setting up
setup(
    name="pyscreenshotter",
    version=VERSION,
    author="Garrett Jones",
    author_email="jonesgc137@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.0',
    install_requires=['keyboard>=0.13.5',  'numpy>=1.21.5', 'opencv_python>=4.6.0.66','PyAutoGUI>=0.9.53'],
    keywords=['opencv', 'keyboard', 'screenshot', 'pyautogui'],
    entry_points={
        'console_scripts': [
            'pyscreen=pyscreenshotter.main:main'
            ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
