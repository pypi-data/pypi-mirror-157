from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'Command line program to merge pim videos.'

setup(
    name='pim_video',
    version='1.0.0',
    author='Zaw Lin Tun',
    author_email='zawlintun1511@gmail.com',
    url='https://github.com/jtur044/pim_video',
    description='pim videos merging program',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache Software",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pim_video = pim_video.pim_video:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='pim videos merging program pim_video',
    install_requires=requirements,
    zip_safe=False
)
