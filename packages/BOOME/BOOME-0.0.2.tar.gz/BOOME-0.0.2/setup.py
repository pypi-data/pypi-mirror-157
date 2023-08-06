import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BOOME",
    version="0.0.2",
    author="Qin-Ying Ou Yang and Li-Pang Chen",
    author_email="109354014@nccu.edu.tw, lchen723@nccu.edu.tw",
    description="This package aims to employ the boosting algorithm to do variable selection and estimation for measurement error in binary responses and high-dimensional covariates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    
)

