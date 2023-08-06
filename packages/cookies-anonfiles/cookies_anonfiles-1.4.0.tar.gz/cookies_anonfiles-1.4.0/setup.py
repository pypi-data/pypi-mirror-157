import setuptools
from anonfiles.main import __version__

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setuptools.setup(
    name="cookies_anonfiles",
    version="1.4.0",
    author="CookiesKush42",
    author_email="jakbin4747@gmail.com",
    description="upload and download to anonfiless server",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/redevil1/anonfiles",
    install_requires=["tqdm","requests","requests-toolbelt"],
    python_requires=">=3",
    project_urls={
        "Bug Tracker": "https://github.com/redevil1/anonfiless/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    keywords='anonfiles,anonfiles-api,anonfiles-cli,anonymous,upload',
    packages=["cookies_anonfiles"],
    entry_points={
        "console_scripts":[
            "anon = anonfiles.main:main"
        ]
    }
)
