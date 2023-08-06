from setuptools import setup, find_packages


setup(
    name="vk_wallet_api",
    version="1.0.1",
    author="DravaGen",
    author_email="dravagen@mail.ru",
    description="Library for working with the wallet api",
    long_description="https://github.com/DravaGen/wallet_api/",
    url="https://github.com/DravaGen/wallet_api/",
    packages=find_packages(),
    install_requires=["aiohttp==3.8.1", "pydantic==1.9.1"],
    python_requires=">=3.10"
)