from setuptools import setup, find_packages
import iwin_cli

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup (
    name="iwin-cli",
    version=iwin_cli.__version__,
    author="Learner Chen",
    author_email="learner.chen@icloud.com",
    description="iwin commandline tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="NO-DISTRIBUTION",
    url="https://iwin2.3thinking.cn",
    # packages=find_packages(),
    packages=['iwin_cli'],
    package_dir={'iwin_cli': 'iwin_cli'},
    entry_points={'console_scripts': ['iwin-cli = iwin_cli.__main__:main']},
    include_package_data=True,
    install_requires=[
        "et-xmlfile",
        "numpy",
        "openpyxl",
        "pandas",
        "XlsxWriter",
        "Pillow",
        "colorama"
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7"
    ]
)