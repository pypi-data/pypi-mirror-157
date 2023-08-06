import setuptools

#with open("README.md", "r", encoding="utf-8") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="mgr_3006_o_cnq_dev",
    version="0.0.1",
    author="MGR",
    author_email="mohamed.grini@aosis.net",
    description="CNQ Test Dev machine",
    long_description="Description",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    #package_data={'src': ['config/*',]},
    package_data = {"": ["*.ini"],},
    # If any package contains *.ini files, include them
   
    
)