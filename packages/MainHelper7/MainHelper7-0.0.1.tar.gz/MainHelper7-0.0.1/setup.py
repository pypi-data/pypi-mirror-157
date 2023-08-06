from setuptools import setup, find_namespace_packages

setup(
    name='MainHelper7',
    version='0.0.1',
    description='MainHelper7 its project to help you create and manage AddressBook, \
    clean your folder.',
    author='Nissa',
    author_email='dgofreyod@gmail.com',
    url='https://github.com/NissaOd',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    packages=find_namespace_packages(),
    data_files=[('main_helper7', ['main_helper7/AB.bin'])],
    include_package_data=True,
    entry_points={'console_scripts': [
        'needhelp=main_helper7.main:main']}
)
