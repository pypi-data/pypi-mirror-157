import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mt5se",
    version="0.2.36",
    author="Paulo Andre Lima de Castro",
    license='MIT', 
    author_email="paulo.al.castro@gmail.com",
    description="mt5se provides access to Stock Exchanges to python programs through Metatrader and some brokers. It can be used with NYSE,Nasdaq, B3(Brazilian Stock Exchange)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulo-al-castro/mt5se/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)