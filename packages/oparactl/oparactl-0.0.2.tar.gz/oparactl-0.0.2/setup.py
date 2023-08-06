from setuptools import setup, find_packages

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'oparactl',
    version = '0.0.2',
    author = 'Nnabueze Opara',
    author_email = 'villavelle101@gmail.com',
    license = 'MIT',
    description = 'Message consumer from AWS SQS',
    long_description = "Message consumer from AWS SQS",
    long_description_content_type = "text/markdown",
    url = 'https://gitlab.com/bayzat/bayzat-sre-interview-NnabuezeOpara',
    py_modules = ['stack_queue', 'database'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        oparactl=src:main
    '''
)