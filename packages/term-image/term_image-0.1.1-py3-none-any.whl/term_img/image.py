"""
Core Library Definitions
========================
"""

__all__ = ("TermImage",)

import io
import os
import re
import time
from itertools import cycle
from math import ceil
from operator import add, gt, mul, sub, truediv
from random import randint
from shutil import get_terminal_size
from types import FunctionType
from typing import Any, Optional, Tuple, Union
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError

from .exceptions import InvalidSize, TermImageException, URLNotFoundError

_ALPHA_THRESHOLD = 40 / 255  # Default alpha threshold
_FG_FMT = "\033[38;2;%d;%d;%dm"
_BG_FMT = "\033[48;2;%d;%d;%dm"
_RESET = "\033[0m"
_UPPER_PIXEL = "\u2580"  # upper-half block element
_LOWER_PIXEL = "\u2584"  # lower-half block element
_FORMAT_SPEC = re.compile(
    r"(([<|>])?(\d+)?)?(\.([-^_])?(\d+)?)?(#(\.\d+|[0-9a-f]{6})?)?",
    re.ASCII,
)
_NO_VERTICAL_SPEC = re.compile(r"(([<|>])?(\d+)?)?\.(#(\.\d+|[0-9a-f]{6})?)?", re.ASCII)
_HEX_COLOR_FORMAT = re.compile("#[0-9a-f]{6}", re.ASCII)


