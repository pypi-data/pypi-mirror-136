import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="editable_list_view",
    version="1.0.0",
    author="Takaaki Fujiki",
    author_email="",
    description="Editable list view for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/t-fujiki/editable_list_view",
    project_urls={
        "Bug Tracker": "https://github.com/t-fujiki/editable_list_view/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)