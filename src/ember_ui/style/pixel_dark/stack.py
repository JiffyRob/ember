from ember_ui.ui.stack import Stack as _Stack
from ember_ui.ui.v_stack import VStack as _VStack
from ember_ui.ui.h_stack import HStack as _HStack
from .container import Container

from ember_ui.spacing.fill_spacing import FillSpacing


class Stack(_Stack, Container):
    ...


Stack.spacing.default_value = FillSpacing(min_value=6)

class VStack(_VStack, Stack):
    ...

class HStack(_HStack, Stack):
    ...
