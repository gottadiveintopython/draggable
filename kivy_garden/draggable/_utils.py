__all__ = (
    'temp_transform', 'temp_grab_current',
    'save_widget_location', 'restore_widget_location',
)

from weakref import ref
from contextlib import contextmanager
from copy import deepcopy


@contextmanager
def temp_transform(touch):
    touch.push()
    try:
        yield
    finally:
        touch.pop()


@contextmanager
def temp_grab_current(touch):
    original = touch.grab_current
    try:
        yield
    finally:
        touch.grab_current = original


_shallow_copyable_property_names = (
    'x', 'y', 'width', 'height',
    'size_hint_x', 'size_hint_y',
    'size_hint_min_x', 'size_hint_min_y',
    'size_hint_max_x', 'size_hint_max_y',
)


def save_widget_location(widget, *, ignore_parent=False) -> dict:
    w = widget.__self__
    location = {
        name: getattr(w, name) for name in _shallow_copyable_property_names}
    location['pos_hint'] = deepcopy(w.pos_hint)
    if ignore_parent:
        return location
    parent = w.parent
    if parent is not None:
        location['weak_parent'] = ref(parent)
        location['index'] = parent.children.index(w)
    return location


def restore_widget_location(widget, location: dict, *, ignore_parent=False):
    w = widget.__self__
    weak_parent = location.get('weak_parent', None)
    index = location.get('index', None)
    for name in _shallow_copyable_property_names:
        setattr(w, name, location[name])
    w.pos_hint = deepcopy(location['pos_hint'])

    if ignore_parent or weak_parent is None:
        return
    parent = weak_parent()
    if parent is None:
        return
    if w.parent is not None:
        w.parent.remove_widget(w)
    parent.add_widget(w, index=index)
