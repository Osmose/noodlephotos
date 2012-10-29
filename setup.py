from distutils.core import setup

setup(
    name='noodlephotos',
    description='Flask app for hosting a small file-based photo gallery.',
    version='0.1',
    packages=['noodlephotos'],
    author='Michael Kelly',
    author_email='me@mkelly.me',
    url='https://github.com/nooodle/noodlephotos',
    license=open("LICENSE").read(),
    install_requires=['Flask', 'Flask-Script'],
    package_data={'noodlephotos': ['static/*']},
)
