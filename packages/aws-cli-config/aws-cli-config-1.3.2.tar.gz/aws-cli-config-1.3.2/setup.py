import os
import pathlib
from pathlib import Path
from shutil import copyfile

from setuptools import setup, find_packages
from setuptools.command.install import install

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
VERSION = (HERE / "VERSION").read_text()


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        yml_config_file__destination = os.path.join(str(Path.home()), '.aws-cli-config.yml')
        print("*** Installing files in user directory %s" % yml_config_file__destination)
        if not os.path.exists(yml_config_file__destination):
            print("*** YML config file did not found. Install a new one")
            copyfile(HERE / "aws-cli-config/template.yml", yml_config_file__destination)

        install.run(self)


setup(
    name='aws-cli-config',
    version=VERSION,
    packages=find_packages(),
    url='https://bitbucket.org/lorenzogatti89/aws-cli-config',
    license='GPL3',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Lorenzo Gatti',
    author_email='lg@lorenzogatti.me',
    description='Multi-account/Multi-Role AWS cli configuration (with MFA support)',
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
    include_package_data=True,
    install_requires=["argparse", "configparser", "boto3", "PyYaml"],
    scripts=['aws-cli-config/aws-cli-config']
)
