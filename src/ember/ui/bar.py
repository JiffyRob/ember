from typing import Optional, Union, Sequence
from abc import ABC, abstractmethod
import pygame
import itertools

from .gauge import Gauge
from ember import log
from ember.ui.multi_element_container import MultiElementContainer

from ..material import Material

from ember.ui.element import Element
from .panel import Panel
from .two_panel_container import TwoPanelContainer

from ..event import VALUEMODIFIED
from ..common import SequenceElementType
from ember.axis import Axis, HORIZONTAL

from ..size import SizeType, OptionalSequenceSizeType, FILL, PivotableSize
from ember.position import (
    PositionType,
    SequencePositionType,
    LEFT,
    BOTTOM,
    PivotablePosition,
)

from ember.on_event import on_event


class Bar(TwoPanelContainer, Gauge, MultiElementContainer, ABC):

    def __init__(
        self,
        *elements: Optional[SequenceElementType],
        value: Optional[float] = 0,
        min_value: float = 0,
        max_value: float = 1,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: OptionalSequenceSizeType = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        axis: Axis = HORIZONTAL,
        **kwargs,
    ):
        super().__init__(
            *elements,
            # Gauge
            value=value,
            min_value=min_value,
            max_value=max_value,
            # MultiElementContainer
            rect=rect,
            pos=pos,
            x=x,
            y=y,
            size=size,
            w=w,
            h=h,
            axis=axis,
            **kwargs,
        )
        
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

        self.cascading.add(Element.x(PivotablePosition(LEFT, 0, watching=self)))
        self.cascading.add(Element.y(PivotablePosition(0, BOTTOM, watching=self)))

        size = PivotableSize(FILL * self._progress, FILL, watching=self)
        self.cascading.add(Element.w(size))
        self.cascading.add(Element.h(~size))

    @on_event()
    def _update_panel_material(self) -> None:
        self._back_panel.material = self._get_back_material()
        self._front_panel.material = self._get_front_material()

    @abstractmethod
    def _get_front_material(self) -> "Material":
        ...

    @abstractmethod
    def _get_back_material(self) -> "Material":
        ...

    @on_event(VALUEMODIFIED)
    def _update_panel_sizes(self):
        with log.size.indent("Updating bar cascading sizes..."):
            size = PivotableSize(FILL * self._progress, FILL, watching=self)
            self.cascading.add(Element.w(size))
            self.cascading.add(Element.h(~size))
            
            