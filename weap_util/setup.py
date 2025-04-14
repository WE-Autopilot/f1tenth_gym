from setuptools import setup, find_packages

setup(
    name='weap_util',
    version='0.1.0',
    author='Aly Ashour',
    packages=find_packages(),  # This will automatically find the "weap_util" package inside
    install_requires=[
        'numpy>=1.18.0,<=1.22.0',
        'opencv-python-headless==4.11.0.86'
    ]
)