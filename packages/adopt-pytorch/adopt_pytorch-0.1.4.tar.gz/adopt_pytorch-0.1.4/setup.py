from setuptools import setup, find_packages

__version__ = '0.1.4'
__author__ = 'Marc-Henri Bleu-Laine'

setup(
    name='adopt_pytorch',
    author=__author__,
    version=__version__,
    description='Pytorch version of ADOPT algorithm used for precursor mining, '
                'developed by NASA (https://github.com/nasa/ADOPT).'
                'Improvements were made to include time-series of different lengths',
    packages=find_packages(),
    url='https://github.com/mhbl3/adopt_pytorch',
    zip_safe=True,
    install_requires=[
        'pandas==1.3.4',
        'numpy==1.21.6',
        'matplotlib==3.5.1',
        'torch==1.12.0',
        'scikit-learn==1.0.2',
        'tqdm==4.64.0',
        # 'torchvision==0.8.2',
        # 'torchaudio==0.7.2'
                    ],
    )
