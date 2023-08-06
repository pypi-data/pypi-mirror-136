import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="django-nextjs",
    version="0.0.1",
    description="Next.js + Django integration",
    long_description="",
    long_description_content_type="text/markdown",
    author="Mohammad Javad Naderi",
    packages=find_packages(".", include=("nextjs", "nextjs.*")),
    include_package_data=True,
    install_requires=["Django>=3.1", "requests", "aiohttp", "channels", "django_js_reverse"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
)
