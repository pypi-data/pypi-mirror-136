from importlib_metadata import entry_points
import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='nnotes',
    version = '0.0.3',
    author = 'wbwqq',
    description= 'A cli notetaking tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/wbwqq/nnotes',
    project_urls = {
        "Bug Tracker" : 'https://github.com/wbwqq/nnotes/issues',
    },
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    packages=['nnotes'],
    package_data={'nnotes':['defaults/settings.ini', 'defaults/notebooks.txt']},
    python_requires=">=3.6",
    entry_points = {
        'console_scripts': [
            'n = nnotes:main',
            'nnotes = nnotes:main'
        ]
    },
    install_requires = [
        'miniparser==0.0.8'
    ]
)