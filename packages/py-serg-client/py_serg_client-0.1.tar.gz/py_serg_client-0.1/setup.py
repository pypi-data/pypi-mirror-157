from setuptools import setup, find_packages

setup(name="py_serg_client",
      version="0.1",
      description="Serg Client",
      author="Sergei Sergeev",
      author_email="isergantnik@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
