from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="helpme-assistance",
    version="0.2.6",
    author="ITeams",
    author_email="vlad_bb@icloud.com, nataliia.kovalchuk90@gmail.com, saifulianna.it@gmail.com",
    description="The project 'HelpMe' - its your personal CLI assistant. AddressBook, NoteBook, CleanFolder - in one "
                "app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vlad-bb/HelpMe-project",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_namespace_packages(),
    include_package_data=True,
    install_requires=['phonenumbers==8.12.50'],
    entry_points={'console_scripts': [
        'helpme=app.main:main'
    ]}
)