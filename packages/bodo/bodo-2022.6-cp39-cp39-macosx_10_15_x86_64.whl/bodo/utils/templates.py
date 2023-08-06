"""
Helper functions and classes to simplify Template Generation
for Bodo classes.
"""
import numba
from numba.core.typing.templates import AttributeTemplate


class OverloadedKeyAttributeTemplate(AttributeTemplate):
    _attr_set = None

    def _is_existing_attr(self, attr_name):
        if self._attr_set is None:
            covjk__bsr = set()
            wckge__hdqn = list(self.context._get_attribute_templates(self.key))
            isza__lvahp = wckge__hdqn.index(self) + 1
            for qdh__uaku in range(isza__lvahp, len(wckge__hdqn)):
                if isinstance(wckge__hdqn[qdh__uaku], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    covjk__bsr.add(wckge__hdqn[qdh__uaku]._attr)
            self._attr_set = covjk__bsr
        return attr_name in self._attr_set
