import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LatestEarthQuakeIndonesiaByFaqih",
    version="0.1",
    author="Faqih Fakhruddin",
    author_email="faqih0776@gmail.com",
    description="This package will get latest earthquake from BMKG | Meteorological, Climatological, "
                "and Geophysical Agency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fakhr07/Latest-EarthQuake-BMKG",
    project_urls={
        "Bug Tracker": "https://github.com/Faqih0776",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
    #package_dir={"": "src"},
    #packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
