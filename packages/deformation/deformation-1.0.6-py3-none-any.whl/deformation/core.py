#!/usr/bin/env python3

"""
** Handles geometric transformations. **
----------------------------------------

Allows to interpolate images and also points.
"""

import copy
import logging
import numbers

import cv2
import numpy as np
import torch

from deformation.padding import blur_contour


__pdoc__ = {
    'Transform.__add__': True,
    'Transform.__bool__': True,
    'Transform.__call__': True,
    'Transform.__radd__': True,
    'Transform.warp_image': False,
    'Transform.warp_image_inv': False,
    'Transform.warp_points': False,
    'Transform.warp_points_inv': False,
}



def _mark(meth):
    """
    ** Add an attribute saying that the object is marked. **

    This allows to detect the fact that a method is rewritten.
    The detection is done via the ``_is_marked`` function.

    Examples
    --------
    >>> from deformation.core import _mark, _is_marked
    >>> class A:
    ...     @_mark
    ...     def f(self):
    ...         pass
    ...     def g(self):
    ...         pass
    ...     @_mark
    ...     def h(self):
    ...         pass
    ...
    >>> class B(A):
    ...     def f(self):
    ...         pass
    ...
    >>> a = A()
    >>> b = B()
    >>> _is_marked(a.f)
    True
    >>> _is_marked(a.g)
    False
    >>> _is_marked(b.f)
    False
    >>> _is_marked(b.g)
    False
    >>> _is_marked(b.h)
    True
    >>>
    """
    setattr(meth, '_mark', None)
    return meth

def _is_marked(meth):
    """
    ** Used to detect if a method is marked. **

    See ``_mark``.

    Returns
    -------
    boolean
        True is the methode is not overwiten, False overwise.
    """
    return hasattr(meth, '_mark')

