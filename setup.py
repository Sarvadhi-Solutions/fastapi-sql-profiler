from setuptools import setup

setup(
    name='database-query-profiling-middleware',
    version='1.0.0',
    description='Middleware for profiling and logging database queries in a Python web application',
    author='abc',
    author_email='abc@example.com',
    install_requires=[
        "fastapi >= 0.97.0",
        "SQLAlchemy >= 2.0.16",
    ],
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python',
          'Topic :: Software Development :: Bug Tracking',
    ]
)