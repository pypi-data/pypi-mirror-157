import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="inseparable_tool",
  version="0.0.1",
  author="Sesen",
  author_email="shiw_21@163.com",
  description="Your Inseparable Tool",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/SeeeeShiwei/InseparableTool.git",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)

