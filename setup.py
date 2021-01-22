# Copyright 2018 The Piccolo Team
#
# This file is part of piccolo2-web.
#
# piccolo2-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-web.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name="piccolo3-web",
    namespace_packages=['piccolo3'],
    packages=find_packages(),
    use_scm_version=True,
    setup_requires=[
        "pyqt-distutils",
        'setuptools_scm'],
    install_requires=[
        "numpy",
        "quart",
        "pytz",
        "configobj",
        "uvicorn"],
    entry_points={
        'gui_scripts': [
            'piccolo3-web = piccolo3.app:main']},
    include_package_data=True,

    # metadata for upload to PyPI
    author="Livia Jakob, Magnus Hagdorn, Alasdair MacArthur, Iain Robinson",
    description="""Part of the piccolo3 system.

This package provides a web GUI client""",
    license="GPL",
    url="https://github.com/TeamPiccolo/piccolo3-web",
)
