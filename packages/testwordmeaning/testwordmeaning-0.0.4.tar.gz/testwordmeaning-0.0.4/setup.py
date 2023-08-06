from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Manufacturing',
    'Operating System :: Microsoft :: Windows :: Windows 8',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name="testwordmeaning",
    version="0.0.4",
    description="Recognize whether words are meaningful or not",
    long_description=open("README.txt").read() + '\n\n' + open("CHANLOGLOG.txt").read(),
    rul="https://sites.google.com/view/testwordmeaning/%D8%B5%D9%81%D8%AD%D9%87-%D8%A7%D8%B5%D9%84%DB%8C",
    author="moein davarzani",
    author_email="moeindavarzani2006@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="testwordmeaning",
    packages=find_packages(),
    install_requires=["bs4", "requests"]
)
