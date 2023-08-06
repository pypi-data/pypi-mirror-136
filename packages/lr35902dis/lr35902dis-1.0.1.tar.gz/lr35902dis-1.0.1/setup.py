import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lr35902dis",
    version="1.0.1",
    author="Lukas Dresel",
    author_email="foo@bar.com",
    description="lr35902 (GameBoy CPU) disassembler library",
    long_description=long_description, # load from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/Lukas-Dresel/lr35902dis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Disassemblers"
    ],
)
