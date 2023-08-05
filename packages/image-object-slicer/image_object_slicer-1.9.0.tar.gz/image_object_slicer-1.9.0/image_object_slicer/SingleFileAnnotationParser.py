# This file is part of image-object-slicer
# Copyright (C) 2022  Natan Junges <natanajunges@gmail.com>
#
# image-object-slicer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# image-object-slicer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with image-object-slicer.  If not, see <https://www.gnu.org/licenses/>.

class SingleFileAnnotationParser:
    """Base class that abstracts the annotation parsing in a single file."""

    glob = ""
    """The glob pattern of the file to be parsed."""

    @classmethod
    def split_file(cls, file):
        """Split a specific annotation file into annotation items."""
        return [None]

    @classmethod
    def parse_item(cls, item):
        """Parse a specific annotation item to a usable dict format."""
        return {"name": "", "slices": [{"xmin": 0.0, "ymin": 0.0, "xmax": 0.0, "ymax": 0.0, "label": ""}], "labels": {""}}
