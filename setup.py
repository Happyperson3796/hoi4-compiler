from setuptools import setup, find_packages

setup(
    name='hoi4',
    version='0.1',
    packages=find_packages(),
    install_requires=[],  # List any dependencies your module has here
    include_package_data=True,
    description='A short description of your module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Happyperson3796',
    author_email='tedisataco@gmail.com',
    url='https://yourprojecturl.com',  # Optional
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',  # Adjust for your supported versions
        'License :: OSI Approved :: MIT License',  # Choose the right license
        'Operating System :: OS Independent',
    ],
)
