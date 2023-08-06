import setuptools
import glob

with open("README.md", "r") as fh:
    long_description = fh.read()


# data_files = []
# directories = glob.glob('tl2/*')
# for directory in directories:
#     files = glob.glob(directory+'*')
#     data_files.append((directory, files))

setuptools.setup(
    name="tl2",
    version="0.0.9",
    author="Peterou",
    author_email="pengzhoucv@gmail.com",
    description="A personal package for research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PeterouZh/tl2",
    packages=setuptools.find_packages(),
    # package_dir={'': 'tl2'},
    include_package_data = True,
    install_requires=[
        # 'Django >= 1.11, != 1.11.1, <= 2',
        'easydict',
        'termcolor',
        'deepdiff',
        'fvcore',
        'numpy',
        'matplotlib',
        'pyyaml',
        'omegaconf',
        'einops',
        'imageio-ffmpeg',
        'opencv-python',
        'scikit-image',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)




