"""Main UI"""

import logging as _logging
import os
from os.path import basename, isfile, islink, realpath
from typing import Dict, Generator, Iterable, Tuple, Union

import PIL
import urwid

from .. import notify
from ..config import context_keys, expand_key
from ..image import TermImage
from ..logging import log_exception
from .keys import (
    disable_actions,
    display_context_keys,
    enable_actions,
    keys,
    menu_nav,
    no_globals,
    set_image_grid_actions,
    set_image_view_actions,
    set_menu_actions,
)
from .widgets import (
    Image,
    LineSquare,
    MenuEntry,
    image_box,
    image_grid,
    image_grid_box,
    info_bar,
    menu,
    placeholder,
    view,
    viewer,
)


def animate_image(image_widget: Image, forced_render: bool = False) -> None:
    """Changes frames of an animated image"""
    if NO_ANIMATION:
        return

    def change_frame(*_) -> None:
        nonlocal last_alarm, n

        loop.remove_alarm(last_alarm)
        if image_box.original_widget is image_widget:
            last_alarm = loop.set_alarm_in(FRAME_DURATION, change_frame)
            image.seek(n)
            if forced_render:
                image_widget._forced_render = True
            n += 1
            if n == image.n_frames:
                n = 0
        else:
            image.seek(0)
            # Avoid overwriting the frame-cache for a new animated image
            widget = image_box.original_widget
            if isinstance(widget, Image) and not widget._image._is_animated:
                Image._frame_cache = None

    image = image_widget._image
    Image._frame_cache = [None] * image._n_frames
    image.seek(0)
    n = 1
    last_alarm = loop.set_alarm_in(FRAME_DURATION, change_frame)


