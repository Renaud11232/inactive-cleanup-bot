import setuptools


def get_long_description():
    with open("README.md", "r") as readme:
        return readme.read()


setuptools.setup(
    name="inactive-cleanup-bot",
    version="0.0.1",
    author="Renaud Gaspard",
    author_email="gaspardrenaud@hotmail.com",
    description="A simple bot that removes inactive users from a server",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Renaud11232/inactive-cleanup-bot",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "inactive-cleanup-bot=inactivecleanupbot.command_line:main"
        ]
    },
    install_requires=[
        "nextcord"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)