from setuptools import setup, find_packages

setup(
    name="family-stories-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pymongo>=4.0.0',
        'pyyaml>=6.0.0',
        'pandas>=1.5.0',
        'schedule>=1.1.0',
        'python-dotenv>=0.19.0',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A family story collection application that sends weekly questions and stores responses",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/app",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'family-stories=app.main:main',
        ],
    },
)
