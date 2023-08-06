from setuptools import setup, find_packages

setup(
    name='readonly_github_sdk',
    version='0.1',
    license='MIT',
    author="Mengyu Jackson",
    author_email='mengyujackson121@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/mengyujackson121/GithubSDK',
    install_requires=[
          'requests',
          'attrs',
      ],
)