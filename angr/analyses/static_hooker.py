
import logging

from . import Analysis, register_analysis

from .. import SIM_LIBRARIES
from ..errors import AngrValueError

l = logging.getLogger("angr.analyses.static_hooker")

class StaticHooker(Analysis):
    """
    This analysis works on statically linked binaries - it finds the library functions statically
    linked into the binary and hooks them with the appropriate simprocedures.

    Right now it only works on unstripped binaries, but hey! There's room to grow!
    """

    def __init__(self, library, binary=None):
        self.results = {}
        try:
            lib = SIM_LIBRARIES[library]
        except KeyError:
            raise AngrValueError("No such library %s" % library)

        if binary is None:
            binary = self.project.loader.main_bin

        for func in binary._symbol_cache.values():
            if not func.is_function:
                continue

            if self.project.is_hooked(func.rebased_addr):
                l.debug("Skipping %s at %#x, already hooked", func.name, func.rebased_addr)

            if lib.has_implementation(func.name):
                proc = lib.get(func.name, self.project.arch)
                self.project.hook(func.rebased_addr, proc)
                l.info("Hooked %s at %#x", func.name, func.rebased_addr)
                self.results[func.rebased_addr] = proc
            else:
                l.debug("Failed to hook %s at %#x", func.name, func.rebased_addr)

register_analysis(StaticHooker, 'StaticHooker')
