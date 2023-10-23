import pygame
import abc
from typing import TYPE_CHECKING, Optional, Sequence, Union

from ember_ui.common import DEFAULT, DefaultType

from ember_ui import log

if TYPE_CHECKING:
    from ember_ui.style.style import ScrollStyle
    from ember_ui.style.state import BackgroundState

from ember_ui import common as _c
from ember_ui.ui.base.element import Element
from .single_element_container import SingleElementContainer
from ember_ui.material.material import Material
from ember_ui.size import (
    SizeType,
    SequenceSizeType,
    OptionalSequenceSizeType,
    FitSize,
    FillSize,
)
from ember_ui.position import (
    PositionType,
    SequencePositionType,
    OptionalSequencePositionType,
)



from ember_ui.utility.timekeeper import BasicTimekeeper


class Scroll(SingleElementContainer, abc.ABC):
    """
    A Scroll holds one Element, and allows you to scroll that Element. There are two subclasses of Scroll -
    :py:class:`ember.ui.VScroll` and :py:class:`ember.ui.HScroll`. This base class should not be
    instantiated directly.
    """

    def __init__(
        self,
        element: Optional[Element] = None,
        material: Union["BackgroundState", Material, None] = None,
        over_scroll: Union[DefaultType, Sequence[int]] = DEFAULT,
        rect: Union[pygame.rect.RectType, Sequence, None] = None,
        pos: Optional[SequencePositionType] = None,
        x: Optional[PositionType] = None,
        y: Optional[PositionType] = None,
        size: Optional[SequenceSizeType] = None,
        w: Optional[SizeType] = None,
        h: Optional[SizeType] = None,
        content_pos: OptionalSequencePositionType = None,
        content_x: Optional[PositionType] = None,
        content_y: Optional[PositionType] = None,
        content_size: OptionalSequenceSizeType = None,
        content_w: Optional[SizeType] = None,
        content_h: Optional[SizeType] = None,
        style: Optional["ScrollStyle"] = None,
    ):
        self.state_controller: StateController = StateController(self)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        background states. Read-only.
        """

        self.scrollbar_controller: StateController = StateController(self, materials=2)
        """
        The :py:class:`ember.state.StateController` responsible for managing the Scroll's 
        scrollbar states. Read-only.
        """

        self.can_scroll: bool = False
        """
        Is :code:`True` when the child element is large enough to need scrolling. Read-only.
        """

        self.scrollbar_hovered: bool = False
        """
        Is :code:`True` when the user is hovering over the scrollbar handle. Read-only.
        """

        self.scrollbar_grabbed: bool = False
        """
        Is :code:`True` when the user is moving the scrollbar handle. Read-only.
        """

        super().__init__(
            material,
            rect,
            pos,
            x,
            y,
            size,
            w,
            h,
            content_pos,
            content_x,
            content_y,
            content_size,
            content_w,
            content_h,
            style,
        )

        self.over_scroll: tuple[int, int] = (
            self._style.over_scroll if over_scroll is DEFAULT else over_scroll
        )
        """
        The distance, in pixels, to allow scrolling past the child element. tuple[start, finish].
        """

        self._subsurf: Optional[pygame.Surface] = None

        self.layer = None

        self._element: Optional[Element] = None
        self.set_element(element, _update=False)

        self.scroll = BasicTimekeeper(self.over_scroll[0] * -1)
        self._scrollbar_pos: int = 0
        self._scrollbar_size: int = 0
        self._scrollbar_grabbed_pos: int = 0

    def _render_elements(
        self, surface: pygame.Surface, offset: tuple[int, int], alpha: int = 255
    ) -> None:
        rect = self._int_rect.move(*offset)
        if self.visible:

            self._element.render(self._subsurf, offset, alpha=alpha)
    
            self._render_scrollbar(surface, rect, alpha)

    @abc.abstractmethod
    def _render_scrollbar(
        self, surface: pygame.Surface, rect: pygame.Rect, alpha: int
    ) -> None:
        pass

    def _check_element(self, max_size: tuple[float, float]) -> None:
        pass

    def _update_rect(
        self, surface: pygame.Surface, x: float, y: float, w: float, h: float
    ) -> None:
        # self._check_element(max_size)

        Element._update_rect(self, surface, x, y, w, h)

        if (
            self._subsurf is None
            or (*self._subsurf.get_abs_offset(), *self._subsurf.get_size())
            != self._int_rect
            or self._subsurf.get_abs_parent() is not surface.get_abs_parent()
        ) and self.visible:
            parent_surface = surface.get_abs_parent()
            rect = self._int_rect.copy().clip(parent_surface.get_rect())
            try:
                self._subsurf = parent_surface.subsurface(rect)
            except ValueError as e:
                log.size.info(f"An error occured: {e}", self)
                self._scrollbar_calc()
                return

        self._scrollbar_calc()
        self._update_element_rect()

    @abc.abstractmethod
    def _update_element_rect(self) -> None:
        pass

    def _update_min_size(self) -> None:
        if isinstance(self._h, FitSize):
            if self._element:
                if isinstance(self._element._h, FillSize):
                    raise ValueError(
                        "Cannot have elements of FILL height inside of a FIT height Scroll."
                    )
                self._min_h = self._element.get_abs_h()
            else:
                self._min_h = 20

        if isinstance(self._w, FitSize):
            if self._element:
                if isinstance(self._element._w, FillSize):
                    raise ValueError(
                        "Cannot have elements of FILL width inside of a FIT width Scroll."
                    )
                self._min_w = self._element.get_abs_w()
            else:
                self._min_w = 20

    def _focus_chain(
        self, direction: _c.FocusDirection, previous: Optional["Element"] = None
    ) -> "Element":
        if self.layer.element_focused is self:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        if (
            direction
            in {
                _c.FocusDirection.LEFT,
                _c.FocusDirection.RIGHT,
                _c.FocusDirection.UP,
                _c.FocusDirection.DOWN,
                _c.FocusDirection.FORWARD,
            }
            or self._element is None
        ):
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        elif direction == _c.FocusDirection.OUT:
            log.nav.info(f"-> parent {self.parent}.")
            return self.parent._focus_chain(direction, previous=self)

        else:
            log.nav.info(f"-> child {self._element}.")
            return self._element._focus_chain(direction, previous=self)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONUP:
            if self.scrollbar_grabbed:
                self.scrollbar_grabbed = False
                return True

        if self._element is not None:
            # Stops you from clicking on elements that are clipped out of the frame
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.rect.collidepoint(_c.mouse_pos):
                    return False
            if self._element._event(event):
                return True

        if self._event2(event):
            return True

        return False

    @abc.abstractmethod
    def _event2(self, event: pygame.event.Event) -> bool:
        pass

    @abc.abstractmethod
    def _scrollbar_calc(self) -> None:
        pass

    def _clamp_scroll_position(self, max_scroll) -> None:
        # If the scrollbar is outside the limits, move it inside.

        if not (-self.over_scroll[0] <= self.scroll.val <= max_scroll):
            if -self.over_scroll[0] == self.scroll.val:
                return
            log.size.info(
                f"Scrollbar pos {self.scroll.val} is outside limits "
                f"{(-self.over_scroll[0], max_scroll)}, starting chain down...", self
            )
            if self.can_scroll:
                self.scroll.val = pygame.math.clamp(
                    self.scroll.val, -self.over_scroll[0], max_scroll
                )
            else:
                self.scroll.val = -self.over_scroll[0]
            if max_scroll <= 0:
                return
            self._update_element_rect()
            self._scrollbar_calc()

    @abc.abstractmethod
    def scroll_to_show_position(
        self, position: int, size: int = 0, offset: int = 0, duration: float = 0.1
    ) -> None:
        """
        Scroll so that a position is shown within the Scroll.
        """
        pass

    @abc.abstractmethod
    def scroll_to_element(self, element: Element) -> None:
        """
        Scroll so that an element is shown within the Scroll.
        """
        pass
