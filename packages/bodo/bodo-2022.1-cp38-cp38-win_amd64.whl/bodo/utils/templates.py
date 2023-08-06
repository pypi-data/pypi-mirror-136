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
            unrnp__cppql = set()
            dwooo__vico = list(self.context._get_attribute_templates(self.key))
            niig__rjrbr = dwooo__vico.index(self) + 1
            for msm__muf in range(niig__rjrbr, len(dwooo__vico)):
                if isinstance(dwooo__vico[msm__muf], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    unrnp__cppql.add(dwooo__vico[msm__muf]._attr)
            self._attr_set = unrnp__cppql
        return attr_name in self._attr_set
