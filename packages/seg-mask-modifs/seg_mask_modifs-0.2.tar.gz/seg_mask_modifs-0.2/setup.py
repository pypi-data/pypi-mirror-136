import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seg_mask_modifs",
    version="0.2",
    author="Vardan Agarwal",
    author_email="vardanagarwal16@gmail.com",
    description="A package for easy generation of mask of different labels using multiple models \
                 and applying different operations on that.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vardanagarwal/seg_mask_modifs",
    project_urls={
        "Bug Tracker": "https://github.com/vardanagarwal/seg_mask_modifs/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "seg_mask_modifs"},
    packages=setuptools.find_packages(where="seg_mask_modifs"),
    python_requires=">=3.6",
)
