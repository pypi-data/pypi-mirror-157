import setuptools

setuptools.setup(
  name="tkinterDev",
  version="1.5.0",
  author="XiangQinxi",
  author_email="XiangQinxi@outlook.com",
  description="tkinter Tool",
  long_description=open("README.md", "r", encoding="utf-8").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/pypa/sampleproject",
  packages=setuptools.find_packages("ctypes", "tkinter-tooltip"),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)