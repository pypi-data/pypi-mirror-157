from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='TwitchPyRC',
    version='1.0.0',
    packages=['TwitchPyRC'],
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
