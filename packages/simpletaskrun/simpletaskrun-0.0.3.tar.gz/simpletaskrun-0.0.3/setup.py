import setuptools  # 导入setuptools打包工具

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name="simpletaskrun",
  version="0.0.3",
  author="",
  author_email="",
  description="Parallel function excutor interface",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="",
  packages=setuptools.find_packages(),
  install_requires= ['termcolor'],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3',
)