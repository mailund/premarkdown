import collections
from .. import plugin

class Section:
    def __init__(self, level, label):
        self.level = level
        self.label = label
        self.parent = None
        self.sibling = None
        self.first_child = None
        self.last_child = None
        self._word_count = 0

    @property
    def word_count(self):
        total_count = self._word_count
        child = self.first_child
        while child is not None:
            total_count += child.word_count
            child = child.sibling
        return total_count
    @word_count.setter
    def word_count(self, count):
        self._word_count = count


    def __repr__(self):
        fmt = 'Section(level={!r}, label={!r}'
        return fmt.format(
            self.level, self.label, 
            self.sibling,
            self.first_child, self.last_child
        )

    def hierarchy(self, indent, lines):
        node = "{} {} ({})".format(
            indent, self.label, self.word_count
        )
        lines.append(node)

        child_indent = indent + "#"
        child = self.first_child
        while child is not None:
            child.hierarchy(child_indent, lines)
            child = child.sibling

    def __str__(self):
        lines = []
        self.hierarchy("", lines)
        return '\n'.join(lines)

    def add_sibling(self, sibling):
        assert self.sibling is None, \
            "You shouldn't add a sibling to a node that already has one"
        assert self.level == sibling.level, \
            "Siblings must have the same level"
        self.sibling = sibling
        self.sibling.parent = self.parent

    def add_child(self, child):
        child.parent = self
        if self.first_child is None:
            self.first_child = child
        else:
            self.last_child.sibling = child
        self.last_child = child


class SectionCollector:
    def __init__(self):
        self.root = Section(level = 0, label = '<root>')
        self.current = self.root

    def add_section(self, level, label):
        next_section = Section(level, label)
        if self.current.level < level:
            while self.current.level < level - 1:
                filler = Section(self.current.level + 1, "")
                self.current.add_child(filler)
                self.current = filler
            self.current.add_child(next_section)

        elif self.current.level > level:
            while self.current.level > level:
                self.current = self.current.parent
            self.current.add_sibling(next_section)

        else: # self.current.level == level
            self.current.add_sibling(next_section)
        self.current = next_section
        
    def __str__(self):
        return 'Document:\n{}'.format(self.root)


class WC(plugin.ObserverPlugin, plugin.SummaryPlugin):
    """Word count in document"""
    def __init__(self):
        self.document = SectionCollector()

    def observe_line(self, filename, lineno, line):
        # FIXME: better recognition of words id:7
        #   
        # ----
        # <https://github.com/mailund/premarkdown/issues/8>
        # Thomas Mailund
        # mailund@birc.au.dk
        if line.startswith('#'):
            header_opcode, header_label = line.split(maxsplit=1)
            self.document.add_section(len(header_opcode), header_label)
        self.document.current.word_count += len(line.split())

    def summarize(self, outfile):
        # FIXME: better formatting id:9
        #   
        # ----
        # <https://github.com/mailund/premarkdown/issues/6>
        # Thomas Mailund
        # mailund@birc.au.dk
        print(self.document, file=outfile)

