import pygame
from ..common import SequenceElementType, DEFAULT
from typing import Optional, Union, Sequence
from ember.position import (
    PositionType,
    OptionalSequencePositionType,
    SequencePositionType,
)
from ..size import SizeType, OptionalSequenceSizeType
from .button import Button
from ..event import TOGGLEDON, TOGGLEDOFF

from ..event import CLICKEDDOWN
from ..on_event import on_event

from .text import Text


class ToggleButton(Button):
    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        active: bool = False,
        disabled: bool = False,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        **kwargs
    ):
        super().__init__(
            *elements,
            disabled=disabled,
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            **kwargs
        )

        self._active: bool = active

    def _post_button_event(self, event_type: int) -> None:
        if self._elements:
            text = (
                self._elements[self.primary_element_index].text
                if isinstance(self._elements[self.primary_element_index], Text)
                else None
            )
        else:
            text = None
        event = pygame.event.Event(
            event_type, element=self, text=text, active=self.active
        )
        self._post_event(event)

    @on_event(CLICKEDDOWN)
    def _toggle_active(self):
        self._active = not self._active
        self._post_button_event(TOGGLEDON if self._active else TOGGLEDOFF)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        if self._active != value:
            self._active = value
            self._post_button_event(TOGGLEDON if self._active else TOGGLEDOFF)
