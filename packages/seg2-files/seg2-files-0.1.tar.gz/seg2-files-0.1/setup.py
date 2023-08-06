from distutils.core import setup
setup(
  name = 'seg2-files',         # How you named your package folder (MyLib)
  packages = ['seg2-files'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Simple tools for reading seg2-format seismic/radar files',   # Give a short description about your library
  author = 'Nathan Stoikopoulos',                  # Type in your name
  author_email = 'nathan.stoikopoulos@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/natstoik/seg2-files',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/natstoik/seg2-files/archive/refs/tags/v_01.tar.gz',    # I explain this later on
  keywords = ['SEISMIC', 'GEOPHYSICS', 'RADAR', 'GPR'],   # Keywords that define your package best
  install_requires=[      # I get to this in a second
          'struct',
          'numpy',
          'distutils',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Science/Research',      # Define that your audience are developers
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)