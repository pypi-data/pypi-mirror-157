import setuptools


setuptools.setup(
    name="streamlit-graphic-slider",
    version="0.1.0",
    author="Mirko Mälicke",
    author_email="mirko@hydrocode.de",
    description="Graphic background slider for Streamlit",
    long_description="",
    long_description_content_type="text/plain",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
)
