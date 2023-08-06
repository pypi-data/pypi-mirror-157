import setuptools
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setuptools.setup(
    name="GenObjDet",
    version="0.1.5",
    author="Brayden Levangie",
    description="A package for isolating objects in images",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=["genobjdet"],
    install_requires=["opencv-python", "requests"],
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"]
)
