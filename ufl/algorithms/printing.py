"""A collection of utility algorithms for printing
of UFL objects, mostly intended for debugging purposes."""

# Copyright (C) 2008-2014 Martin Sandve Alnes
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
#
# Modified by Anders Logg 2009, 2014

from itertools import chain

from ufl.log import error
from ufl.assertions import ufl_assert
from ufl.expr import Expr
from ufl.terminal import Terminal
from ufl.form import Form
from ufl.integral import Integral, Measure
from ufl.algorithms.analysis import extract_arguments, extract_coefficients

#--- Utilities for constructing informative strings from UFL objects ---

def integral_info(integral):
    ufl_assert(isinstance(integral, Integral), "Expecting an Integral.")
    s  = "  Integral:\n"
    s += "    Type:\n"
    s += "      %s\n" % integral.integral_type()
    s += "    Domain:\n"
    s += "      %r\n" % integral.domain()
    s += "    Domain id:\n"
    s += "      %r\n" % integral.subdomain_id()
    s += "    Domain data:\n"
    s += "      %s\n" % integral.subdomain_data()
    s += "    Compiler metadata:\n"
    s += "      %s\n" % integral.metadata()
    s += "    Integrand expression representation:\n"
    s += "      %r\n" % integral.integrand()
    s += "    Integrand expression short form:\n"
    s += "      %s" % integral.integrand()
    return s

def form_info(form):
    ufl_assert(isinstance(form, Form), "Expecting a Form.")

    bf = extract_arguments(form)
    cf = extract_coefficients(form)

    ci = form.integrals_by_type("cell")
    ei = form.integrals_by_type("exterior_facet")
    ebi = form.integrals_by_type("exterior_facet_bottom")
    eti = form.integrals_by_type("exterior_facet_top")
    evi = form.integrals_by_type("exterior_facet_vert")
    ii = form.integrals_by_type("interior_facet")
    ihi = form.integrals_by_type("interior_facet_horiz")
    ivi = form.integrals_by_type("interior_facet_vert")
    pi = form.integrals_by_type("point")
    qi = form.integrals_by_type("quadrature")
    mi = form.integrals_by_type("macro_cell")

    s  = "Form info:\n"
    s += "  rank:                          %d\n" % len(bf)
    s += "  num_coefficients:              %d\n" % len(cf)
    s += "  num_cell_integrals:            %d\n" % len(ci)
    s += "  num_exterior_facet_integrals:  %d\n" % len(ei)
    s += "  num_exterior_bottom_facet_integrals:  %d\n" % len(ebi)
    s += "  num_exterior_top_facet_integrals:  %d\n" % len(eti)
    s += "  num_exterior_vert_facet_integrals:  %d\n" % len(evi)
    s += "  num_interior_facet_integrals:  %d\n" % len(ii)
    s += "  num_interior_horiz_facet_integrals:  %d\n" % len(ihi)
    s += "  num_interior_vert_facet_integrals:  %d\n" % len(ivi)
    s += "  num_point_integrals:           %d\n" % len(pi)
    s += "  num_quadrature_integrals:      %d\n" % len(qi)
    s += "  num_macro_cell_integrals:      %d\n" % len(mi)

    for f in cf:
        if f._name:
            s += "\n"
            s += "  Coefficient %d is named '%s'" % (f._count, f._name)
    s += "\n"

    for itg in ci:
        s += "\n"
        s += integral_info(itg)
    for itg in ei:
        s += "\n"
        s += integral_info(itg)
    for itg in ebi:
        s += "\n"
        s += integral_info(itg)
    for itg in eti:
        s += "\n"
        s += integral_info(itg)
    for itg in evi:
        s += "\n"
        s += integral_info(itg)
    for itg in ii:
        s += "\n"
        s += integral_info(itg)
    for itg in ihi:
        s += "\n"
        s += integral_info(itg)
    for itg in ivi:
        s += "\n"
        s += integral_info(itg)
    for itg in mi:
        s += "\n"
        s += integral_info(itg)
    return s

def _indent_string(n):
    return "    "*n

def _tree_format_expression(expression, indentation, parentheses):
    ind = _indent_string(indentation)
    if isinstance(expression, Terminal):
        s = ind + "%s" % repr(expression)
    else:
        sops = [_tree_format_expression(o, indentation+1, parentheses) for o in expression.operands()]
        s = ind + "%s\n" % expression._uflclass.__name__
        if parentheses and len(sops) > 1:
            s += ind + "(\n"
        s += "\n".join(sops)
        if parentheses and len(sops) > 1:
            s += "\n" + ind + ")"
    return s

def tree_format(expression, indentation=0, parentheses=True):
    s = ""

    if isinstance(expression, Form):
        ci = expression.integrals_by_type("cell")
        ei = expression.integrals_by_type("exterior_facet")
        ebi = expression.integrals_by_type("exterior_facet_bottom")
        eti = expression.integrals_by_type("exterior_facet_top")
        evi = expression.integrals_by_type("exterior_facet_vert")
        ii = expression.integrals_by_type("interior_facet")
        ihi = expression.integrals_by_type("interior_facet_horiz")
        ivi = expression.integrals_by_type("interior_facet_vert")
        pi = expression.integrals_by_type("point")
        qi = expression.integrals_by_type("quadrature")
        mi = expression.integrals_by_type("macro_cell")
        ind = _indent_string(indentation)
        s += ind + "Form:\n"
        s += "\n".join(tree_format(itg, indentation+1, parentheses) for itg in chain(ci, ei, ebi, eti, evi, ii, ihi, ivi, pi, qi, mi))

    elif isinstance(expression, Integral):
        ind = _indent_string(indentation)
        s += ind + "Integral:\n"
        ind = _indent_string(indentation+1)
        s += ind + "domain type: %s\n" % expression.integral_type()
        s += ind + "domain id: %s\n" % expression.subdomain_id()
        s += ind + "integrand:\n"
        s += tree_format(expression._integrand, indentation+2, parentheses)

    elif isinstance(expression, Expr):
        s += _tree_format_expression(expression, indentation, parentheses)

    else:
        error("Invalid object type %s" % type(expression))

    return s