def _remap(image, field_i, field_j):
    """
    ** Alias to cv2. **
    """
    return cv2.remap(
        image, field_j, field_i,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


class Transform:
    """
    ** Base class for basic transformations. **

    By convention, assume that the direct transformation takes place from space A to space B.

    Attributes
    ----------
    src_shape : list
        The dimensions (i, j) of the input image. In the source A space.
        If not specified, is None.
    dst_shape : list
        The dimensions (i, j) of the output image. In the destination B space.
        If not specified, is None.
    """

    def __init__(self, src_shape=None, dst_shape=None, crop_and_pad=False):
        """
        Parameters
        ----------
        src_shape : tuple, optional
            The dimensions of the input image. If they are provided, this allows
            (if one of the crop or pad flags is activated) to calculate
            the parameters allowing to satisfy the need stated by the flags.
        dst_shape : tuple, optional
            The imposed size of the output image, if this value is imposed,
            then the 'crop_and_pad' option cannot be activated.
        crop_and_pad : boolean, default=False
            If True, modifies the position and size of the output image
            so as not to leave an empty band on one of the edges of the image
            and no part of the source image is truncated in the destination image.
            Requires the 'src_shape' value to be provided.
            Attention, that modifies the term of translation of the matrix provided.
        """
        if src_shape is not None:
            assert hasattr(src_shape, '__iter__'), src_shape.__class__.__name__
            src_shape = list(src_shape)
            assert len(src_shape) == 2, len(src_shape)
            assert isinstance(src_shape[0], numbers.Integral), src_shape[0].__class__.__name__
            assert isinstance(src_shape[1], numbers.Integral), src_shape[1].__class__.__name__
            assert src_shape[0] > 0 and src_shape[1] > 0, src_shape
        if dst_shape is not None:
            assert hasattr(dst_shape, '__iter__'), dst_shape.__class__.__name__
            dst_shape = list(dst_shape)
            assert len(dst_shape) == 2, len(dst_shape)
            assert isinstance(dst_shape[0], numbers.Integral), dst_shape[0].__class__.__name__
            assert isinstance(dst_shape[1], numbers.Integral), dst_shape[1].__class__.__name__
            assert dst_shape[0] > 0 and dst_shape[1] > 0, dst_shape
        assert isinstance(crop_and_pad, bool), crop_and_pad.__class__.__name__
        if crop_and_pad and src_shape is None:
            raise AttributeError("if 'crop_and_pad' is True, 'src_shape' must be provide")
        if crop_and_pad and dst_shape is not None:
            raise AttributeError(
                "the option 'crop_and_pad' allows when it is at True, to deduce "
                "'dst_shape', it is thus not necessary to provide 'dst_shape'"
            )

        self.src_shape = src_shape
        self.dst_shape = copy.copy(src_shape if crop_and_pad else (dst_shape or src_shape))
        self.reverse_instance = None

        if crop_and_pad:
            i_points, j_points = np.meshgrid(
                np.linspace(0, src_shape[0], 21),
                np.linspace(0, src_shape[1], 21),
                indexing='ij'
            )
            i_points, j_points = self.apply_points_trans(i_points, j_points)

            # borders touching the origin
            dep_i = -np.min(i_points)
            self.dst_shape[0] += dep_i
            i_points -= np.min(i_points)
            dep_j = -np.min(j_points)
            self.dst_shape[1] += dep_j
            j_points -= np.min(j_points)
            self._translation(dep_i, dep_j)

            # borders facing the origin
            self.dst_shape[0] = np.max(i_points)
            self.dst_shape[1] = np.max(j_points)

            # correction
            self.dst_shape[0] = max(1, round(np.ceil(self.dst_shape[0])))
            self.dst_shape[1] = max(1, round(np.ceil(self.dst_shape[1])))

    def __add__(self, other):
        """
        ** Concatenation of transformations. **

        Can be overloaded to actually compute the simplified expression,
        limiting error propagation and optimizing computations.

        Returns
        -------
        Transform
            A new transformation that is equivalent to apply
            successively ``self`` and ``other`` after ``self``.

        Examples
        --------
        >>> from deformation.core import AbstractTransform
        >>> AbstractTransform('a') + AbstractTransform('b')
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>>
        """
        if not isinstance(other, Transform):
            return NotImplemented
        return ChainTransform(self, other)

    def __bool__(self):
        """
        ** Returns True while the transformation is not identity. **
        """
        return True

    def __call__(self, *img_or_pts, **kwargs):
        """
        ** Parse to ``Transform.apply_img_trans`` and ``Transform.apply_points_trans``. **

        Parameters
        ----------
        *img_or_pts: tuple
            If only 1 element is provided, it is considered as an image.
            If 2 elements are provided, they are considered to be
            the points along i then the points along j.
        **kwargs : dict
            Transmited to the concerned functions.
        """
        if len(img_or_pts) == 1:
            return self.apply_img_trans(*img_or_pts, **kwargs)
        if len(img_or_pts) == 2:
            return self.apply_points_trans(*img_or_pts, **kwargs)
        raise ValueError(f'img_or_pts must be of len 1 or 2, not {len(img_or_pts)}')

    def __getstate__(self):
        """
        ** Returns compact information for pickle. **
        """
        logging.warning("'__getstate__' method is not overridden")
        return {k: v for k, v in self.__dict__.items() if k != 'reverse_instance'}

    def __radd__(self, other):
        """
        ** Like `__add__` but in reverse order. **

        In the general case, the composition of geometric transformations is not a commutative law.
        """
        if not isinstance(other, Transform):
            return NotImplemented
        return ChainTransform(other, self)

    def __repr__(self):
        """
        ** Returns a nice presentation. **
        """
        args = ', '.join(
            f'{k}={repr(v)}'
            for k, v in self.__dict__.items()
            if not k.startswith('_') and k != 'reverse_instance' and v is not None
        )
        return f'{self.__class__.__name__}({args})'

    def __setstate__(self, state):
        """
        ** Allows you to correctly fill the object. **
        """
        logging.warning("'__setstate__' method is not overridden")
        for key, value in state.items():
            setattr(self, key, value)

    @staticmethod
    def _get_identity_field(shape):
        """
        ** Retrieve Identity Deformation Field. **

        Parameters
        ----------
        shape : tuple
            The dimension of the field.

        Returns
        -------
        i_field : np.ndarray
            The deformation field ``i_dst = i_field[i_srcm j_src]``.
        j_field : np.ndarray
            The deformation field ``i_dst = j_field[i_srcm j_src]``.
        """
        i_field, j_field = np.meshgrid(
            np.arange(shape[0], dtype=np.float32),
            np.arange(shape[1], dtype=np.float32),
            indexing='ij'
        )
        return i_field, j_field

    @_mark
    def _reverse(self):
        """
        ** Returns a bijection of self. **

        Returns
        -------
        Transform
            A new instance of the bijection of this transformation.

        Notes
        -----
        It is advised to rewrite this method for performance reasons.
        If this method is defined, it is no longer necessary to define
        the ``warp_points_inv`` method.
        """
        if _is_marked(self.warp_points) or _is_marked(self.warp_points_inv):
            raise NotImplementedError(
                "if 'reverse' is not implemented, "
                "it is necessary to implement the 2 methods 'warp_points' and 'warp_points_inv'"
            )
        return InverseTransform(self)

    def _translation(self, dep_i, dep_j):
        """
        ** In-place translation of the output image. **

        Parameters
        ----------
        dep_i : float
            The deplacement value along the i axis, ``dep_i>0 => lower output``.
        dep_j : float
            The deplacement value along the j axis, ``dep_j>0 => righter output``.

        A positive value on r i indicates that the final image will end up lower.
        Similarly, a positive value on j has the effect of shifting the output image to the right.

        Notes
        -----
        Must not touch the ``dst_shape`` attribute.
        """
        raise RuntimeError(
            "The '_translation' method must be implemented if you set 'crop_and_pad=True'."
        )

    def apply_img_trans(self, image, *, blur_font=True):
        """
        ** Takes care of the homogeneity of the data. **

        Transfere the data from the space A to the space B.
        It is based on the ``warp_image`` method.

        Parameters
        ----------
        image : arraylike
            Any kind of array in any data type in the A space.
        blur_font : boolean
            If True and the image shape > (5, 5), apply a median filter on
            the border of the image in order to smooth the background.

        Returns
        -------
        out_image : arraylike
            An homogeneous version of ``image`` interpolated in the B space.
        """
        assert isinstance(blur_font, bool), blur_font.__class__.__name__

        if isinstance(image, np.ndarray):
            if image.ndim == 2:
                if issubclass(image.dtype.type, np.float32):
                    if self.src_shape is not None and self.src_shape != list(image.shape):
                        message = (
                            f'the source image should have a dimension of {self.src_shape} '
                            f'but the actual dimension is {image.shape}'
                        )
                        logging.warning(message)
                    if blur_font and image.size > 5 * 5:
                        image = blur_contour(image)
                    return self.warp_image(image)
                return self.apply_img_trans(image.astype(np.float32)).astype(image.dtype.type)
            if image.ndim <= 1:
                raise ValueError(
                    f'the image {image} have to minium 2 dimensions, not {image.shape}'
                )
            return np.concatenante(list(map(self.apply_img_trans, image)))
        if isinstance(image, torch.Tensor):
            return torch.from_numpy(
                self.apply_img_trans(image.detach().cpu().numpy()),
            ).to(device=image.device)
        return self.apply_img_trans(np.array(image))

    def apply_points_trans(self, points_i, points_j):
        """
        ** Takes care of the homogeneity of the data. **

        Transfere the data from the space A to the space B.
        It is based on the ``warp_points`` method.

        Parameters
        ----------
        points_i : arraylike
            Any kind of array in any data type in the A space
            representing the i coordinates of the points.
        points_j : arraylike
            Any kind of array in any data type in the A space
            representing the j coordinates of the points.

        Returns
        -------
        out_points_i : arraylike
            An homogeneous version of ``i_points`` interpolated in the B space.
        out_points_j : arraylike
            An homogeneous version of ``j_points`` interpolated in the B space.
        """
        if points_i.__class__ != points_j.__class__:
            raise ValueError(
                'points_i and points_j are different type, '
                f'{points_i.__class__.__name__} vs {points_j.__class__.__name__}'
            )
        if isinstance(points_i, np.ndarray):
            if points_i.ndim != 1:
                points_i_rav, points_j_rav = self.apply_points_trans(
                    points_i.ravel(), points_j.ravel()
                )
                points_i_rav.resize(*points_i.shape)
                points_j_rav.resize(*points_j.shape)
                return points_i_rav, points_j_rav
            points_i_out, points_j_out = self.warp_points(points_i, points_j)
            if issubclass(points_i.dtype.type, numbers.Integral):
                np.round(points_i_out, out=points_i_out)
            if issubclass(points_j.dtype.type, numbers.Integral):
                np.round(points_j_out, out=points_j_out)
            points_i_out = points_i_out.astype(points_i.dtype.type, copy=False)
            points_j_out = points_j_out.astype(points_j.dtype.type, copy=False)
            return points_i_out, points_j_out
        if isinstance(points_i, torch.Tensor):
            points_i_numpy, points_j_numpy = self.apply_points_trans(
                points_i.detach().cpu().numpy(),
                points_j.detach().cpu().numpy(),
            )
            return (
                torch.from_numpy(points_i_numpy).to(device=points_i.device),
                torch.from_numpy(points_j_numpy).to(device=points_j.device),
            )
        return self.apply_points_trans(np.array(points_i), np.array(points_j))

    def copy(self):
        """
        ** Returns a true copy of self. **
        """
        self_copy = self.__class__.__new__(self.__class__)
        self_copy.__setstate__(self.__getstate__())
        return self_copy

    def reverse(self, **kwargs):
        """
        ** Returns the bijection with caching. **

        Relies on the ``reverse`` method.
        Please note, do not return a copy.

        Returns
        -------
        Transform
            A new instance of the bijection of this transformation.
        """
        if self.reverse_instance is None:
            self.reverse_instance = self._reverse(**kwargs)
            self.reverse_instance.reverse_instance = self
        return self.reverse_instance

    def simplify(self):
        """
        ** Attempts to simplify the transformation. **

        The goal is to find a particular form and therefore simpler and faster to calculate.

        Returns
        -------
        Transformation
            A transformation equivalent to self, if possible simpler.
            If no simplification is found, directly returns self.
        """
        # the _simplify methode can modifiate in place.
        self_ = self.copy()
        if hasattr(self_, '_simplify'):
            return getattr(self_, '_simplify')()
        return self_

    @_mark
    def warp_image(self, image):
        """
        ** Passage of an image from space A to space B. **

        Parameters
        ----------
        image : np.ndarray
            The float32 image expressed in the A space.

        Returns
        -------
        dst_img : np.ndarray
            An interpolation of the image in the B space.
        """
        if _is_marked(self.warp_image_inv):
            i_field, j_field = Transform._get_identity_field(self.dst_shape or image.shape)
            i_field, j_field = self.reverse().apply_points_trans(i_field, j_field)
            return _remap(image, i_field, j_field)
        return self.reverse().warp_image_inv(image)

    @_mark
    def warp_image_inv(self, image):
        """
        ** Passage of an image from space B to space A. **

        Parameters
        ----------
        image : np.ndarray
            The float32 image expressed in the B space.

        Returns
        -------
        dst_img : np.ndarray
            An interpolation of the image in the A space.
        """
        if _is_marked(self.warp_image):
            i_field, j_field = Transform._get_identity_field(self.src_shape or image.shape)
            i_field, j_field = self.apply_points_trans(i_field, j_field)
            return _remap(image, i_field, j_field)
        return self.reverse().warp_image(image)

    @_mark
    def warp_points(self, points_i, points_j):
        """
        ** Exploits the other methods but does not add any info. **
        """
        if not _is_marked(self._reverse):
            inv = self.reverse()
            if not _is_marked(inv.warp_points_inv):
                return inv.warp_points_inv(points_i, points_j)

        raise NotImplementedError(
            "you need to implement 'warp_points' or 'reverse'+'warp_points_inv'"
        )

    @_mark
    def warp_points_inv(self, points_i, points_j):
        """
        ** Exploits the other methods but does not add any info. **
        """
        if not _is_marked(self._reverse):
            inv = self.reverse()
            if not _is_marked(inv.warp_points):
                return inv.warp_points(points_i, points_j)

        raise NotImplementedError(
            "you need to implement 'warp_points_inv' or 'reverse'+'warp_points'"
        )


class AbstractTransform(Transform):
    """
    ** A general abstract transformation for testing. **

    Examples
    --------
    >>> from deformation.core import AbstractTransform
    >>> AbstractTransform('foo')
    AbstractTransform('foo')
    >>>
    """

    def __init__(self, name, **kwargs):
        """
        Parameters
        ----------
        name : str
            The display name of the transformation.
        """
        assert isinstance(name, str), name.__class__.__name__
        self.name = name
        super().__init__(**kwargs)

    def __getstate__(self):
        return self.name, self.src_shape, self.dst_shape

    def __setstate__(self, state):
        name, src_shape, dst_shape = state
        AbstractTransform.__init__(self, name, src_shape=src_shape, dst_shape=dst_shape)

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.name)})'

    def _reverse(self):
        return InverseTransform(self)


