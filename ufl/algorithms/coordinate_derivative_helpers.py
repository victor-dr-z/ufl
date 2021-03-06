# -*- coding: utf-8 -*-
"""This module provides the necessary tools to strip away and then reattach the
coordinate derivatives at the right time point in compute_form_data."""

# Copyright (C) 2018 Florian Wechsung
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

from ufl.log import error
from ufl.differentiation import CoordinateDerivative
from ufl.algorithms.multifunction import MultiFunction
from ufl.corealg.map_dag import map_expr_dags
from ufl.classes import Form, Integral


class CoordinateDerivativeIsOutermostChecker(MultiFunction):

    """ Traverses the tree to make sure that CoordinateDerivatives are only on
    the outside. The visitor returns False as long as no CoordinateDerivative
    has been seen. """

    def multi_index(self, o):
        return False

    def terminal(self, o):
        return False

    def expr(self, o, *operands):
        """ If we have already seen a CoordinateDerivative, then no other
        expressions apart from more CoordinateDerivatives are allowed to wrap
        around it. """
        if any(operands):
            error("CoordinateDerivative(s) must be outermost")
        return False

    def coordinate_derivative(self, o, expr, *_):
        return True


def assert_that_coordinate_derivatives_are_the_same(cds):
    # make sure that the coordinate derivatives that were stripped are all the
    # same
    hashes_per_integral = []
    for cd in cds:
        hsh = sum(sum(tuple_elem._ufl_compute_hash_() for tuple_elem in tuple_) for tuple_ in cd)
        hashes_per_integral.append(hsh)
    if not all(hsh == hashes_per_integral[0] for hsh in hashes_per_integral):
        error("Did not apply the same CoordinateDerivative to all integrals.")


def strip_coordinate_derivatives(form):

    if isinstance(form, Form):
        if len(form.integrals()) == 0:
            return form, None
        stripped_integrals = []
        coordinate_derivatives = []
        for integral in form.integrals():
            (si, cd) = strip_coordinate_derivatives(integral)
            stripped_integrals.append(si)
            coordinate_derivatives.append(cd)
        assert_that_coordinate_derivatives_are_the_same(coordinate_derivatives)
        # now that we have checked that the coordinate derivative that we apply is
        # the same for all integrals, we only have to return them for the first integral
        return (Form(stripped_integrals), coordinate_derivatives[0])

    elif isinstance(form, Integral):
        integral = form
        integrand = integral.integrand()
        checker = CoordinateDerivativeIsOutermostChecker()
        map_expr_dags(checker, [integrand])
        coordinate_derivatives = []

        # grab all coordinate derivatives and store them, so that we can apply
        # them later again
        def take_top_coordinate_derivatives(o):
            o_ = o.ufl_operands
            if isinstance(o, CoordinateDerivative):
                coordinate_derivatives.append((o_[1], o_[2], o_[3]))
                return take_top_coordinate_derivatives(o_[0])
            else:
                return o

        newintegrand = take_top_coordinate_derivatives(integrand)
        return (integral.reconstruct(integrand=newintegrand), coordinate_derivatives)

    else:
        error("Invalid type %s" % (form.__class__.__name__,))


def attach_coordinate_derivatives(form, coordinate_derivatives):
    if coordinate_derivatives is None:
        return form

    if isinstance(form, Form):
        cds = coordinate_derivatives
        new_integrals = [attach_coordinate_derivatives(integ, cds) for integ in form.integrals()]
        return Form(new_integrals)

    elif isinstance(form, Integral):
        integral = form
        integrand = integral.integrand()
        # apply the stored coordinate derivatives back onto the integrand
        for tup in reversed(coordinate_derivatives):
            integrand = CoordinateDerivative(integrand, tup[0], tup[1], tup[2])
        return integral.reconstruct(integrand=integrand)
    else:
        error("Invalid type %s" % (form.__class__.__name__,))
