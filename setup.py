from setuptools import setup

setup(
    name='fastapi-sql-profiler',
    version='1.0.1',
    description='Middleware for profiling and logging database queries in a Python web application',
    package_data={'fastapi_sql_profiler': ['templates/*']},
    author='Ganesh Sali',
    author_email='ganesh@sarvadhi.com',
    url="https://github.com/Sarvadhi-Solutions/fastapi-sql-profiler.git",
    install_requires=[
        "fastapi >= 0.97.0",
        "SQLAlchemy >= 2.0.16",
        "python-dotenv >= 1.0.0",
        "Jinja2 >= 3.1.2",
        "python-multipart >= 0.0.6"
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