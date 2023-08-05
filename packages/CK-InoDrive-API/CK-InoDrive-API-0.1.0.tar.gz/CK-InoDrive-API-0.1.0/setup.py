from setuptools import setup

# reading long description from file
with open('description.md') as file:
    long_description = file.read()

# specify requirements of your package here
REQUIREMENTS = ['websocket-client']

# some more details
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows',
    'Topic :: Scientific/Engineering',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10',
]

# calling the setup function
setup(name='CK-InoDrive-API',
      version='0.1.0',
      description='Cardinal Kinetic Python API library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://cardinalkinetic.com',
      author='Cardinal Kinetic',
      author_email='support@cardinalkinetic.com',
      license='https://www.cardinalkinetic.com/terms-of-service',
      packages=['CkInoDriveAPI'],
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS,
      keywords='InoWorx InoDrive InoSync MotionControl ServoControl'
      )
