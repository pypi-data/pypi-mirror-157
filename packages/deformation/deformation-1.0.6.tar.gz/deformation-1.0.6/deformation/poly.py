#!/usr/bin/env python3

"""
** Polynomial transformation of order n. **
-------------------------------------------

dst(i, j) = src(poly_i(i, j), poly_y(i, j))
"""


import numbers

import numpy as np
import sympy
import torch

from deformation.core import Transform


__pdoc__ = {'InvPolyTrans': False}



class NotSolvableError(Exception):
    """
    ** In the case where we do not know how to invert the polynomial. **
    """

class TorchPoly(torch.nn.Module):
    r"""
    ** Polynomial surface. **

    \(
        P(i, j) = \sum\limits_{k=0}^N{
            \sum\limits_{l=0}^N{
                \alpha_{kl} i^k j^l
            }
        }
    \)

    Attributes
    ----------
    coeffs : torch.Tensor
        The matrix of the polynomial coeficients.
    order : int
        The order of the polynomial.

    Examples
    --------
    >>> import torch
    >>> from deformation.poly import TorchPoly
    >>> poly = TorchPoly(order=3)
    >>> i, j = torch.meshgrid(torch.arange(
    ...     4, dtype=torch.float32), torch.arange(4, dtype=torch.float32), indexing='ij')
    >>> i
    tensor([[0., 0., 0., 0.],
            [1., 1., 1., 1.],
            [2., 2., 2., 2.],
            [3., 3., 3., 3.]])
    >>> j
    tensor([[0., 1., 2., 3.],
            [0., 1., 2., 3.],
            [0., 1., 2., 3.],
            [0., 1., 2., 3.]])
    >>> poly[...] = torch.tensor([[1., 0., 0., 0.],
    ...                           [0., 0., 0., 0.],
    ...                           [0., 0., 0., 0.],
    ...                           [0., 0., 0., 0.]])
    >>> poly
    TorchPoly(1.00000000000000)
    >>> poly(i, j) # out = 1 * i**0*j**0
    tensor([[1., 1., 1., 1.],
            [1., 1., 1., 1.],
            [1., 1., 1., 1.],
            [1., 1., 1., 1.]])
    >>> poly[...] = torch.tensor([[0., 0., 0., 0.],
    ...                           [1., 0., 0., 0.],
    ...                           [0., 0., 0., 0.],
    ...                           [1., 0., 0., 0.]])
    >>> poly
    TorchPoly(1.0*i**3 + 1.0*i)
    >>> poly(i, j) # out = 1 * i**1*j**0 + 1 * i**3*j**0
    tensor([[ 0.,  0.,  0.,  0.],
            [ 2.,  2.,  2.,  2.],
            [10., 10., 10., 10.],
            [30., 30., 30., 30.]])
    >>> poly[...] = torch.tensor([[0., 1., 0., 1.],
    ...                           [0., 0., 0., 0.],
    ...                           [0., 0., 0., 0.],
    ...                           [0., 0., 0., 0.]])
    >>> poly
    TorchPoly(1.0*j**3 + 1.0*j)
    >>> poly(i, j) # out = 1 * i**0*j**1 + 1 * i**0*j**3
    tensor([[ 0.,  2., 10., 30.],
            [ 0.,  2., 10., 30.],
            [ 0.,  2., 10., 30.],
            [ 0.,  2., 10., 30.]])
    >>> poly[...] = torch.tensor([[0., 0., 0., 0.],
    ...                           [0., 0., 0., 0.],
    ...                           [0., 0., 1., 0.],
    ...                           [0., 0., 0., 0.]])
    >>> poly
    TorchPoly(1.0*i**2*j**2)
    >>> poly(i, j) # out = 1 * i**2*j**2
    tensor([[ 0.,  0.,  0.,  0.],
            [ 0.,  1.,  4.,  9.],
            [ 0.,  4., 16., 36.],
            [ 0.,  9., 36., 81.]])
    >>>

    Notes
    -----
    Input/output is not checked because this class
    is not intended to be directly used by the user.
    It is an internal variable which allows to help the detortion of the image.
    """

    def __init__(self, order):
        """
        Parameters
        ----------
        order : int
            The order of the polynomial, ie the highest power.
            So there are ``(order+1)**2`` parameters in the model.
        """
        assert isinstance(order, numbers.Integral), order.__class__.__name__
        assert order > 0

        super().__init__()

        self.coeffs = torch.nn.Parameter(torch.zeros((order+1), (order+1)), requires_grad=False)
        power = torch.arange(order+1, device=self.coeffs.device, dtype=self.coeffs.dtype)
        i_power, j_power = torch.meshgrid(power, power, indexing='ij')
        self.i_power, self.j_power = i_power.ravel(), j_power.ravel()

    def __getstate__(self):
        """
        ** Retrieve the coefficients. **
        """
        return self.coeffs.detach().cpu().clone(), self.coeffs.requires_grad, self.coeffs.device

    def __repr__(self):
        """
        ** Offers meaningful but non-evaluable representation. **

        Examples
        --------
        >>> from deformation.poly import TorchPoly
        >>> TorchPoly(order=3)
        TorchPoly(0)
        >>> _[0, 0] = 1
        >>> _
        TorchPoly(1.00000000000000)
        >>> _[1, 0] = 2
        >>> _
        TorchPoly(2.0*i + 1.0)
        >>> _[0, 3] = 3
        >>> _
        TorchPoly(2.0*i + 3.0*j**3 + 1.0)
        >>> _[2, 2] = -1
        >>> _
        TorchPoly(-1.0*i**2*j**2 + 2.0*i + 3.0*j**3 + 1.0)
        >>>
        """
        i_sym, j_sym = sympy.symbols('i j', real=True)
        expr = sum(
            self.coeffs.detach().cpu().numpy().ravel()
            * i_sym**self.i_power.detach().cpu().numpy().astype(int)
            * j_sym**self.j_power.detach().cpu().numpy().astype(int)
        )
        return f'{self.__class__.__name__}({expr})'

    def __setitem__(self, item, value):
        """
        ** Simplifies the handling of coeffs by avoiding the ``RuntimeError`` error. **

        Syntax shortcut for ``self[item] = value``.
        Because ``self.coeffs[item] = value`` raises:
        RuntimeError: a view of a leaf Variable that requires grad
        is being used in an in-place operation.

        Examples
        --------
        >>> from deformation.poly import TorchPoly
        >>> poly = TorchPoly(order=3)
        >>> poly.coeffs
        Parameter containing:
        tensor([[0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.]])
        >>> poly[0, 0] = 1
        >>> poly.coeffs
        Parameter containing:
        tensor([[1., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.]])
        >>>
        """
        coeffs_copy = self.coeffs.detach()
        coeffs_copy[item] = value
        self.coeffs = torch.nn.Parameter(coeffs_copy, requires_grad=self.coeffs.requires_grad)

    def __setstate__(self, state):
        """
        ** Reinjects the coefficients. **
        """
        coeffs, requires_grad, device = state
        TorchPoly.__init__(self, coeffs.shape[0]-1)
        self.coeffs = torch.nn.Parameter(
            coeffs.to(device=device), requires_grad=requires_grad
        )

    def copy(self):
        """
        ** Returns a clone of the polynomial. **

        Examples
        --------
        >>> from deformation.poly import TorchPoly
        >>> poly = TorchPoly(1)
        >>> poly[1, 0] = 1
        >>> poly
        TorchPoly(1.0*i)
        >>> poly_bis = poly.copy()
        >>> poly_bis
        TorchPoly(1.0*i)
        >>> poly_bis[0, 1] = 1
        >>> poly_bis
        TorchPoly(1.0*i + 1.0*j)
        >>> poly # not modified
        TorchPoly(1.0*i)
        >>>
        """
        poly_copy = TorchPoly(order=self.order)
        poly_copy.__setstate__(self.__getstate__())
        return poly_copy

    def diff(self, axis):
        r"""
        ** Returns the first derivative of the polynomial on an axis. **

        \(
            \frac{\partial P(i, j)}{\partial i} =
            \frac{\partial \sum\limits_{k=0}^N\sum\limits_{l=0}^N \alpha_{kl} i^k j^l}{\partial i} =
            \sum\limits_{k=1}^N\sum\limits_{l=0}^N k \alpha_{kl} i^{k-1} j^l =
            \sum\limits_{k=0}^{N-1}\sum\limits_{l=0}^N (k+1) \alpha_{k+1,l} i^k j^l =
            \sum\limits_{k=0}^N\sum\limits_{l=0}^N \beta_{kl} i^k j^l
        \)

        or

        \(
            \frac{\partial P(i, j)}{\partial j} =
            \frac{\partial \sum\limits_{k=0}^N\sum\limits_{l=0}^N \alpha_{kl} i^k j^l}{\partial j} =
            \sum\limits_{k=0}^N\sum\limits_{l=1}^N l \alpha_{kl} i^k j^{l-1} =
            \sum\limits_{k=0}^N\sum\limits_{l=0}^{N-1} (l+1) \alpha_{k,l+1} i^k j^l =
            \sum\limits_{k=0}^N\sum\limits_{l=0}^N \beta_{kl} i^k j^l
        \)

        according to the chosen axis

        Parameters
        ----------
        axis : str
            'i' or 'j', the derivation variable.

        Returns
        -------
        TorchPoly
            The polynomial \(P^{\prime}\), derives from ``self`` along the ``axis`` axis.

        Examples
        --------
        >>> import torch
        >>> from deformation.poly import TorchPoly
        >>> poly = TorchPoly(order=4)
        >>> poly[:, :] = torch.tensor([[1., 0., 0., 2., 0.],
        ...                            [0., 0., 0., 0., 0.],
        ...                            [0., 0., 1., 0., 0.],
        ...                            [0., 0., 0., 0., 0.],
        ...                            [2., 0., 0., 0., 0.]])
        >>> poly
        TorchPoly(2.0*i**4 + 1.0*i**2*j**2 + 2.0*j**3 + 1.0)
        >>> poly.diff('i')
        TorchPoly(8.0*i**3 + 2.0*i*j**2)
        >>> poly.diff('i').diff('i')
        TorchPoly(24.0*i**2 + 2.0*j**2)
        >>> poly.diff('j')
        TorchPoly(2.0*i**2*j + 6.0*j**2)
        >>>
        """
        assert isinstance(axis, str), axis.__class__.__name__
        assert axis in {'i', 'j'}, axis

        diff = TorchPoly(order=self.order)
        ref_coeffs = self.coeffs if axis == 'i' else self.coeffs.T

        coeffs = torch.zeros_like(diff.coeffs)
        coeffs[:-1, :] = (
            ref_coeffs * torch.arange(
                diff.coeffs.shape[0],
                device=diff.coeffs.device,
                dtype=diff.coeffs.dtype
            ).reshape(-1, 1)
        )[1:, :]
        diff.coeffs = torch.nn.Parameter(coeffs)

        if axis == 'j':
            diff.coeffs = torch.nn.Parameter(diff.coeffs.T)
        return diff

    def forward(self, i_tensor, j_tensor):
        """
        ** Eval the surface at the positions i and j. **

        Returns
        -------
        z_tensor : torch.Tensor
            The evaluation of the function at the given points.
            The shape is the same as input.
        """
        return torch.sum(
            (
                self.coeffs.ravel().unsqueeze(0)
                * i_tensor.unsqueeze(-1)**self.i_power.unsqueeze(0)
                * j_tensor.unsqueeze(-1)**self.j_power.unsqueeze(0)
            ),
            axis=-1
        )

    @property
    def order(self):
        """
        ** The polynomial order. **
        """
        return self.coeffs.shape[0] - 1


