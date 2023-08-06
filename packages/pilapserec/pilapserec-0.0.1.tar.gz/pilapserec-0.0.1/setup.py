import pilapse
from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pilapserec',
    version=pilapse.__version__,
    description=pilapse.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=pilapse.__url__,
    author=pilapse.__author__,
    author_email=pilapse.__author_email__,
    license=pilapse.__license__,
    packages=['pilapse'],
    entry_points={
        'console_scripts': [
            'pilapse = pilapse.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'Topic :: Multimedia :: Video :: Capture'
    ],
    keywords='timelapse video pilapse picamera raspberrypi',
    install_requires=[
        'tqdm',
        'docopt',
        'moviepy',
        'picamera'
    ],
)