def display_images(
    dir: str,
    items: Iterable[Tuple[str, Union[Image, Generator]]],
    contents: dict,
    prev_dir: str = "..",
    *,
    top_level: bool = False,
) -> Generator[None, int, bool]:
    """Display images in _dir_ (and sub-directories, if '--recursive' is set)
    as yielded by `scan_dir(dir)`.

    Args:
        - dir: Path to directory containing images.
        - items: An iterator yielding the images in _dir_ and/or similar iterators
            for sub-directories of _dir_ (such as returned by `scan_dir(dir)`).
        - contents: Tree of directories containing readable images
            (such as returned by `check_dir(dir)`).
        - prev_dir: Path to set as working directory after displaying images in _dir_
            (default:  parent directory of _dir_).
        - top_level: Specifies if _dir_ is the top level (For internal use only).
    """
    items = sorted(
        items,
        key=(
            (
                lambda x: (
                    basename(x[0]).upper()
                    if isinstance(x[1], Image)
                    else basename(x[0]).lower()
                )
            )
            if top_level
            else (lambda x: x[0].upper() if isinstance(x[1], Image) else x[0].lower())
        ),
    )
    update_menu(items, top_level)

    entry = prev_pos = value = None  # Silence linter's `F821`
    pos = 0

    os.chdir(dir)

    while True:
        if pos == -1:  # Cursor on top menu item ("..")
            if top_level:
                if items:
                    # Ensure ".." is not selectable at top level
                    # Possible when "Home" action is invoked
                    pos = 0
                    menu.focus_position = 1
                    continue
                else:
                    set_context("global")
            image_box._w.contents[1][0].contents[1] = (
                placeholder,
                ("weight", 1, False),
            )
            image_box.original_widget = placeholder  # For image animation
            image_box.set_title("Image")
            view.original_widget = image_box

        elif pos == OPEN:  # Implements "menu::Open" action (for non-image entries)
            if prev_pos == -1:
                # prev_pos can never be -1 at top level (See `pos == -1` branch above),
                # so the program can't be broken.
                break

            if not value.gi_frame:
                # The directory has been visited earlier
                value = scan_dir(
                    entry,
                    contents[entry],
                    # Return to Top-Level Directory, OR
                    # Return to the link's parent rather than the linked directory's
                    # parent
                    os.getcwd() if top_level or islink(entry) else "..",
                )

            logger.debug(f"Going into {realpath(entry)}/")
            empty = yield from display_images(
                entry,
                value,
                contents[entry],
                # Return to Top-Level Directory, OR
                # to the link's parent instead of the linked directory's parent
                os.getcwd() if top_level or islink(entry) else "..",
            )

            if empty:  # All entries in the exited directory have been deleted
                del items[prev_pos]
                del contents[entry]
                pos = min(prev_pos, len(items) - 1)
                # Restore the menu and view pane for the previous (this) directory,
                # while removing the empty directory entry.
                update_menu(items, top_level, pos)

                logger.debug(f"Removed empty directory entry '{entry}/' from the menu")
                notify.notify(f"Removed empty directory entry '{entry}/' from the menu")
            else:
                # Restore the menu and view pane for the previous (this) directory
                update_menu(items, top_level, prev_pos)
                pos = prev_pos

            continue  # Skip `yield`

        elif pos == BACK:  # Implements "menu::Back" action
            if not top_level:
                break
            # Since the execution context is not exited at top-level, ensure pos
            # (and indirectly, prev_pos) always corresponds to a valid menu position.
            # By implication, this prevents an `IndexError` or rendering the wrong image
            # when coming out of a directory that was entered when prev_pos < -1.
            pos = prev_pos

        elif pos == DELETE:
            del items[prev_pos]
            pos = min(prev_pos, len(items) - 1)
            update_menu(items, top_level, pos)
            yield  # Displaying next image immediately will mess up confirmation overlay
            if DEBUG:
                info_bar.set_text(f"delete_pos={pos} {info_bar.text}")
            continue

        else:
            entry, value = items[pos]
            if isinstance(value, Image):
                image_box._w.contents[1][0].contents[1] = (value, ("weight", 1, False))
                image_box.set_title(entry)
                view.original_widget = image_box
                image_box.original_widget = value  # For image animation
                if value._image._is_animated:
                    animate_image(value)
            else:  # Directory
                # For some reason, the `GridListBox` renders the cached canvas whenever
                # the previous grid is empty
                if not image_grid.cells:
                    image_grid_box.base_widget._invalidate()

                image_grid.contents[:] = [
                    (
                        urwid.AttrMap(LineSquare(val), "unfocused box", "focused box"),
                        image_grid.options(),
                    )
                    for _, val in scan_dir(
                        entry,
                        contents[entry],
                        # Return to Top-Level Directory, OR
                        # Return to the link's parent rather than the linked directory's
                        # parent
                        os.getcwd() if top_level or islink(entry) else "..",
                    )
                    if isinstance(val, Image)  # Exclude directories from the grid
                ]

                image_grid_box.set_title(f"{realpath(entry)}/")
                view.original_widget = image_grid_box
                Image._grid_cache.clear()
                if image_grid.cells:
                    enable_actions("menu", "Switch Pane")
                else:
                    disable_actions("menu", "Switch Pane")

        prev_pos = pos
        pos = yield
        while pos == prev_pos:
            pos = yield
        if DEBUG:
            info_bar.set_text(f"pos={pos} {info_bar.text}")

    if not top_level:
        logger.debug(f"Going back to {realpath(prev_dir)}/")
        os.chdir(prev_dir)

    return not len(items)


def get_context() -> None:
    """Returns the current context"""
    return _context


def get_prev_context(n: int = 1) -> None:
    """Return the nth previous context (1 <= n <= 3)"""
    return _prev_contexts[n - 1]


def process_input(key: str) -> bool:
    if DEBUG:
        info_bar.set_text(f"{key!r} {info_bar.text}")

    found = False
    if key in keys["global"]:
        if (
            _context not in no_globals
            or _context == "global"
            or key in {"resized", expand_key[0]}
        ):
            func, state = keys["global"][key]
            func() if state else print("\a", end="", flush=True)
            found = True

    elif key[0] == "mouse press":  # strings also support subscription
        # change context if the pane in focus changed.
        if _context in {"image", "image-grid"} and viewer.focus_position == 0:
            set_context("menu")
            menu_nav()
            found = True
        elif _context == "menu":
            if viewer.focus_position == 1:
                if not context_keys["menu"]["Switch Pane"][4]:
                    # Set focus back to the menu if "menu::Switch Pane" is disabled
                    viewer.focus_position = 0
                else:
                    if view.original_widget is image_box:
                        set_context("image")
                        set_image_view_actions()
                    else:
                        set_context("image-grid")
                        set_image_grid_actions()
            else:  # Update image view
                menu_nav()
            found = True

    else:
        func, state = keys[_context].get(key, (None, None))
        if state:
            func()
        elif state is False:
            print("\a", end="", flush=True)
        found = state is not None

    return bool(found)


