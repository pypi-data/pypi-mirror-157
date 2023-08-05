import setuptools
 
with open("README.md", "r") as fh:
    long_description = fh.read()
  
setuptools.setup(

    name="scroll_of_seals",
    packages = ['scroll_of_seals'],
    version="0.0.01",
    author="Túlio F. Almeida",
    author_email="tuliofalmeida@hotmail.com",
    description="A useful library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuliofalmeida/scroll-of-seals",
    install_requires= ['numpy',
                      'pandas',
                      'matplotlib'],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)