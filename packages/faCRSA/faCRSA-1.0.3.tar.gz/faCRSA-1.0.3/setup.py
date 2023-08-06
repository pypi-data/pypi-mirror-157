from distutils.core import setup


setup(name='faCRSA',  # 包名
      version='1.0.3',  # 版本号
      description='faCRSA',
      long_description="A fully automated pipeline for the high-throughput analysis of crop root system architecture",
      author='Ruinan Zhang',
      author_email='2020801253@stu.njau.edu.cn',
      url='https://github.com/njauzrn/facrsa',
      install_requires=['click==7.1.2','Flask==1.1.4', 'huey==2.4.3', 'numpy==1.19.2', 'opencv_python==4.6.0.66',
                        'pandas==0.24.0', 'Pillow==8.4.0', 'scikit_image==0.17.2', 'tensorflow==2.4.0', 'yagmail==0.15.277', 'python-dotenv==0.20.0', 'pyparsing==2.4.7'],
      license='GPL v3.0 License',
      packages=['faCRSA', 'faCRSA.facrsa_code', 'faCRSA.facrsa_code.library', 'faCRSA.facrsa_code.static', 'faCRSA.facrsa_code.templates', 'faCRSA.facrsa_code.library.analysis', 'faCRSA.facrsa_code.library.util',
                'faCRSA.facrsa_code.library.web', 'faCRSA.facrsa_code.library.analysis.database', 'faCRSA.facrsa_code.library.analysis.net'],
      entry_points={
          'console_scripts': ['facrsa-web=faCRSA.start_web:start_web', 'facrsa-queue=faCRSA.start_queue:start_queue'],
      },
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries'
      ],
      include_package_data=True
      )