class InvPolyTrans(Transform):
    """
    ** Formal inversion of a polynomial. **
    """

    def __init__(self, i_src, j_src, i_dst, j_dst, *exprs, **kwargs):
        """
        Parameters
        ----------
        i_src : sympy.Symbol
            Represents the i coordinate of the polynomial source.
        j_src : sympy.Symbol
            Represents the j coordinate of the polynomial source.
        i_dst : sympy.Symbol
            Represents the i coordinate of the polynomial destination.
        j_dst : sympy.Symbol
            Represents the j coordinate of the polynomial destination.
        *exprs: tuple
            Expressions for expressing i_src and j_ src as a function of i_dst and j_dst.
        **kwarg : dict
            Passed to initializers of parent transformation classes.
        """
        assert isinstance(i_src, sympy.Symbol), i_src.__class__.__name__
        assert isinstance(j_src, sympy.Symbol), j_src.__class__.__name__
        assert isinstance(i_dst, sympy.Symbol), i_dst.__class__.__name__
        assert isinstance(j_dst, sympy.Symbol), j_dst.__class__.__name__
        assert len(exprs) == 2, len(exprs)
        exprs_1, exprs_2 = exprs
        assert isinstance(exprs_1, list), exprs_1.__class__.__name__
        assert isinstance(exprs_2, list), exprs_2.__class__.__name__
        assert all(isinstance(d, dict) for d in exprs_1), [e.__class__.__name__ for e in exprs_1]
        assert all(isinstance(d, dict) for d in exprs_2), [e.__class__.__name__ for e in exprs_2]
        key_1 = set.union(*(set(d.keys()) for d in exprs_1))
        key_2 = set.union(*(set(d.keys()) for d in exprs_2))
        assert len(key_1) == 1, key_1
        assert len(key_2) == 1, key_2
        key_1, key_2 = key_1.pop(), key_2.pop()
        assert key_1 != key_2, (key_1, key_2)
        assert key_1 in {i_src, j_src}, key_1
        assert key_2 in {i_src, j_src}, key_2
        exprs_1, exprs_2 = [d[key_1] for d in exprs_1], [d[key_2] for d in exprs_2]
        assert all(isinstance(e, sympy.Expr) for e in exprs_1), [e.__class__ for e in exprs_1]
        assert all(isinstance(e, sympy.Expr) for e in exprs_2), [e.__class__ for e in exprs_2]
        assert all(e.free_symbols.issubset({i_dst, j_dst}) for e in exprs_1), \
            [e.free_symbols for e in exprs_1]
        assert all(e.free_symbols.issubset({key_1, i_dst, j_dst}) for e in exprs_2), \
            [e.free_symbols for e in exprs_2]

        super().__init__(**kwargs)

        self.symbols = i_src, j_src, i_dst, j_dst
        self.exprs_1, self.exprs_2 = exprs_1, exprs_2

        # compilation
        self._exprs_1 = [
            sympy.lambdify([i_dst, j_dst], e, modules='numpy', cse=True)
            for e in exprs_1
        ]
        self._exprs_2 = [
            sympy.lambdify([key_1, i_dst, j_dst], e, modules='numpy', cse=True)
            for e in exprs_2
        ]
        self._order_is_ij = (key_1 == i_src)

    def warp_points(self, points_i, points_j):
        """
        ** Combines formal expressions. **
        """
        out_points_1 = np.full(points_i.shape, np.nan)
        out_points_2 = np.full(points_i.shape, np.nan)
        for expr_1 in self._exprs_1:
            out_points_1 = np.where(
                np.isnan(out_points_1), expr_1(points_i, points_j), out_points_1
            )
        for expr_2 in self._exprs_2:
            out_points_2 = np.where(
                np.isnan(out_points_2), expr_2(out_points_1, points_i, points_j), out_points_2
            )
        if self._order_is_ij:
            return out_points_1, out_points_2
        return out_points_2, out_points_1


