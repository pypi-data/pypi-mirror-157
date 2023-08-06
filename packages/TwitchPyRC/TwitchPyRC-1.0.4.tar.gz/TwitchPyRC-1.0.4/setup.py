from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

packages = find_packages(where=".")

if "tests" in packages:
    packages.remove("tests")

setup(
    name='TwitchPyRC',
    version='1.0.4',
    packages=packages,
    url='https://github.com/CPSuperstore/TwitchPyRC',
    license='MIT',
    author='CPSuperstore',
    author_email='cpsuperstoreinc@gmail.com',
    description='Yet another generic Twitch IRC interface that probably works',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/CPSuperstore/TwitchPyRC/issues",
    },
    keywords=['Twitch', 'IRC', 'Bot', "Chat Bot", "Socket", "livestream"],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ]
)
