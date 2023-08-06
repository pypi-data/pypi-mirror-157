# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
import setuptools

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
def readme_handler() -> str:
    with open("README.md", "r") as readme_file:
        return readme_file.read()

def version_handler() -> str:
    # ------------------------------------------------------------------------------------------------------------------
    version = 0,2,0 # <-- DEFINE THE VERSION IN A TUPLE FORMAT HERE
    # ------------------------------------------------------------------------------------------------------------------
    version_str = ".".join(str(i) for i in version)

    with open("src/AthenaDocumentor/_info/_v.py", "w") as file:
        file.write(f"def _version():\n    return '{version_str}'")

    return version_str

# ----------------------------------------------------------------------------------------------------------------------
# - Actual Setup -
# ----------------------------------------------------------------------------------------------------------------------
setuptools.setup(
    name="AthenaDocumentor",
    version=version_handler(),
    author="Andreas Sas",
    author_email="",
    url="https://github.com/DirectiveAthena/AthenaDocumentor",
    project_urls={
        "Bug Tracker": "https://github.com/DirectiveAthena/AthenaDocumentor/issues",
    },
    license="GPLv3",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.10"
)