class IdentityTransform(Transform):
    """
    ** A transformation that transforms nothing at all. **

    Examples
    --------
    >>> import numpy as np
    >>> import torch
    >>> from deformation.core import IdentityTransform
    >>> identity = IdentityTransform()
    >>> identity
    IdentityTransform()
    >>> img = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
    >>> identity(img)
    array([[0, 1, 2],
           [1, 2, 3],
           [2, 3, 4]])
    >>> img = np.array(img)
    >>> identity(img)
    array([[0, 1, 2],
           [1, 2, 3],
           [2, 3, 4]])
    >>> img = img.astype(np.float32)
    >>> identity(img)
    array([[0., 1., 2.],
           [1., 2., 3.],
           [2., 3., 4.]], dtype=float32)
    >>> img = img.astype(np.uint8)
    >>> identity(img)
    array([[0, 1, 2],
           [1, 2, 3],
           [2, 3, 4]], dtype=uint8)
    >>> img = torch.from_numpy(img)
    >>> identity(img)
    tensor([[0, 1, 2],
            [1, 2, 3],
            [2, 3, 4]], dtype=torch.uint8)
    >>> identity([1, 2, 3, 4, 5], [0, 1, 0, 1, 0])
    (array([1, 2, 3, 4, 5]), array([0, 1, 0, 1, 0]))
    >>>
    """

    def __init__(self, **kwargs):
        """
        ** Prevents improper operation. **
        """
        super().__init__(**kwargs)
        self.src_shape = self.src_shape or self.dst_shape
        self.dst_shape = self.dst_shape or self.src_shape
        assert self.src_shape == self.dst_shape, (self.src_shape, self.dst_shape)

    def __bool__(self):
        return False

    def __getstate__(self):
        return self.src_shape, self.dst_shape

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __setstate__(self, state):
        src_shape, dst_shape = state
        IdentityTransform.__init__(self, src_shape=src_shape, dst_shape=dst_shape)

    def reverse(self, **_):
        return self.copy()

    def warp_image(self, image):
        return image.copy()

    def warp_image_inv(self, image):
        return image.copy()

    def warp_points(self, points_i, points_j):
        return points_i.copy(), points_j.copy()

    def warp_points_inv(self, points_i, points_j):
        return points_i.copy(), points_j.copy()


