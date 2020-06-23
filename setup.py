import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metaapi_cloud_sdk",
    version="1.1.5",
    author="Agilium Labs LLC",
    author_email="agiliumtrade@agiliumtrade.ai",
    description="SDK for MetaApi, a professional cloud MetaTrader API.",
    long_description="SDK for MetaApi, a professional cloud MetaTrader API which includes MetaTrader REST API "
                     "and MetaTrader websocket API. Supports both MetaTrader 5 (MT5) and MetaTrader 4 (MT4). "
                     "(https://metaapi.cloud)",
    long_description_content_type="text/markdown",
    url="https://github.com/agiliumtrade-ai/metaapi-python-client",
    package_dir={
        'metaapi_cloud_sdk': 'lib',
    },
    packages=['metaapi_cloud_sdk'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: SEE LICENSE IN LICENSE",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)