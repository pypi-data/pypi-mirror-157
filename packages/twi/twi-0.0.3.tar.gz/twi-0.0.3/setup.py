from pathlib import Path
from distutils.core import setup

setup(
    name="twi",
    author="Zev Averbach",
    author_email="zev@averba.ch",
    version="0.0.3",
    description="do Twitter things via CLI",
    long_description=Path("README.md").read_text(),
    long_description_content_type='text/markdown',
    license="MIT",
    url="http://code.averba.ch/Zev/twi",
    install_requires=[
        "tweepy",
    ],
    packages=[
        "twi",
    ],
    entry_points="""
        [console_scripts]
        tw=twi.send_tweet:main
        prof=twi.update_profile:main
        dtw=twi.delete_last_tweet:main
    """,
)
