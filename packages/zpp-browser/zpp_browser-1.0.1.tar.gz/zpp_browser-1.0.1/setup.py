from setuptools import setup
import os
import zpp_browser

setup(name="zpp_browser",
      version=zpp_browser.__version__,
      author="ZephyrOff",
      author_email="contact@apajak.fr",
      keywords = "browser cli terminal zephyroff",
      classifiers = ["Development Status :: 5 - Production/Stable", "Environment :: Console", "License :: OSI Approved :: MIT License", "Programming Language :: Python :: 3"],
      packages=["zpp_browser"],
      description="Browser (Explorateur) de fichier en cli",
      long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
      long_description_content_type='text/markdown',
      url = "https://github.com/ZephyrOff/py-zpp_browser",
      platforms = "ALL",
      license="MIT")