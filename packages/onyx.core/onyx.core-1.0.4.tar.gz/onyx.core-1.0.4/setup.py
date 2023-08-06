###############################################################################
#
#   Copyright: (c) 2015-2020 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

from setuptools import setup, find_packages

install_requires = [
    "dateutils",
    "numpy",
    "psycopg2",
    "argh",
]

DESCRIPTION = """
Onyx is a framework to develop integrated trading, position management, pricing
and risk management platforms.
onyx.core implements the fundamental datatypes, various serialization tools,
and a powerful dependency graph."""

setup(
    name="onyx.core",
    namespace_packages=["onyx"],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    description="Core functions and datatypes for the onyx framework.",
    long_description=DESCRIPTION,
    author="carlo sbraccia",
    author_email="carlo.sbraccia@gmail.com",
    url="https://github.com/sbraccia/onyx.core",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "run-forever = onyx.core.utils.run_forever:main",
        ],
    },
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
