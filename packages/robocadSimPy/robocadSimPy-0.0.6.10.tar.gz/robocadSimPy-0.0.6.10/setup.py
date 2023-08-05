from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='robocadSimPy',
    version='0.0.6.10',
    description='python lib for robocadV',
    long_description="Python library for robocadV" + '\n\n' + open('CHANGELOG.md').read(),
    url='https://robocadv.readthedocs.io/en/latest/docs/all_docs/lib_docs/python/index.html',
    author='Abdrakov Airat',
    author_email='abdrakovairat@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['simulator', 'robotics', 'robot', '3d'],
    packages=find_packages(),
    install_requires=['numpy', 'funcad']
)
