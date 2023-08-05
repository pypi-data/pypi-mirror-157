import setuptools
import subprocess

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()


def get_git_version() -> str:
    return (
        subprocess.check_output(["git", "describe", "--tags"])
        .decode("ascii")
        .strip()
    )


setuptools.setup(
    name="dkdisc",
    version=get_git_version(),
    author="Fischer Group",
    description="Collection of solvers for Dean-Kawasaki",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qwinters/dean-kawasaki-discretizations",
    packages=[
        "dkdisc",
        "dkdisc.utils",
        "dkdisc.finitediff",
    ],
    python_requires=">=3.6",
)
