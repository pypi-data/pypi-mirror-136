from setuptools import setup, find_packages

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(name='halmoney',
      version='1.0.0',
      url='https://www.halmoney.com',
      download_url='https://github.com/sjpark/halmoney/archive/v1.0.0.tar.gz',
      author='sjpark',
      author_email='sjpkorea@yahoo.com',
      description='small business module for Python',

      packages=find_packages("src"),
      package_dir={"" : "src"},
      include_package_data=True,
      package_data={
            "halmoney": ["pcell_addin/*.*"],
            "halmoney": ["pcell_code/*.*"],
            "halmoney": ["halmoney_history/*.*"],
            "halmoney": ["halmoney_manual/*.*"],
            "halmoney": ["pcell_menu/*.*"],
            "halmoney": ["halmoney_test_sample/*.*"],
            "halmoney": ["user_code/*.*"],
            "halmoney": ["user_menu/*.*"],
      },
      long_description=open('README.md').read(),
      install_requires=[],
      python_requires='>=3.5',
      zip_safe=False,
      classifiers=[
            "Programming Language :: Python :: 3",
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: Microsoft :: Windows',
      ],
)