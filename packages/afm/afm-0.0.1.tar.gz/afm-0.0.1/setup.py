import setuptools

setuptools.setup(
    name="afm",
    version="0.0.1",
    author="Xiaoyu Zhai",
    author_email="xiaoyu.zhai@hotmail.com",
    description="A placeholder for afm project",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)