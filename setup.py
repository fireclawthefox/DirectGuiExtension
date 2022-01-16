import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DirectGuiExtension",
    version="22.01",
    author="Fireclaw",
    author_email="fireclawthefox@gmail.com",
    description="A set of extensions for the DirectGUI system of the Panda3D engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fireclawthefox/DirectGuiExtension",
    packages=setuptools.find_packages(),
    include_package_data=True,
    project_urls = {
        "Documentation": "https://github.com/fireclawthefox/DirectGuiExtension/wiki"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: User Interfaces",
    ],
    install_requires=[
        'panda3d',
    ],
    python_requires='>=3.6',
)
