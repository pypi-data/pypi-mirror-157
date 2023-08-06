from setuptools import setup

setup(name='signal-aspect-detection',
      version='0.0.5',
      description='A railway signal aspect detection library',
      url='https://gitlab.hpi.de/osm/drohnenflieger/signal-aspect-detection',
      author='Dirk Friedenberger',
      author_email='Dirk.Friedenberger@guest.hpi.de',
      license='MIT',
      packages=['signal_aspect_detection'],
      install_requires=[
          'opencv-python',
          'scikit-image',
          'sklearn'
      ],
      zip_safe=False)