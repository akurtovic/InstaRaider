from setuptools import setup

setup(
    name='instaraider',
    version='0.1.0',
    py_modules=['instaraider'],
    entry_points=dict(
        console_scripts=[
            'instaraider = instaraider:main',
        ],
    ),
    install_requires=['requests', 'selenium'],
)
