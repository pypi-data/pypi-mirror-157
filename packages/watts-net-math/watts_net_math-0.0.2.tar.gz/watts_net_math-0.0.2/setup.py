#!/data/data/com.termux/files/usr/bin/python3
import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="watts_net_math",
    version="0.0.2",
    author="Tyler Watts",
    author_email="slickwattsbiz@gmail.com",
    packages=["watts_net_math"],
    description="A package with methods to help with IP address subnetting.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/slickwatts/net_math.git",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)
