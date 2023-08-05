import setuptools

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setuptools.setup(
    name="dkdisc",
    version="0.1.0-rc9",
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
    entry_points={
        'console_scripts': [
            'dkdisc=dkdisc.dkdisc:main',
        ],
    },
)
