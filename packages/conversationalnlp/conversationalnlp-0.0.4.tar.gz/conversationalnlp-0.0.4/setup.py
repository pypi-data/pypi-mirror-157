from setuptools import find_packages
from setuptools import setup

with open("readme.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='conversationalnlp',
    version='0.0.4',
    install_requires=['torch==1.10.0', 'torchaudio==0.10.0', 'transformers==4.20.',
                      'autocorrect==2.6.1', 'SoundFile==0.10.3.post1', 'librosa == 0.8.1'],
    include_package_data=True,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8.5",
    url='https://github.com/codenamewei/conversationalnlp',
    license='MIT',
    author='codenamewei',
    author_email='codenamewei@gmail.com',
    description='Your main project',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
