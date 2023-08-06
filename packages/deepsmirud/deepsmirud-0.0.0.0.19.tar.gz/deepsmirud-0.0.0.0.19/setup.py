from setuptools import setup, find_packages

setup(
    name="deepsmirud",
    # version="0.0.1",
    version="0.0.0.0.19",
    keywords=("pip", "deepsmirud"),
    description="deepsmirud",
    long_description="deep learning SM-miR relation",
    license="MIT",

    url="https://github.com/2003100127",
    author="Jianfeng Sun",
    author_email="jianfeng.sunmt@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    python_requires='>3.6',
    install_requires=[
        'pandas==1.3.5',
        'numpy==1.19.5',
        'biopython==1.79',
        'pyfiglet==0.8.post1',
        'click==8.1.3',
        'tensorflow==2.6.0',
        'rdkit-pypi==2022.3.3',
        # 'tensorflow-gpu==2.6.0',
    ],
    entry_points={
        'console_scripts': [
            'deepsmirud=deepsmirud.Main:main',
            'deepsmirud_download=deepsmirud.Main:download',
        ],
    }
)