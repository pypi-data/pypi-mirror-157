from setuptools import setup, find_packages


setup(
    name='reportclassicproject',
    version='0.2',
    license='MIT',
    author="Câmara Municipal de São Bernardo do Campo, SP, Brazil",
    author_email='informatica@camarasbc.sp.gov.br',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/cmsbc/report-classic-project',
    keywords='ReportClassic Project',
    install_requires=[
          'reportlab',
          'django',
          'datetime',
          'requests'
      ],
    description="This is a ReportClassic Project made to print labels and reports in PDF FOR DJANGO FRAMEWORK.",
)
