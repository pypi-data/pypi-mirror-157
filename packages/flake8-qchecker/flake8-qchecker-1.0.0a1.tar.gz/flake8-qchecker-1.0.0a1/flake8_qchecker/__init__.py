from qchecker.parser import CodeModule
from qchecker.substructures import SUBSTRUCTURES

__version__ = "1.0.0a1"


class Plugin:
    name = __name__
    version = __version__

    # Named tree parameter is required by flake8
    def __init__(self, tree, lines):
        code = ''.join(lines)
        self.module = CodeModule(code)

    def run(self):
        yield from sorted(self._get_matches(), key=lambda elt: elt[:1])

    def _get_matches(self):
        for i, substructure in enumerate(SUBSTRUCTURES):
            for match in substructure.iter_matches(self.module):
                pos = match.text_range
                msg = (
                    f"Q{i:02d} {match.id}"
                    f" ({pos.from_line},{pos.from_offset}"
                    f"->{pos.to_line},{pos.to_offset})"
                )
                yield pos.from_line, pos.from_offset, msg, type(self)
