from setuptools import setup, find_packages


setup(
    name='clipboard-sync',
    version='0.0.4',
    keywords=['clipboard', 'sync'],
    description='A simple clipboard sync tool',
    url='http://github.com/yetone/clipboard-sync',
    license='MIT License',
    author='yetone',
    author_email='yetoneful@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'clipboard-sync=clipboard_sync:main',
        ],
    },
    zip_safe=False,
    install_requires=[],
)