class PolyTransform(Transform):
    """
    ** Any polynomial transformation. **

    Attributes
    ----------
    poly_i : TorchPoly
        The provide polynomial.
    poly_j : TorchPoly
        The provide polynomial.

    Examples
    --------
    >>> from deformation.poly import TorchPoly, PolyTransform
    >>> poly_i = TorchPoly(2)
    >>> poly_i[0, 2] = 1
    >>> PolyTransform(poly_i=poly_i, src_shape=(1, 4))
    PolyTransform(TorchPoly(1.0*j**2), TorchPoly(1.0*j))
    >>> _([0., 0., 0., 0., 0.], [0., 1., 2., 3., 4.])
    (array([1.   , 0.625, 0.5  , 0.625, 1.   ]), array([0., 1., 2., 3., 4.]))
    >>>
    """

    def __init__(self, poly_i=None, poly_j=None, src_shape=None, **kwargs):
        """
        Parameters
        ----------
        poly_i : TorchPoly
            The deformation field along the i axis.
        poly_j : TorchPoly
            The deformation field along the j axis.
        src_shape : tuple
            See ``deformation.core.Transform``.
            This parameter is essential because the coordinates
            of the image are brought back between -1 and 1 to limit the risk of divergence.
        **kwargs : dict
            Passed to initializers of parent transformation classes.
        """
        if poly_i is None:
            poly_i = TorchPoly(order=1)
            poly_i[1, 0] = 1
        if poly_j is None:
            poly_j = TorchPoly(order=1)
            poly_j[0, 1] = 1
        assert isinstance(poly_i, TorchPoly), poly_i.__class__.__name__
        assert isinstance(poly_j, TorchPoly), poly_j.__class__.__name__
        assert src_shape is not None, 'you must provide this value'

        self.poly_i = poly_i.copy()
        self.poly_j = poly_j.copy()

        super().__init__(src_shape=src_shape, **kwargs)

    def __getstate__(self):
        return self.poly_i, self.poly_j, self.src_shape, self.dst_shape

    def __repr__(self):
        return f'{self.__class__.__name__}({self.poly_i}, {self.poly_j})'

    def __setstate__(self, state):
        poly_i, poly_j, src_shape, dst_shape = state
        PolyTransform.__init__(self, poly_i, poly_j, src_shape=src_shape, dst_shape=dst_shape)

    def _translation(self, dep_i, dep_j):
        dep_rel_i, dep_rel_j = 2*dep_i/self.src_shape[0], 2*dep_j/self.src_shape[1]
        self.poly_i[0, 0] = self.poly_i.coeffs[0, 0] + dep_rel_i
        self.poly_j[0, 0] = self.poly_j.coeffs[0, 0] + dep_rel_j

    def forward(self, field_i, field_j):
        """
        ** Like 'apply_points_trans' but differentiable torch. **

        Parameters
        ----------
        field_i : torch.Tensor
            The coordinates along the i axis.
        field_j : torch.Tensor
            The coordinates along the j axis.

        Returns
        -------
        out_fields : tuple
            The fields of the new i and j values.
        """
        assert isinstance(field_i, torch.Tensor), field_i.__class__.__name__
        assert isinstance(field_j, torch.Tensor), field_j.__class__.__name__
        return self.poly_i(field_i, field_j), self.poly_j(field_i, field_j)

    def _reverse(self, *, try_formal=False, **kwargs):
        """
        Parameters
        ----------
        try_formal : boolean
            If True, attempts to find the exact expression for the inverse of the polynomial.
        """
        if try_formal:
            try:
                return self._reverse_symb()
            except NotSolvableError:
                pass
        return self._reverse_approx(**kwargs)

    def _reverse_approx(self, *, order=None):
        """
        ** Approximation of the inverse field by minimisation of reverse distance. **

        Parameters
        ----------
        order : int
            The order of the reversed polynomes. By default, the same order is used.

        Returns
        -------
        PolyTransform
            An approximation of the inverse deformation field.
        """
        if order is None:
            order = max(self.poly_i.order, self.poly_j.order)
        assert isinstance(order, numbers.Integral), order.__class__.__name__
        assert order > 0

        # creation of the new polynomials
        q_i = TorchPoly(order)
        q_i[0, 0] = -self.poly_i.coeffs[0, 0]
        q_i[1, 0] = 1 / self.poly_i.coeffs[1, 0]
        q_i.coeffs.requires_grad = True
        q_j = TorchPoly(order)
        q_j[0, 0] = -self.poly_j.coeffs[0, 0]
        q_j[0, 1] = 1 / self.poly_j.coeffs[0, 1]
        q_j.coeffs.requires_grad = True

        # precomputing
        i_src_rel, j_src_rel = torch.meshgrid(
            torch.linspace(-1, 1, 21),
            torch.linspace(-1, 1, 21),
            indexing='ij',
        )
        i_dst_rel = self.src_shape[0]/self.dst_shape[0]*(self.poly_i(i_src_rel, j_src_rel) + 1) - 1
        j_dst_rel = self.src_shape[1]/self.dst_shape[1]*(self.poly_j(i_src_rel, j_src_rel) + 1) - 1

        # fit for minimize the loss
        optimizer_i = torch.optim.Adam(q_i.parameters(), lr=5e-3)
        optimizer_j = torch.optim.Adam(q_j.parameters(), lr=5e-3)
        scheduler_i = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer_i, factor=.5, patience=3)
        scheduler_j = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer_j, factor=.5, patience=3)
        for _ in range(400*order):
            loss_i = torch.mean(
                (
                    self.dst_shape[0]/self.src_shape[0]*(q_i(i_dst_rel, j_dst_rel) + 1) - 1
                    # q_i(i_dst_rel, j_dst_rel)
                    - i_src_rel
                )**2
            )
            loss_j = torch.mean(
                (
                    self.dst_shape[1]/self.src_shape[1]*(q_j(i_dst_rel, j_dst_rel) + 1) - 1
                    # q_j(i_dst_rel, j_dst_rel)
                    - j_src_rel
                )**2
            )
            scheduler_i.step(loss_i)
            scheduler_j.step(loss_j)
            optimizer_i.zero_grad()
            optimizer_j.zero_grad()
            loss_i.backward()
            loss_j.backward()
            torch.nn.utils.clip_grad_norm_([q_i.coeffs, q_j.coeffs], 1)
            optimizer_i.step()
            optimizer_j.step()

        # instanciation of the reversed polynome
        q_i.coeffs.requires_grad = False
        q_j.coeffs.requires_grad = False
        return PolyTransform(
            poly_i=q_i, poly_j=q_j, src_shape=self.dst_shape, dst_shape=self.src_shape
        )

    def _reverse_symb(self):
        """
        ** Try if possible to find the exact expression of the inverse. **

        Examples
        --------
        >>> from torch import tensor
        >>> from deformation.poly import TorchPoly, PolyTransform
        >>> i_src, j_src = torch.meshgrid(
        ...     torch.linspace(-1, 1, 5),
        ...     torch.linspace(-1, 1, 5),
        ...     indexing='ij')
        >>> poly_i = TorchPoly(2)
        >>> poly_j = TorchPoly(1)
        >>> poly_i[...] = tensor([[3., 0., .5],
        ...                       [1., 0., 0.],
        ...                       [0., 0., 0.]])
        >>> poly_j[...] = tensor([[-1., 1.],
        ...                       [ .5, 0.]])
        >>> PolyTransform(src_shape=(1, 1))
        PolyTransform(TorchPoly(1.0*i), TorchPoly(1.0*j))
        >>> i_fin, j_fin = _._reverse_symb()(*_(i_src, j_src))
        >>> i_fin
        tensor([[-1.0000, -1.0000, -1.0000, -1.0000, -1.0000],
                [-0.5000, -0.5000, -0.5000, -0.5000, -0.5000],
                [ 0.0000,  0.0000,  0.0000,  0.0000,  0.0000],
                [ 0.5000,  0.5000,  0.5000,  0.5000,  0.5000],
                [ 1.0000,  1.0000,  1.0000,  1.0000,  1.0000]])
        >>> j_fin
        tensor([[-1.0000, -0.5000,  0.0000,  0.5000,  1.0000],
                [-1.0000, -0.5000,  0.0000,  0.5000,  1.0000],
                [-1.0000, -0.5000,  0.0000,  0.5000,  1.0000],
                [-1.0000, -0.5000,  0.0000,  0.5000,  1.0000],
                [-1.0000, -0.5000,  0.0000,  0.5000,  1.0000]])
        >>> PolyTransform(poly_i=poly_i, src_shape=(1, 1))
        PolyTransform(TorchPoly(1.0*i + 0.5*j**2 + 3.0), TorchPoly(1.0*j))
        >>> i_fin, j_fin = _._reverse_symb()(*_(i_src, j_src))
        >>> (abs(i_fin - i_src) < 1e-6).all()
        tensor(True)
        >>> (abs(j_fin - j_src) < 1e-6).all()
        tensor(True)
        >>> _ = PolyTransform(poly_i=poly_i, poly_j=poly_j, src_shape=(1, 1))
        >>> i_fin, j_fin = _._reverse_symb()(*_(i_src, j_src))
        >>> (abs(i_fin - i_src) < 1e-6).all()
        tensor(True)
        >>> (abs(j_fin - j_src) < 1e-6).all()
        tensor(True)
        >>>
        """
        i_src, j_src, i_dst, j_dst = sympy.symbols('i_src j_src i_dst j_dst', real=True)

        # forward
        i_dst_, j_dst_ = 2*(i_src/self.src_shape[0])-1, 2*(j_src/self.src_shape[1])-1
        i_dst_, j_dst_ = (
            sum(
                self.poly_i.coeffs.detach().cpu().numpy().ravel()
                * i_dst_**self.poly_i.i_power.detach().cpu().numpy().astype(int)
                * j_dst_**self.poly_i.j_power.detach().cpu().numpy().astype(int)
            ),
            sum(
                self.poly_j.coeffs.detach().cpu().numpy().ravel()
                * i_dst_**self.poly_j.i_power.detach().cpu().numpy().astype(int)
                * j_dst_**self.poly_j.j_power.detach().cpu().numpy().astype(int)
            ),
        )
        i_dst_, j_dst_ = .5*(i_dst_+1)*self.src_shape[0], .5*(j_dst_+1)*self.src_shape[1]


        # substitution
        (eq_1, _), (eq_2, _) = (
            sympy.poly_from_expr(i_dst - i_dst_, i_src, j_src),
            sympy.poly_from_expr(j_dst - j_dst_, i_src, j_src),
        ) # polynomial object for performance
        eq_1, eq_2 = sorted([eq_1, eq_2], key=lambda p: min(p.degree(i_src), p.degree(j_src)))
        eq_1 = [e for e in (sympy.poly(eq_1, i_src), sympy.poly(eq_1, j_src)) if e.degree() == 1]
        if not eq_1:
            raise NotSolvableError('not solvable degres to hight')
        eq_1 = min(eq_1, key=lambda p: p.degree())
        eq_1 = sympy.solve(eq_1.as_expr(eq_1.gen), eq_1.gen, dict=True)
        if not eq_1:
            raise NotSolvableError('not solvable')
        eq_1 = sorted(eq_1, key=lambda d: (
            1 if any(e.atoms(sympy.core.numbers.ImaginaryUnit) for e in d.values()) else 0,
            sum(sympy.count_ops(e) for e in d.values())
            )
        ) # list of {i_or_j: expr}
        subs = eq_1[0]

        # resolution
        eq_2 = eq_2.as_expr(subs.get(i_src, i_src), subs.get(j_src, j_src))
        eq_2 = sympy.solve(eq_2, (eq_2.free_symbols & {i_src, j_src}).pop(), dict=True)
        if not eq_2:
            raise NotSolvableError('not solvable')
        eq_2 = sorted(eq_2, key=lambda d: (
            1 if any(e.atoms(sympy.core.numbers.ImaginaryUnit) for e in d.values()) else 0,
            sum(sympy.count_ops(e) for e in d.values())
            )
        )

        # compilation
        return InvPolyTrans(
            i_src, j_src, i_dst, j_dst,
            eq_2, eq_1,
            src_shape=self.dst_shape, dst_shape=self.src_shape
        )

    def warp_points(self, points_i, points_j):
        """
        ** Apply direct transformation. **

        The values are reduced between -1 and 1, the internal unit is therefore no longer in pxl.

        Examples
        --------
        >>> import torch
        >>> from deformation.poly import TorchPoly, PolyTransform
        >>> poly_i = TorchPoly(order=2)
        >>> poly_i[2, 0] = 1
        >>> ptsi = ptsj = torch.arange(5, dtype=torch.float32)
        >>> poly_i(ptsi, ptsj)
        tensor([ 0.,  1.,  4.,  9., 16.])
        >>> PolyTransform(poly_i=poly_i, src_shape=(4, 1))(ptsi, ptsj)[0]
        tensor([4.0000, 2.5000, 2.0000, 2.5000, 4.0000])
        >>> PolyTransform(poly_i=poly_i, src_shape=(16, 1))(ptsi, ptsj)[0]
        tensor([16.0000, 14.1250, 12.5000, 11.1250, 10.0000])
        >>> # there are no consequences on the linear term
        >>> PolyTransform(src_shape=(4, 1))(ptsi, ptsj)[0]
        tensor([0., 1., 2., 3., 4.])
        >>> PolyTransform(src_shape=(16, 1))(ptsi, ptsj)[0]
        tensor([0., 1., 2., 3., 4.])
        >>>
        """
        points_i, points_j = torch.from_numpy(points_i), torch.from_numpy(points_j)
        points_i, points_j = 2*(points_i/self.src_shape[0])-1, 2*(points_j/self.src_shape[1])-1
        points_i, points_j = self.forward(points_i, points_j)
        points_i, points_j = .5*(points_i+1)*self.src_shape[0], .5*(points_j+1)*self.src_shape[1]
        points_i, points_j = points_i.detach().cpu().numpy(), points_j.detach().cpu().numpy()
        return points_i, points_j
