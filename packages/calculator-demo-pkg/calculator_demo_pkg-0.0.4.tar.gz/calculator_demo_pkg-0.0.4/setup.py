import setuptools

setuptools.setup(
    name="calculator_demo_pkg",
    version="0.0.4",
    author="Akhil",
    author_email="akhil@example.com",
    description="A calculator package",
    license='MIT',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.4",
)
