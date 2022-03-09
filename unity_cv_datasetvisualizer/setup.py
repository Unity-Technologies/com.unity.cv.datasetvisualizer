import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unity-cv-datasetvisualizer",
    version="0.1.2",
    author="Unity Technologies",
    description="This Python based tool allows you to visualize datasets created using Unity Computer Vision tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Unity-Technologies/com.unity.cv.datasetvisualizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    packages=["datasetvisualizer", "datasetvisualizer/helpers", "datasetvisualizer/visualization"],
    include_package_data=True,
    python_requires=">=3.7, !=3.9.*",
    install_requires=[
        "Pillow>=8.1.0",
        "streamlit==0.84.1",
        "pyquaternion>=0.9.9",
        "datasetinsights==1.1.1",
        "PySide2==5.15.2",
    ],
    entry_points={"console_scripts": ["datasetvisualizer=datasetvisualizer.cli:main"]},
)
