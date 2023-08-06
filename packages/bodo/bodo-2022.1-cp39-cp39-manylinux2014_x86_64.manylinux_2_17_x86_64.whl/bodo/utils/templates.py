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
            dszf__kgd = set()
            vxwid__fcvtn = list(self.context._get_attribute_templates(self.key)
                )
            qpzk__vizlx = vxwid__fcvtn.index(self) + 1
            for nxe__wjb in range(qpzk__vizlx, len(vxwid__fcvtn)):
                if isinstance(vxwid__fcvtn[nxe__wjb], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    dszf__kgd.add(vxwid__fcvtn[nxe__wjb]._attr)
            self._attr_set = dszf__kgd
        return attr_name in self._attr_set
