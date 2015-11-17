# -*- coding: utf-8 -*-
# Copyright (C) 2008-2015 Martin Sandve Alnæs
#
# This file is part of UFL.
#
# UFL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with UFL. If not, see <http://www.gnu.org/licenses/>.

def id_or_none(obj):
    """Returns None if the object is None, obj.ufl_id() if available, or id(obj) if not.

    This allows external libraries to implement an alternative
    to id(obj) in the ufl_id() function, such that ufl can identify
    objects as the same without knowing about their types.
    """
    if obj is None:
        return None
    elif hasattr(obj, 'ufl_id'):
        return obj.ufl_id()
    else:
        #warning("Expecting an object implementing the ufl_id function.") # TODO: Can we enable this? Not sure about meshfunctions etc in dolfin.
        return id(obj)

def metadata_equal(a, b):
    return (sorted((k, id(v)) for k, v in list(a.items())) ==
            sorted((k, id(v)) for k, v in list(b.items())))

def metadata_hashdata(md):
    return tuple(sorted((k, id(v)) for k, v in list(md.items())))
