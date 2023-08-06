from setuptools import setup, find_packages

setup(
    name ='KivyMDEmulator',
    version ='1.0.3',
    author ='Francisco carbonell',
    author_email ='francabezo@gmail.com',
    url ='https://gitlab.com/franciscocarbonell/kivymdemulator',
    description ='KivyMD Emulator.',
    long_description_content_type ="text/markdown",
    license='MIT',
    packages=find_packages(),
    entry_points ={
        'console_scripts': [
            'kivymdemulator = cli:kivymd_emulator_group'
        ]
    },
    keywords='python3 kivymd kivy kivymdemulator',
    zip_safe=False
)
