from setuptools import find_namespace_packages, setup
setup(
    name = 'actelink-computation',
    packages=find_namespace_packages(include=['actelink*']),
    license='LICENSE.txt',
    install_requires=['requests', 'flask', 'flask_restx', 'coloredlogs', 'python-dotenv', 'gunicorn']
)