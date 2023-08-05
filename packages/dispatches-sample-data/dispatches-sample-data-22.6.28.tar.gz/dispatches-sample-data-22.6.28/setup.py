from setuptools import setup


setup(
    name="dispatches-sample-data",
    description="Sample datasets for the DISPATCHES project",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    include_package_data=True,
    install_requires=[
        "importlib-metadata; python_version < '3.8'",
    ]
)
