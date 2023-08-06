import io
import os

from setuptools import setup, find_packages


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def read(fname):
    with io.open(fname) as fp:
        return fp.read()


long_description = read("README.md")


REQUIREMENTS_FILE = "requirements.txt"
REQUIREMENTS = open(os.path.join(PROJECT_DIR, REQUIREMENTS_FILE)).readlines()

REQUIREMENTS_DEV_FILE = "requirements-dev.txt"
REQUIREMENTS_TESTS = open(os.path.join(PROJECT_DIR, REQUIREMENTS_DEV_FILE)).readlines()


EXTRAS_REQUIRE = {
    "enum": ["marshmallow-enum"],
    "union": ["marshmallow-union"],
}


setup(
    name="marshmallow-jsonschema-3",
    version="1.0.9",
    description="Marshmallow schema to OpenAPI 3.0.x-3.1 spec. Fork of marshmallow-jsonschema by Stephen J. Fuhry.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="10Speed",
    author_email="info@10speed.cloud",
    # url="https://github.com/pauliusbaulius/marshmallow-jsonschema-3",
    packages=find_packages(exclude=("test*",)),
    package_dir={"marshmallow-jsonschema-3": "marshmallow-jsonschema-3"},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_TESTS,
    extras_require=EXTRAS_REQUIRE,
    license="MIT License",
    zip_safe=False,
    keywords=(
        "marshmallow-jsonschema marshmallow schema serialization "
        "jsonschema validation openapi openapi3.1 openapi3.0"
    ),
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    test_suite="tests",
)
