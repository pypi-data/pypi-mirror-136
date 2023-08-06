from distutils.core import setup
    
version = '0.1.0'

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='nextcord-ext-space',
    author='japandotorg',
    python_requires='>=3.8.0',
    url='https://github.com/japandotorg/nextcord-ext-space',
    version=version,
    packages=[
        'nextcord/ext/space',
        'nextcord/ext/space/recorders',
    ],
    license='MIT',
    description='A event logger for nextcord discord API library.',
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'nextcord==2.0.0a6',
        'databases',
    ],
    keywords=[
        'nextcord',
        'extension',
        'discord'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)