class InverseTransform(Transform):
    """
    ** Reverses the starting and destination space. **

    Examples
    --------
    >>> from deformation.core import AbstractTransform, InverseTransform
    >>> InverseTransform(AbstractTransform('foo'))
    InverseTransform(AbstractTransform('foo'))
    >>> _.reverse()
    AbstractTransform('foo')
    >>>
    """

    def __init__(self, transform):
        """
        Parameters
        ----------
        transform : Transform
            The geometric transformation to invert.
        """
        assert isinstance(transform, Transform), transform.__class__.__name__

        self._trans = transform
        super().__init__()

    def __getstate__(self):
        return self._trans

    def __repr__(self):
        """
        ** Returns a nice presentation. **
        """
        return f'{self.__class__.__name__}({self._trans})'

    def __setstate__(self, state):
        InverseTransform.__init__(self, state)

    @property
    def dst_shape(self):
        """
        ** Simple parser. **
        """
        return self._trans.src_shape

    @dst_shape.setter
    def dst_shape(self, value):
        self._trans.src_shape = value

    @property
    def src_shape(self):
        """
        ** Simple parser. **
        """
        return self._trans.dst_shape

    @src_shape.setter
    def src_shape(self, value):
        self._trans.dst_shape = value

    def reverse(self, **_):
        return self._trans.copy()

    def warp_image(self, image):
        return self._trans.warp_image_inv(image)

    def warp_image_inv(self, image):
        return self._trans.warp_image(image)

    def warp_points(self, points_i, points_j):
        return self._trans.warp_points_inv(points_i, points_j)

    def warp_points_inv(self, points_i, points_j):
        return self._trans.warp_points(points_i, points_j)


