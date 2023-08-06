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
            dqid__diq = set()
            dpxd__epsp = list(self.context._get_attribute_templates(self.key))
            webf__icd = dpxd__epsp.index(self) + 1
            for gjj__frdy in range(webf__icd, len(dpxd__epsp)):
                if isinstance(dpxd__epsp[gjj__frdy], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    dqid__diq.add(dpxd__epsp[gjj__frdy]._attr)
            self._attr_set = dqid__diq
        return attr_name in self._attr_set
