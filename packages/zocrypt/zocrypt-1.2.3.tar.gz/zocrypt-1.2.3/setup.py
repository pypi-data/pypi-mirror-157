from setuptools import setup, find_packages


setup(
    name='zocrypt',
    version='1.2.3',
    license='MIT',
    author="Siddhant Mohile",
    author_email='meetsiddhant@gmail.com',
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    url='https://github.com/SidmoGoesBrrr/zocrypt',
    keywords=['encrypt','decrypt','encoding','secret messages'],
    install_requires=[],
    long_description="""
Zocrypt
=======

Intended mainly for use by **ZeroAndOne Developers** for protection of
data with 6 level encryption.

Based on our project [secret message encoder
decoder](https://Secret-Message-Encoder-Decoder.itszeroandone.repl.co)

Installing
==========

``` {.bash}
pip install zocrypt
```

Usage
=====

``` {.bash}
>>> from zocrypt import encrypter,decrypter,key
>>> from encrypter import encrypt_text
>>> from decrypter import decrypt_text
>>> text="5 Mangoes are better than 6 Mangoes"
>>> key=key.generate()
>>> encrypt_text(text,key)
'`"V`O/i|;^a^.~k|4~k|;a|R#`k|l`V~#^#^V~Hk~V|l/a|k^"~V/O/i^;|a^.`k3'
>>> decrypt_text(text,key)
'5 Mangoes are better than 6 Mangoes'
```

""",
    long_description_content_type='text/markdown',

)
