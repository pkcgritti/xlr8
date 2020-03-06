from setuptools import find_namespace_packages, setup

import project

setup(name=project.get_package_name(),
      description=project.get_description(),
      version=project.get_version(),
      cmdclass=project.get_cmdclass(),
      packages=find_namespace_packages(where="src"),
      package_dir={'': 'src'},
      install_requires=project.get_requirements(),
      scripts=[])
