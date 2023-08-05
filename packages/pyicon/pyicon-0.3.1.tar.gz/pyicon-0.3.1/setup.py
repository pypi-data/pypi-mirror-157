from setuptools import setup


setup(
    name="pyicon",
    version="0.3.1",
    install_requires=[
        "click",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "icon = icon:cli",
        ],
    },
)