class ChainTransform(Transform):
    """
    ** Allows you to accumulate transformations. **

    Examples
    --------
    >>> from deformation.core import AbstractTransform, ChainTransform
    >>> ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
    ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
    >>>
    """

    def __init__(self, *transformations):
        """
        Parameters
        ----------
        *transformations : tuple
            The differents transformation to concatenate.
        """
        assert len(transformations) >= 1, transformations
        assert all(isinstance(t, Transform) for t in transformations), transformations

        self.chain = list(transformations)
        super().__init__()

    def __getstate__(self):
        return self.chain

    def __repr__(self):
        """
        ** Returns a nice presentation. **
        """
        return f'{self.__class__.__name__}({", ".join(map(repr, self.chain))})'

    def __setstate__(self, state):
        """
        Examples
        --------
        >>> from deformation.core import AbstractTransform, ChainTransform
        >>> ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>> _.copy()
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>>
        """
        ChainTransform.__init__(self, *state)

    def _simplify(self):
        """
        Examples
        --------
        >>> from deformation.core import AbstractTransform, IdentityTransform, ChainTransform
        >>>
        >>> ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>> _.simplify() # do nothing
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>>
        >>> ChainTransform(AbstractTransform('a'))
        ChainTransform(AbstractTransform('a'))
        >>> _.simplify() # one element
        AbstractTransform('a')
        >>>
        >>> ChainTransform(IdentityTransform())
        ChainTransform(IdentityTransform())
        >>> _.simplify() # one identity element
        IdentityTransform()
        >>> ChainTransform(AbstractTransform('a'), IdentityTransform(), AbstractTransform('b'))
        ChainTransform(AbstractTransform('a'), IdentityTransform(), AbstractTransform('b'))
        >>> _.simplify() # remove identity
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>> ChainTransform(IdentityTransform(), AbstractTransform('a'), AbstractTransform('b'))
        ChainTransform(IdentityTransform(), AbstractTransform('a'), AbstractTransform('b'))
        >>> _.simplify() # remove identity
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>> ChainTransform(AbstractTransform('a'), AbstractTransform('b'), IdentityTransform())
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'), IdentityTransform())
        >>> _.simplify() # remove identity
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>>
        >>> ChainTransform(ChainTransform(AbstractTransform('a'), AbstractTransform('b')))
        ChainTransform(ChainTransform(AbstractTransform('a'), AbstractTransform('b')))
        >>> _.simplify() # recursive chaine
        ChainTransform(AbstractTransform('a'), AbstractTransform('b'))
        >>>
        """
        self.chain = [t.simplify() for t in self.chain]
        self.chain = [
            trans for chain in self.chain
            for trans in (chain.chain if isinstance(chain, ChainTransform) else (chain,))
        ]

        # simplify identity
        src_shape, dst_shape = self.src_shape, self.dst_shape
        self.chain = [t for t in self.chain if not isinstance(t, IdentityTransform)]
        if not self.chain:
            return IdentityTransform(src_shape=src_shape, dst_shape=dst_shape)
        self.src_shape, self.dst_shape = src_shape, dst_shape
        if len(self.chain) == 1:
            return self.chain[0]

        return self

    @property
    def dst_shape(self):
        """
        ** Simple parser. **
        """
        return self.chain[-1].dst_shape

    @dst_shape.setter
    def dst_shape(self, value):
        self.chain[-1].dst_shape = value

    @property
    def src_shape(self):
        """
        ** Simple parser. **
        """
        return self.chain[0].src_shape

    @src_shape.setter
    def src_shape(self, value):
        self.chain[-1].src_shape = value

    def warp_points(self, points_i, points_j):
        for trans in self.chain:
            points_i, points_j = trans.warp_points(points_i, points_j)
        return points_i, points_j

    def warp_points_inv(self, points_i, points_j):
        for trans in self.chain[::-1]:
            points_i, points_j = trans.warp_points_inv(points_i, points_j)
        return points_i, points_j