def scan_dir(
    dir: str, contents: Dict[str, Dict[str, dict]], prev_dir: str = ".."
) -> Generator[Tuple[str, Union[Image, Generator]], None, None]:
    """Scan _dir_ (and sub-directories, if '--recursive' is set) for readable images
    using a directory tree of the form produced by `.cli.check_dir(dir)`.

    Args:
        - dir: Path to directory to be scanned.
        - contents: Tree of directories containing readable images
            (as produced by `check_dir(dir)`).
        - prev_dir: Path to set as working directory after scannning _dir_
            (default:  parent directory of _dir_).

    Yields:
        - A `term_img.widgets.Image` instance for each image in _dir_.
        - A similar generator for sub-directories (if '--recursive' is set).

    - If '--all' is set, hidden (.*) images and subdirectories are considered.
    """
    os.chdir(dir)
    errors = 0
    for entry in os.listdir():
        if entry.startswith(".") and not SHOW_HIDDEN:
            continue
        if isfile(entry):
            try:
                PIL.Image.open(entry)
            except PIL.UnidentifiedImageError:
                # Reporting will apply to every non-image file :(
                pass
            except Exception:
                log_exception(f"{realpath(entry)!r} could not be read", logger)
                errors += 1
            else:
                yield entry, Image(TermImage.from_file(entry))
        elif RECURSIVE and entry in contents:
            if islink(entry):  # check_dir() already eliminates bad symlinks
                # Return to the link's parent rather than the linked directory's parent
                yield (
                    entry,
                    scan_dir(entry, contents[entry], os.getcwd()),
                )
            else:
                yield entry, scan_dir(entry, contents[entry])

    os.chdir(prev_dir)
    if errors:
        notify.notify(
            f"{errors} file(s) could not be read in {realpath(dir)!r}! Check the logs.",
            level=notify.ERROR,
        )


def set_context(new_context) -> None:
    """Sets the current context and updates the Key/Action bar"""
    global _context

    if DEBUG:
        info_bar.set_text(f"{_prev_contexts} {info_bar.text}")
    _prev_contexts[1:] = _prev_contexts[:2]  # Right-shift older contexts
    _prev_contexts[0] = _context
    _context = new_context
    display_context_keys(new_context)
    if DEBUG:
        info_bar.set_text(f"{new_context!r} {_prev_contexts} {info_bar.text}")


def set_prev_context(n: int = 1) -> None:
    """Set the nth previous context as the current context (1 <= n <= 3)"""
    global _context

    if DEBUG:
        info_bar.set_text(f"{_prev_contexts} {info_bar.text}")
    _context = _prev_contexts[n - 1]
    display_context_keys(_context)
    _prev_contexts[:n] = []
    _prev_contexts.extend(["menu"] * n)
    if DEBUG:
        info_bar.set_text(f"{_prev_contexts} {info_bar.text}")


def update_menu(
    items: Iterable[Tuple[str, Union[Image, Generator]]],
    top_level: bool = False,
    pos: int = 0,
) -> None:
    global menu_list, at_top_level
    menu_list, at_top_level = items, top_level

    menu.body[:] = [
        urwid.Text(("inactive", ".."))
        if top_level
        else urwid.AttrMap(MenuEntry(".."), "default", "focused entry")
    ] + [
        urwid.AttrMap(
            MenuEntry(
                basename(entry) + "/" * isinstance(value, Generator),
                "left",
                "clip",
            ),
            "default",
            "focused entry",
        )
        for entry, value in items
    ]
    menu.focus_position = pos + 1
    set_menu_actions()


logger = _logging.getLogger(__name__)

# For Context Management
_prev_contexts = ["menu"] * 3
_context = "menu"  # To avoid a NameError the first time set_context() is called.

# Constants for `display_images()`
OPEN = -2
BACK = -3
DELETE = -4

# Set by `update_menu()`
menu_list = None
at_top_level = None

# Placeholders; Set from `..tui.init()`
displayer = None
loop = None

# # Corresponsing to command-line args
DEBUG = None
FRAME_DURATION = None
MAX_PIXELS = None
NO_ANIMATION = None
RECURSIVE = None
SHOW_HIDDEN = None
