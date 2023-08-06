import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
name="monitorBuilding",
version="6.0.4",
author="Dorian Drevon",
author_email="drevondorian@gmail.com",
description="Utilities package",
long_description=long_description,
long_description_content_type="text/markdown",
classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
],
packages=['monitorBuilding'],
package_data={'': ['confFiles/*','confFiles/PLC_config/*']},
# include_package_data=True,
install_requires=['dorianUtils==6.0.4'],
python_requires=">=3.8"
)
