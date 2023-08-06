
import setuptools


setuptools.setup(
    name="jittor_offline",
    version="0.0.3",
    author="jittor",
    author_email="jittor@qq.com",
    description="jittor project",
    long_description="jittor_offline",
    long_description_content_type="text/markdown",
    url="https://github.com/jittor/jittor",
    project_urls={
        "Bug Tracker": "https://github.com/jittor/jittor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=[],
    package_dir={"": "python"},
    package_data={'': ['*', '*/*', '*/*/*','*/*/*/*','*/*/*/*/*','*/*/*/*/*/*']},
    python_requires=">=3.7",
    install_requires=[
        "jittor>=1.3.4.10",
    ],
)
