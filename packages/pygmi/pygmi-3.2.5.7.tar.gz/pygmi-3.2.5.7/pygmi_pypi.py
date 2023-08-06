# -----------------------------------------------------------------------------
# Name:        pygmi_pypi.py (part of PyGMI)
#
# Author:      Patrick Cole
# E-Mail:      pcole@geoscience.org.za
#
# Copyright:   (c) 2013 Council for Geoscience
# Licence:     GPL-3.0
#
# This file is part of PyGMI
#
# PyGMI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyGMI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------
"""
Convenience routine to upload pygmi to pypi.
"""

import os
import subprocess
import shutil


os.chdir(r'd:\work\programming\pygmi')

shutil.rmtree(r'dist', ignore_errors=True)
shutil.rmtree(r'build', ignore_errors=True)

pipe = subprocess.run(['python', r'setup.py', 'sdist', 'bdist_wheel'],
                      capture_output=True, check=True)
print(pipe.stdout.decode())
print(pipe.stderr.decode())

pipe = subprocess.run(['twine', 'check', r'dist/*'], capture_output=True,
                      check=True)

print(pipe.stdout.decode())
print(pipe.stderr.decode())

pipe = subprocess.run(['twine', 'upload', r'dist/*',
                       '-u', 'pcole',
                       '-p', 'themightywarzone'], capture_output=True,
                      check=True)

print(pipe.stdout.decode())
print(pipe.stderr.decode())

shutil.rmtree(r'dist', ignore_errors=True)
shutil.rmtree(r'build', ignore_errors=True)
