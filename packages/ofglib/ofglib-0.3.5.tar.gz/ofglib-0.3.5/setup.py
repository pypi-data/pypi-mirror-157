from setuptools import setup, find_packages
import ofglib

setup(
    name='ofglib',
    python_requires='>3.6',
    author='dies0mbre',
    version=ofglib.__version__,
    packages=find_packages(),
    install_requires=['numpy>=1.19.5,<1.20.0',
                      'matplotlib>=3.4.2',
                      'seaborn>=0.11.1',
                      'pandas>=1.3.0',
                      'scipy>=1.7.0',
                      'scikit-learn>=1.0',
                      'pyod>=0.9.5',
                      'pyodbc>=4.0.32',
                      'autofeat>=2.0.10',
                      'cx_Oracle>=8.3.0',
                      'tensorflow-io>=0.26.0',
                      'xgboost>=1.4.2',
                      'pygam>=0.8.0',
                    ]

)