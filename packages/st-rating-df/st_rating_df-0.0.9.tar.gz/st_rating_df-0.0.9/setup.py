import setuptools

setuptools.setup(
    name="st_rating_df",
    version="0.0.9",
    author="Anton Buch",
    author_email="anton.buch@bayer.com",
    description="",
    long_description="",
    long_description_content_type="text/plain",
    license='MIT License',
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
        "pandas >= 1.3",
        "numpy >= 1.20",
    ],
)