class TermImage:
    """Text-printable image

    Args:
        image: Image to be rendered.
        width: The width to render the image with.
        height: The height to render the image with.
        scale: The image render scale on respective axes.

    Raises:
        TypeError: An argument is of an inappropriate type.
        ValueError: An argument has an unexpected/invalid value.

    Propagates exceptions raised by :py:meth:`set_size()`, if *width* or *height* is
    given.

    NOTE:
        * *width* is not neccesarily the exact number of columns that'll be used
          to render the image. That is influenced by the currently set
          :term:`font ratio`.
        * *height* is **2 times** the number of lines that'll be used in the terminal.
        * If neither is given or both are ``None``, the size is automatically determined
          when the image is to be :term:`rendered`, such that it can fit
          within the terminal.
        * The :term:`size <render size>` is multiplied by the :term:`scale` on each axis
          respectively before the image is :term:`rendered`.
    """

    # Special Methods

    def __init__(
        self,
        image: Image.Image,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: Tuple[float, float] = (1.0, 1.0),
    ):
        """See class description"""
        if not isinstance(image, Image.Image):
            raise TypeError(
                "Expected a 'PIL.Image.Image' instance for 'image' "
                f"(got: {type(image).__name__!r})."
            )

        self._closed = False
        self._source = image
        self._buffer = io.StringIO()
        self._original_size = image.size
        if width is None is height:
            self._size = None
        else:
            self.set_size(width, height)
        self._scale = []
        self._scale[:] = self._check_scale(scale)

        self._is_animated = hasattr(image, "is_animated") and image.is_animated
        if self._is_animated:
            self._frame_duration = 0.1
            self._seek_position = 0
            self._n_frames = image.n_frames

        # Recognized advanced sizing options.
        # These are initialized here only to avoid `AttributeError`s in case `_size` is
        # initially set via a means other than `set_size()`.
        self._check_height = True
        self._h_allow = 0
        self._v_allow = 2  # A 2-line allowance for the shell prompt, etc

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.close()
        return False  # Currently, no particular exception is suppressed

    def __format__(self, spec):
        """Renders the image with alignment, padding and transparency control"""
        # Only the currently set frame is rendered for animated images
        match_ = _FORMAT_SPEC.fullmatch(spec)
        if not match_ or _NO_VERTICAL_SPEC.fullmatch(spec):
            raise ValueError("Invalid format specifier")

        _, h_align, width, _, v_align, height, alpha, threshold_or_bg = match_.groups()

        width = width and int(width)
        height = height and int(height)

        return self._renderer(
            lambda image: self._format_render(
                self._render_image(
                    image,
                    (
                        threshold_or_bg
                        and (
                            "#" + threshold_or_bg
                            if _HEX_COLOR_FORMAT.fullmatch("#" + threshold_or_bg)
                            else float(threshold_or_bg)
                        )
                        if alpha
                        else _ALPHA_THRESHOLD
                    ),
                ),
                *self._check_formatting(h_align, width, v_align, height),
            )
        )

    def __repr__(self):
        return (
            "<{}(source={!r}, original_size={}, size={}, scale={}, is_animated={})>"
        ).format(
            type(self).__name__,
            (self._url if hasattr(self, "_url") else self._source),
            self._original_size,
            self._size,
            self.scale,  # Stored as a list but should be shown as a tuple
            self._is_animated,
        )

    def __str__(self):
        """Renders the image with transparency enabled and without alignment"""
        # Only the currently set frame is rendered for animated images
        return self._renderer(lambda image: self._render_image(image, _ALPHA_THRESHOLD))

    # Properties

    closed = property(
        lambda self: self._closed,
        doc="Instance finalization status",
    )

    frame_duration = property(
        lambda self: self._frame_duration if self._is_animated else None,
        doc="""Duration (in seconds) of a single frame for :term:`animated` images

        Setting this on non-animated images is simply ignored, no exception is raised.
        """,
    )

    @frame_duration.setter
    def frame_duration(self, value: float) -> None:
        if not isinstance(value, float):
            raise TypeError(f"Invalid duration type (got: {type(value).__name__})")
        if value <= 0.0:
            raise ValueError(
                f"Invalid frame duration (got: {value}, n_frames={self._n_frames})"
            )
        if self._is_animated:
            self._frame_duration = value

    height = property(
        lambda self: self._size and self._size[1],
        lambda self, height: self.set_size(height=height),
        doc="""
        Image :term:`render height`

        ``None`` when :py:attr:`render size <size>` is :ref:`unset <unset-size>`.

        Settable values:

            * ``None``: Sets the render size to the automatically calculated one.
            * A positive ``int``: Sets the render height to the given value and
              the width proprtionally.

        The image is actually :term:`rendered` using half this number of lines
        """,
    )

    is_animated = property(
        lambda self: self._is_animated,
        doc="``True`` if the image is :term:`animated`. Otherwise, ``False``.",
    )

    original_size = property(
        lambda self: self._original_size, doc="Original image size"
    )

    n_frames = property(
        lambda self: self._n_frames if self._is_animated else 1,
        doc="The number of frames in the image",
    )

    rendered_height = property(
        lambda self: ceil(
            round((self._size or self._valid_size(None, None))[1] * self._scale[1]) / 2
        ),
        doc="The number of lines that the drawn image will occupy in a terminal",
    )

    @property
    def rendered_size(self) -> Tuple[int, int]:
        """The number of columns and lines (respectively) that the drawn image will
        occupy in a terminal
        """
        columns, rows = map(
            round,
            map(
                mul,
                map(
                    add,
                    map(
                        truediv,
                        self._size or self._valid_size(None, None),
                        (_pixel_ratio, 1),
                    ),
                    (self._width_compensation, 0.0),
                ),
                self._scale,
            ),
        )
        return (columns, ceil(rows / 2))

    rendered_width = property(
        lambda self: round(
            (
                (self._size or self._valid_size(None, None))[0] / _pixel_ratio
                + self._width_compensation
            )
            * self._scale[0]
        ),
        doc="The number of columns that the drawn image will occupy in a terminal",
    )

    scale = property(
        lambda self: tuple(self._scale),
        doc="""
        Image :term:`render scale`

        Settable values are:

            * A *scale value*; sets both axes.
            * A ``tuple`` of two *scale values*; sets ``(x, y)`` respectively.

        A scale value is a ``float`` in the range **0.0 < value <= 1.0**.
        """,
    )

    @scale.setter
    def scale(self, scale: Union[float, Tuple[float, float]]) -> None:
        if isinstance(scale, float):
            if not 0.0 < scale <= 1.0:
                raise ValueError(f"Scale value out of range (got: {scale})")
            self._scale[:] = (scale,) * 2
        elif isinstance(scale, tuple):
            self._scale[:] = self._check_scale(scale)
        else:
            raise TypeError("Given value must be a float or a tuple of floats")

    scale_x = property(
        lambda self: self._scale[0],
        doc="""
        x-axis :term:`render scale`

        A scale value is a ``float`` in the range **0.0 < x <= 1.0**.
        """,
    )

    @scale_x.setter
    def scale_x(self, x: float) -> None:
        self._scale[0] = self._check_scale_2(x)

    scale_y = property(
        lambda self: self._scale[1],
        doc="""
        y-ayis :term:`render scale`

        A scale value is a ``float`` in the range **0.0 < y <= 1.0**.
        """,
    )

    @scale_y.setter
    def scale_y(self, y: float) -> None:
        self._scale[1] = self._check_scale_2(y)

    size = property(
        lambda self: self._size,
        doc="""Image :term:`render size`

        ``None`` when render size is unset.

        Setting this to ``None`` :ref:`unsets <unset-size>` the *render size* (so that
        it's automatically calculated whenever the image is :term:`rendered`) and
        resets the recognized advanced sizing options to their defaults.
        """,
    )

    @size.setter
    def size(self, value: None) -> None:
        if value is not None:
            raise TypeError("The only acceptable value is `None`")
        self._size = value
        self._check_height = True
        self._h_allow = 0
        self._v_allow = 2  # A 2-line allowance for the shell prompt, etc

    source = property(
        lambda self: (self._url if hasattr(self, "_url") else self._source),
        doc="""
        The :term:`source` from which the instance was initialized

        Can be a PIL image, file path or URL.
        """,
    )

    width = property(
        lambda self: self._size and self._size[0],
        lambda self, width: self.set_size(width),
        doc="""
        Image :term:`render width`

        ``None`` when :py:attr:`render size <size>` is :ref:`unset <unset-size>`.

        Settable values:

            * ``None``: Sets the render size to the automatically calculated one.
            * A positive ``int``: Sets the render width to the given value and
              the height proportionally.
        """,
    )

    # Public Methods

    def close(self) -> None:
        """Finalizes the instance and releases external resources.

        NOTE:
            * It's not neccesary to explicity call this method, as it's automatically
              called when neccesary.
            * This method can be safely called mutiple times.
            * If the instance was initialized with a PIL image, the PIL image is never
              finalized.
        """
        try:
            if not self._closed:
                self._buffer.close()
                self._buffer = None

                if (
                    hasattr(self, "_url")
                    and os.path.exists(self._source)
                    # The file might not exist for whatever reason.
                ):
                    os.remove(self._source)
        except AttributeError:
            # Instance creation or initialization was unsuccessful
            pass
        finally:
            self._closed = True

    def draw(
        self,
        h_align: Optional[str] = None,
        pad_width: Optional[int] = None,
        v_align: Optional[str] = None,
        pad_height: Optional[int] = None,
        alpha: Optional[float] = _ALPHA_THRESHOLD,
        *,
        animate: bool = True,
        ignore_oversize: bool = False,
    ) -> None:
        """Draws/Displays an image in the terminal, with optional :term:`alignment` and
        :term:`padding`.

        Args:
            h_align: Horizontal alignment ("left"/"<", "center"/"|" or "right"/">").
              Default: center.
            pad_width: Number of columns within which to align the image.

              * Excess columns are filled with spaces.
              * default: terminal width.

            v_align: Vertical alignment ("top"/"^", "middle"/"-" or "bottom"/"_").
              Default: middle.
            pad_height: Number of lines within which to align the image.

              * Excess lines are filled with spaces.
              * default: terminal height, with a 2-line allowance.

            alpha: Transparency setting.

              * If ``None``, transparency is disabled (i.e black background).
              * If a ``float`` (**0.0 <= x < 1.0**), specifies the alpha ratio
                **above** which pixels are taken as *opaque*.
              * If a string, specifies a **hex color** with which transparent background
                should be replaced.

            animate: If ``False``, disable animation i.e draw only the current frame of
              an :term:`animated` image.
            ignore_oversize: If ``True``, do not verify if the image will fit into
              the :term:`available terminal size <available size>` with it's currently
              set :term:`render size`.

        Raises:
            TypeError: An argument is of an inappropriate type.
            ValueError: An argument has an unexpected/invalid value.
            ValueError: :term:`Render size` or :term:`scale` too small.
            term_img.exceptions.InvalidSize: The terminal has been resized in such a
              way that the previously set size can no longer fit into it.
            term_img.exceptions.InvalidSize: The image is :term:`animated` and the
              previously set size won't fit into the :term:`available terminal size
              <available size>`.

        NOTE:
            * Animations, if not disabled, are infinitely looped but can be terminated
              with ``Ctrl-C`` (``SIGINT`` or "KeyboardInterrupt").
            * If :py:meth:`set_size()` was previously used to set the
              :term:`render size` (directly or not), the last values of its
              *check_height*, *h_allow* and *v_allow* parameters are taken into
              consideration, with *check_height* applying to only non-animated images.
            * For animated images, when *animate* is ``True``:

              * :term:`Render size` and :term:`padding height` are always validated.
              * *ignore_oversize* has no effect.
        """
        h_align, pad_width, v_align, pad_height = self._check_formatting(
            h_align, pad_width, v_align, pad_height
        )

        if (
            animate
            and self._is_animated
            and None is not pad_height > get_terminal_size()[1]
        ):
            raise ValueError(
                "Padding height can not be greater than the terminal height for "
                "animated images"
            )

        if alpha is not None:
            if isinstance(alpha, float):
                if not 0.0 <= alpha < 1.0:
                    raise ValueError(f"Alpha threshold out of range (got: {alpha})")
            elif isinstance(alpha, str):
                if not _HEX_COLOR_FORMAT.fullmatch(alpha):
                    raise ValueError(f"Invalid hex color string (got: {alpha})")
            else:
                raise TypeError(
                    "'alpha' must be `None` or of type `float` or `str` "
                    f"(got: {type(alpha).__name__})"
                )
        if not isinstance(animate, bool):
            raise TypeError("'animate' must be a boolean")
        if not isinstance(ignore_oversize, bool):
            raise TypeError("'ignore_oversize' must be a boolean")

        def render(image) -> None:
            try:
                if animate and self._is_animated:
                    self._display_animated(
                        image, alpha, h_align, pad_width, v_align, pad_height
                    )
                else:
                    print(
                        self._format_render(
                            self._render_image(image, alpha),
                            h_align,
                            pad_width,
                            v_align,
                            pad_height,
                        ),
                        end="",
                        flush=True,
                    )
            finally:
                print("\033[0m")  # Always reset color

        self._renderer(
            render, check_size=animate and self._is_animated or not ignore_oversize
        )

    @classmethod
    def from_file(
        cls,
        filepath: str,
        **kwargs: Union[Optional[int], Tuple[float, float]],
    ) -> "TermImage":
        """Creates a :py:class:`TermImage` instance from an image file.

        Args:
            filepath: Relative/Absolute path to an image file.
            kwargs: Same keyword arguments as the class constructor.

        Returns:
            A new :py:class:`TermImage` instance.

        Raises:
            TypeError: *filepath* is not a string.
            FileNotFoundError: The given path does not exist.
            IsADirectoryError: Propagated from from ``PIL.Image.open()``.
            UnidentifiedImageError: Propagated from from ``PIL.Image.open()``.

        Also Propagates exceptions raised or propagated by the class constructor.
        """
        if not isinstance(filepath, str):
            raise TypeError(
                f"File path must be a string (got: {type(filepath).__name__!r})."
            )

        # Intentionally propagates `IsADirectoryError` since the message is OK
        try:
            Image.open(filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"No such file: {filepath!r}") from None
        except UnidentifiedImageError as e:
            e.args = (f"Could not identify {filepath!r} as an image",)
            raise

        new = cls(Image.open(filepath), **kwargs)
        new._source = os.path.realpath(filepath)
        return new

    @classmethod
    def from_url(
        cls,
        url: str,
        **kwargs: Union[Optional[int], Tuple[float, float]],
    ) -> "TermImage":
        """Creates a :py:class:`TermImage` instance from an image URL.

        Args:
            url: URL of an image file.
            kwargs: Same keyword arguments as the class constructor.

        Returns:
            A new :py:class:`TermImage` instance.

        Raises:
            TypeError: *url* is not a string.
            ValueError: The URL is invalid.
            term_img.exceptions.URLNotFoundError: The URL does not exist.
            PIL.UnidentifiedImageError: Propagated from ``PIL.Image.open()``.

        Also propagates connection-related exceptions from ``requests.get()``
        and exceptions raised or propagated by the class constructor.

        NOTE:
            This method creates a temporary image file, but only after a successful
            initialization.

            Proper clean-up is guaranteed except maybe in very rare cases.

            To ensure 100% guarantee of clean-up, use the object as a
            :ref:`context manager <context-manager>`.
        """
        if not isinstance(url, str):
            raise TypeError(f"URL must be a string (got: {type(url).__name__!r}).")
        if not all(urlparse(url)[:3]):
            raise ValueError(f"Invalid URL: {url!r}")

        # Propagates connection-related errors.
        response = requests.get(url, stream=True)
        if response.status_code == 404:
            raise URLNotFoundError(f"URL {url!r} does not exist.")

        try:
            new = cls(Image.open(io.BytesIO(response.content)), **kwargs)
        except UnidentifiedImageError as e:
            e.args = (f"The URL {url!r} doesn't link to an identifiable image",)
            raise

        # Ensure initialization is successful before writing to file

        basedir = os.path.join(os.path.expanduser("~"), ".term_img", "temp")
        if not os.path.isdir(basedir):
            os.makedirs(basedir)

        filepath = os.path.join(basedir, os.path.basename(urlparse(url).path))
        while os.path.exists(filepath):
            filepath += str(randint(0, 9))
        with open(filepath, "wb") as image_writer:
            image_writer.write(response.content)

        new._source = filepath
        new._url = url
        return new

    def seek(self, pos: int) -> None:
        """Changes current image frame.

        Args:
            pos: New frame number.

        Raises:
            TypeError: An argument is of an inappropriate type.
            ValueError: An argument has an unexpected/invalid value but of an
              appropriate type.

        Frame numbers start from 0 (zero).
        """
        if not isinstance(pos, int):
            raise TypeError(f"Invalid seek position type (got: {type(pos).__name__})")
        if not 0 <= pos < self._n_frames if self._is_animated else pos:
            raise ValueError(
                f"Invalid frame number (got: {pos}, n_frames={self.n_frames})"
            )
        if self._is_animated:
            self._seek_position = pos

    def set_size(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        h_allow: int = 0,
        v_allow: int = 2,
        *,
        maxsize: Optional[Tuple[int, int]] = None,
        check_width: bool = True,
        check_height: bool = True,
    ) -> None:
        """Sets the :term:`render size` with advanced control.

        Args:
            width: :term:`Render width` to use.
            height: :term:`Render height` to use.
            h_allow: Horizontal allowance i.e minimum number of columns to leave unused.
            v_allow: Vertical allowance i.e minimum number of lines to leave unused.
            maxsize: If given ``(cols, lines)``, it's used instead of the terminal size.
            check_width: If ``False``, the validity of the resulting
              :term:`rendered width` is not checked.
            check_height: If ``False``, the validity of the resulting
              :term:`rendered height` is not checked.

        Raises:
            TypeError: An argument is of an inappropriate type.
            ValueError: An argument has an unexpected/invalid value but of an
              appropriate type.
            ValueError: Both *width* and *height* are specified.
            ValueError: The :term:`available size` is too small.
            term_img.exceptions.InvalidSize: The resulting :term:`render size` is too
              small.
            term_img.exceptions.InvalidSize: The resulting :term:`rendered size` will
              not fit into the :term:`available terminal size <available size>`
              (or *maxsize*, if given).

        If neither *width* nor *height* is given or anyone given is ``None``:

          * and *check_height* and *check_width* are both ``True``, the size is
            automatically calculated to fit within the *available* terminal size
            (or *maxsize*, if given).
          * and *check_height* is ``False``, the size is set such that the
            :term:`rendered width` is exactly the *available* terminal width
            or ``maxsize[0]`` (assuming the :term:`render scale` equals 1),
            regardless of the :term:`font ratio`.
          * and *check_width* is ``False`` (and *check_height* is ``True``), the size is
            set such that the :term:`rendered height` is exactly the *available*
            terminal height or ``maxsize[1]`` (assuming the :term:`render scale`
            equals 1), regardless of the :term:`font ratio`.

        :term:`Allowance` does not apply when *maxsize* is given.

        | No :term:`vertical allowance` when *check_height* is ``False``.
        | No :term:`horizontal allowance` when *check_width* is ``False``.

        The *check_height* might be set to ``False`` to set the *render size* for
        vertically-oriented images (i.e images with height > width) such that the
        drawn image spans more columns but the terminal window has to be scrolled
        to view the entire image.

        All image rendering and formatting methods recognize and respect the
        *check_height*, *h_allow* and *v_allow* options, until the size is re-set
        or :ref:`unset <unset-size>`.

        *check_width* is only provided for completeness, it should probably be used only
        when the image will not be drawn to the current terminal.
        The value of this parameter is **not** recognized by any other method or
        operation.
        """
        if width is not None is not height:
            raise ValueError("Cannot specify both width and height")
        for argname, x in zip(("width", "height"), (width, height)):
            if not (x is None or isinstance(x, int)):
                raise TypeError(
                    f"{argname!r} must be `None` or an integer "
                    f"(got: type {type(x).__name__!r})"
                )
            if None is not x <= 0:
                raise ValueError(f"{argname!r} must be positive (got: {x})")
        for argname, x in zip(("h_allow", "v_allow"), (h_allow, v_allow)):
            if not isinstance(x, int):
                raise TypeError(
                    f"{argname!r} must be an integer (got: type {type(x).__name__!r})"
                )
            if x < 0:
                raise ValueError(f"{argname!r} must be non-negative (got: {x})")
        if maxsize is not None:
            if not (
                isinstance(maxsize, tuple) and all(isinstance(x, int) for x in maxsize)
            ):
                raise TypeError(
                    f"'maxsize' must be a tuple of integers (got: {maxsize!r})"
                )

            if not (len(maxsize) == 2 and all(x > 0 for x in maxsize)):
                raise ValueError(
                    f"'maxsize' must contain two positive integers (got: {maxsize})"
                )
        if not (isinstance(check_width, bool) and isinstance(check_height, bool)):
            raise TypeError("The size-check arguments must be booleans")

        self._size = self._valid_size(
            width,
            height,
            h_allow * check_width,
            v_allow * check_height,
            maxsize=maxsize,
            check_height=check_height,
            check_width=check_width,
            ignore_oversize=not (check_width or check_height),
        )
        self._check_height = check_height
        self._h_allow = h_allow * (not maxsize) * check_width
        self._v_allow = v_allow * (not maxsize) * check_height

    def tell(self) -> int:
        """Returns the current image frame number."""
        return self._seek_position if self._is_animated else 0

    # Private Methods

    def _check_formatting(
        self,
        h_align: Optional[str] = None,
        width: Optional[int] = None,
        v_align: Optional[str] = None,
        height: Optional[int] = None,
    ) -> Tuple[Union[None, str, int]]:
        """Validates formatting arguments while also translating literal ones.

        Returns:
            The respective arguments appropriate for ``_format_render()``.
        """
        if not isinstance(h_align, (type(None), str)):
            raise TypeError("'h_align' must be a string.")
        if None is not h_align not in set("<|>"):
            align = {"left": "<", "center": "|", "right": ">"}.get(h_align)
            if not align:
                raise ValueError(f"Invalid horizontal alignment option: {h_align!r}")
            h_align = align

        if not isinstance(width, (type(None), int)):
            raise TypeError("Padding width must be `None` or an integer.")
        if width is not None:
            if width <= 0:
                raise ValueError(f"Padding width must be positive (got: {width})")
            if width > get_terminal_size()[0] - self._h_allow:
                raise ValueError(
                    "Padding width is larger than the available terminal width"
                )

        if not isinstance(v_align, (type(None), str)):
            raise TypeError("'v_align' must be a string.")
        if None is not v_align not in set("^-_"):
            align = {"top": "^", "middle": "-", "bottom": "_"}.get(v_align)
            if not align:
                raise ValueError(f"Invalid vertical alignment option: {v_align!r}")
            v_align = align

        if not isinstance(height, (type(None), int)):
            raise TypeError("Padding height must be `None` or an integer.")
        if None is not height <= 0:
            raise ValueError(f"Padding height must be positive (got: {height})")

        return h_align, width, v_align, height

    @staticmethod
    def _check_scale(scale: Tuple[float, float]) -> Tuple[float, float]:
        """Checks a tuple of scale values.

        Returns:
            The tuple of scale values, if valid.

        Raises:
            TypeError: The object is not a tuple of ``float``\\ s.
            ValueError: The object is not a 2-tuple or the values are out of range.
        """
        if not (isinstance(scale, tuple) and all(isinstance(x, float) for x in scale)):
            raise TypeError(f"'scale' must be a tuple of floats (got: {scale!r})")

        if not (len(scale) == 2 and all(0.0 < x <= 1.0 for x in scale)):
            raise ValueError(
                f"'scale' must be a tuple of two floats, 0.0 < x <= 1.0 (got: {scale})"
            )
        return scale

    @staticmethod
    def _check_scale_2(value: float) -> float:
        """Checks a single scale value.

        Returns:
            The scale value, if valid.

        Raises:
            TypeError: The object is not a ``float``.
            ValueError: The value is out of range.
        """
        if not isinstance(value, float):
            raise TypeError(
                f"Given value must be a float (got: type {type(value).__name__!r})"
            )
        if not 0.0 < value <= 1.0:
            raise ValueError(f"Scale value out of range (got: {value})")
        return value

    def _display_animated(
        self, image: Image.Image, alpha: Optional[float], *fmt: Union[None, str, int]
    ) -> None:
        """Displays an animated GIF image in the terminal.

        This is done infinitely but can be terminated with ``Ctrl-C``.
        """
        lines = max(
            (fmt or (None,))[-1] or get_terminal_size()[1] - self._v_allow,
            self.rendered_height,
        )
        cache = [None] * self._n_frames
        prev_seek_pos = self._seek_position
        try:
            # By implication, the first frame is repeated once at the start :D
            self.seek(0)
            cache[0] = frame = self._format_render(
                self._render_image(image, alpha), *fmt
            )
            duration = self._frame_duration
            for n in cycle(range(self._n_frames)):
                print(frame, end="", flush=True)  # Current frame

                # Render next frame during current frame's duration
                start = time.time()
                self._buffer.truncate()  # Clear buffer
                self.seek(n)
                if cache[n]:
                    frame = cache[n]
                else:
                    cache[n] = frame = self._format_render(
                        self._render_image(image, alpha),
                        *fmt,
                    )
                # Move cursor up to the begining of the first line of the image
                # Not flushed until the next frame is printed
                print("\r\033[%dA" % (lines - 1), end="")

                # Left-over of current frame's duration
                time.sleep(max(0, duration - (time.time() - start)))
        finally:
            self.seek(prev_seek_pos)
            # Move the cursor to the line after the image
            # Prevents "overlayed" output in the terminal
            print("\033[%dB" % lines, end="", flush=True)

    def _format_render(
        self,
        render: str,
        h_align: Optional[str] = None,
        width: Optional[int] = None,
        v_align: Optional[str] = None,
        height: Optional[int] = None,
    ) -> str:
        """Formats rendered image text.

        All arguments should be passed through ``_check_formatting()`` first.
        """
        lines = render.splitlines()
        cols, rows = self.rendered_size

        width = width or get_terminal_size()[0] - self._h_allow
        width = max(cols, width)
        if h_align == "<":  # left
            pad_left = ""
            pad_right = " " * (width - cols)
        elif h_align == ">":  # right
            pad_left = " " * (width - cols)
            pad_right = ""
        else:  # center
            pad_left = " " * ((width - cols) // 2)
            pad_right = " " * (width - cols - len(pad_left))

        if pad_left and pad_right:
            lines = [pad_left + line + pad_right for line in lines]
        elif pad_left:
            lines = [pad_left + line for line in lines]
        elif pad_right:
            lines = [line + pad_right for line in lines]

        height = height or get_terminal_size()[1] - self._v_allow
        height = max(rows, height)
        if v_align == "^":  # top
            pad_up = 0
            pad_down = height - rows
        elif v_align == "_":  # bottom
            pad_up = height - rows
            pad_down = 0
        else:  # middle
            pad_up = (height - rows) // 2
            pad_down = height - rows - pad_up

        if pad_down:
            lines[rows:] = (" " * width,) * pad_down
        if pad_up:
            lines[:0] = (" " * width,) * pad_up

        return "\n".join(lines)

    def _render_image(self, image: Image.Image, alpha: Optional[float]) -> str:
        """Converts image pixel data into a "color-coded" string.

        Two pixels per character using FG and BG colors.

        NOTE: This method is not meant to be used directly, use it via `_renderer()`
        instead.
        """
        if self._closed:
            raise TermImageException("This image has been finalized")

        # NOTE:
        # It's more efficient to write separate strings to the buffer separately
        # than concatenate and write together.

        # Eliminate attribute resolution cost
        buffer = self._buffer
        buf_write = buffer.write

        def update_buffer():
            if alpha:
                no_alpha = False
                if a_cluster1 == 0 == a_cluster2:
                    buf_write(_RESET)
                    buf_write(" " * n)
                elif a_cluster1 == 0:  # up is transparent
                    buf_write(_RESET)
                    buf_write(_FG_FMT % cluster2)
                    buf_write(_LOWER_PIXEL * n)
                elif a_cluster2 == 0:  # down is transparent
                    buf_write(_RESET)
                    buf_write(_FG_FMT % cluster1)
                    buf_write(_UPPER_PIXEL * n)
                else:
                    no_alpha = True

            if not alpha or no_alpha:
                buf_write(_BG_FMT % cluster2)
                if cluster1 == cluster2:
                    buf_write(" " * n)
                else:
                    buf_write(_FG_FMT % cluster1)
                    buf_write(_UPPER_PIXEL * n)

        if self._is_animated:
            image.seek(self._seek_position)

        width, height = map(
            round,
            map(
                mul,
                self._scale,
                map(
                    add,
                    map(truediv, self._size, (_pixel_ratio, 1)),
                    (self._width_compensation, 0.0),
                ),
            ),
        )

        if alpha is None or image.mode == "RGB":
            try:
                image = image.convert("RGB").resize((width, height))
            except ValueError:
                raise ValueError("Render size or scale too small") from None
            rgb = tuple(image.getdata())
            a = (255,) * (width * height)
            alpha = None
        else:
            try:
                image = image.convert("RGBA").resize((width, height))
            except ValueError:
                raise ValueError("Render size or scale too small") from None
            if isinstance(alpha, str):
                bg = Image.new("RGBA", image.size, alpha)
                bg.alpha_composite(image)
                if image is not self._source:
                    image.close()
                image = bg
                alpha = None
            rgb = tuple(image.convert("RGB").getdata())
            if alpha is None:
                a = (255,) * (width * height)
            else:
                alpha = round(alpha * 255)
                a = [0 if val < alpha else val for val in image.getdata(3)]
                # To distinguish `0.0` from `None` in truth value tests
                if alpha == 0.0:
                    alpha = True

        # clean up
        if image is not self._source:
            image.close()

        if height % 2:
            mark = width * (height // 2) * 2  # Starting index of the last row
            rgb, last_rgb = rgb[:mark], rgb[mark:]
            a, last_a = a[:mark], a[mark:]

        rgb_pairs = (
            (
                zip(rgb[x : x + width], rgb[x + width : x + width * 2]),
                (rgb[x], rgb[x + width]),
            )
            for x in range(0, len(rgb), width * 2)
        )
        a_pairs = (
            (
                zip(a[x : x + width], a[x + width : x + width * 2]),
                (a[x], a[x + width]),
            )
            for x in range(0, len(a), width * 2)
        )

        row_no = 0
        # Two rows of pixels per line
        for (rgb_pair, (cluster1, cluster2)), (a_pair, (a_cluster1, a_cluster2)) in zip(
            rgb_pairs, a_pairs
        ):
            row_no += 2
            n = 0
            for (px1, px2), (a1, a2) in zip(rgb_pair, a_pair):
                # Color-code characters and write to buffer
                # when upper and/or lower pixel color/alpha-level changes
                if not (alpha and a1 == a_cluster1 == 0 == a_cluster2 == a2) and (
                    px1 != cluster1
                    or px2 != cluster2
                    or alpha
                    and (
                        # From non-transparent to transparent
                        a_cluster1 != a1 == 0
                        or a_cluster2 != a2 == 0
                        # From transparent to non-transparent
                        or 0 == a_cluster1 != a1
                        or 0 == a_cluster2 != a2
                    )
                ):
                    update_buffer()
                    cluster1 = px1
                    cluster2 = px2
                    if alpha:
                        a_cluster1 = a1
                        a_cluster2 = a2
                    n = 0
                n += 1
            # Rest of the line
            update_buffer()
            if row_no < height:  # last line not yet rendered
                buf_write("\033[0m\n")

        if height % 2:
            cluster1 = last_rgb[0]
            a_cluster1 = last_a[0]
            n = 0
            for px1, a1 in zip(last_rgb, last_a):
                if px1 != cluster1 or (
                    alpha and a_cluster1 != a1 == 0 or 0 == a_cluster1 != a1
                ):
                    if alpha and a_cluster1 == 0:
                        buf_write(_RESET)
                        buf_write(" " * n)
                    else:
                        buf_write(_FG_FMT % cluster1)
                        buf_write(_UPPER_PIXEL * n)
                    cluster1 = px1
                    if alpha:
                        a_cluster1 = a1
                    n = 0
                n += 1
            # Last cluster
            if alpha and a_cluster1 == 0:
                buf_write(_RESET)
                buf_write(" " * n)
            else:
                buf_write(_FG_FMT % cluster1)
                buf_write(_UPPER_PIXEL * n)

        buf_write(_RESET)  # Reset color after last line
        buffer.seek(0)  # Reset buffer pointer

        return buffer.getvalue()

    def _renderer(
        self, renderer: FunctionType, *args: Any, check_size: bool = False, **kwargs
    ) -> Any:
        """Performs common render preparations and a rendering operation.

        Args:
            renderer: The function to perform the specifc rendering operation for the
              caller of this method (``_renderer()``).
              This function must accept at least one positional argument, the
              ``PIL.Image.Image`` instance corresponding to the source.
            args: Positional arguments to pass on to *renderer*, after the
              ``PIL.Image.Image`` instance.
            check_size: Determines whether or not the image's set size (if any) is
              checked to see if it still fits into the *avaliable* terminal size.
            kwargs: Keyword arguments to pass on to *renderer*.

        Returns:
            The return value of *renderer*.

        Raises:
            ValueError: Render size or scale too small.

        NOTE:
            * If the ``set_size()`` method was previously used to set the *render size*,
              (directly or not), the last value of its *check_height* parameter
              is taken into consideration, for non-animated images.
        """
        if self._closed:
            raise TermImageException("This image has been finalized")

        try:
            reset_size = False
            if not self._size:  # Size is unset
                self.set_size()
                reset_size = True

            # If the set size is larger than the available terminal size but the scale
            # makes it fit in, then it's all good.
            elif check_size:
                columns, lines = map(
                    sub,
                    get_terminal_size(),
                    (self._h_allow, self._v_allow),
                )

                if any(
                    map(
                        gt,
                        # the compared height will be 0 when `_check_height` is `False`
                        # and the terminal height should never be < 0
                        map(mul, self.rendered_size, (1, self._check_height)),
                        (columns, lines),
                    )
                ):
                    raise InvalidSize(
                        "Seems the terminal has been resized or font ratio has been "
                        "changed since the image render size was set and the image "
                        "can no longer fit into the available terminal size"
                    )

                # Reaching here means it's either valid or `_check_height` is `False`.
                # Hence, there's no need to check `_check_height`.
                if self._is_animated and self.rendered_height > lines:
                    raise InvalidSize(
                        "The image height cannot be greater than the terminal height "
                        "for animated images"
                    )

            image = (
                Image.open(self._source)
                if isinstance(self._source, str)
                else self._source
            )

            return renderer(image, *args, **kwargs)

        finally:
            self._buffer.seek(0)  # Reset buffer pointer
            self._buffer.truncate()  # Clear buffer
            if reset_size:
                self._size = None

    def _valid_size(
        self,
        width: Optional[int],
        height: Optional[int],
        h_allow: int = 0,
        v_allow: int = 2,
        *,
        maxsize: Optional[Tuple[int, int]] = None,
        check_height: bool = True,
        check_width: bool = True,
        ignore_oversize: bool = False,
    ) -> Tuple[int, int]:
        """Generates a *render size* tuple and checks if the resulting *rendered size*
        is valid.

        Args:
            ignore_oversize: If ``True``, the validity of the resulting *rendered size*
              is not checked.

        See the description of ``set_size()`` for the other parameters.

        Returns:
            A valid *render size* tuple.
        """
        ori_width, ori_height = self._original_size

        columns, lines = maxsize or map(sub, get_terminal_size(), (h_allow, v_allow))
        for name in ("columns", "lines"):
            if locals()[name] <= 0:
                raise ValueError(f"Number of available {name} too small")

        # Two pixel rows per line
        rows = (lines) * 2

        # NOTE: The image scale is not considered since it should never be > 1

        if width is None is height:
            if not check_height:
                width = columns * _pixel_ratio
                # Adding back later compensates for the rounding
                self._width_compensation = columns - (round(width) / _pixel_ratio)
                return (round(width), round(ori_height * width / ori_width))
            if not check_width:
                self._width_compensation = 0.0
                return (round(ori_width * rows / ori_height), rows)

            # The smaller fraction will always fit into the larger fraction
            # Using the larger fraction with cause the image not to fit on the axis with
            # the smaller fraction
            factor = min(map(truediv, (columns, rows), (ori_width, ori_height)))
            width, height = map(round, map(mul, (factor,) * 2, (ori_width, ori_height)))

            # The width will later be divided by the pixel-ratio when rendering
            rendered_width = width / _pixel_ratio
            if round(rendered_width) <= columns:
                self._width_compensation = 0.0
                return (width, height)
            else:
                # Adjust the width such that the rendered width is exactly the maximum
                # number of available columns and adjust the height proportionally

                # w1 == rw1 * (w0 / rw0) == rw1 * _pixel_ratio
                new_width = round(columns * _pixel_ratio)
                # Adding back later compensates for the rounding
                self._width_compensation = columns - (new_width / _pixel_ratio)
                return (
                    new_width,
                    # h1 == h0 * (w1 / w0) == h0 * (rw1 / rw0)
                    # But it's better to avoid the rounded widths
                    round(height * columns / rendered_width),
                )
        elif width is None:
            width = round((height / ori_height) * ori_width)
        elif height is None:
            height = round((width / ori_width) * ori_height)

        if not (width and height):
            raise InvalidSize(
                f"The resulting render size is too small: {width, height}"
            )
        if not ignore_oversize and (
            # The width will later be divided by the pixel-ratio when rendering
            (check_width and round(width / _pixel_ratio) > columns)
            or (check_height and height > rows)
        ):
            raise InvalidSize(
                "The resulting rendered size will not fit into the available size"
            )

        self._width_compensation = 0.0
        return (width, height)


# Reserved
def _color(text: str, fg: tuple = (), bg: tuple = ()) -> str:
    """Prepends *text* with ANSI 24-bit color escape codes
    for the given foreground and/or background RGB values.

    The color code is ommited for any of *fg* or *bg* that is empty.
    """
    return (_FG_FMT * bool(fg) + _BG_FMT * bool(bg) + "%s") % (*fg, *bg, text)


# The pixel ratio is always used to adjust the width and not the height, so that the
# image can fill the terminal screen as much as possible.
# The final width is always rounded, but that should never be an issue
# since it's also rounded during size validation.
_pixel_ratio = 1.0  # Default
