from setuptools import setup
import os

with open(os.path.dirname(__file__) + "/README.md", "r") as f:
    readme = f.read()

setup(name="HowMonoPy",
      version="0.1",
      description="A Python wrapper for the c library from how-monochromatic.",
      long_description=readme,
      long_description_content_type='text/markdown',
      url="https://github.com/SebTee/HowMonoPy",
      author="Sebastian Tee",
      maintainer="Sebastian Tee",
      license="MIT",
      package_dir={"": "src"},
      packages=["HowMonoPy"],
      package_data={"HowMonoPy": ["clib/*"]},
      platforms=["Windows", "Linux"],
      classifiers=[
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3",
          "Programming Language :: Haskell",
          "Topic :: Scientific/Engineering :: Mathematics",
          "License :: OSI Approved :: MIT License",
          "Development Status :: 3 - Alpha"
      ],
      zip_safe=True)
