from setuptools import setup, find_namespace_packages

setup(
    name='helpme_assistance',
    version='0.2.3',
    description='The project "HelpMe" - its your personal CLI assistant.' \
                ' AddressBook, NoteBook, CleanFolder - in one app.',
    author='Vladyslav Babenko',
    author_email='vlad_bb@icloud.com',
    url='https://github.com/vlad-bb',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    packages=find_namespace_packages(),
    data_files=[('helpme_pack', ['helpme_pack/AddressBook.bin', 'helpme_pack/NoteBook.bin'])],
    include_package_data=True,
    entry_points={'console_scripts': [
        'helpme=helpme_pack.main:main']}
)
