from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from plone.app.transmogrifier.utils import convert_path
from zope.interface import implementer
from zope.interface import provider


@provider(ISectionBlueprint)
@implementer(ISection)
class PathFixer:
    """Changes the start of the path."""

    def __init__(self, transmogrifier, name, options, previous):
        """
        :param options['path-key']: The key, under the path can be found in
                                    the item.
        :param options['stripstring']: A string to strip from the beginning of
                                       the path.
        :param options['prependstring']: A string to prepend on the beginning
                                         of the path.
        """
        self.previous = previous
        self.context = transmogrifier.context

        if "path-key" in options:
            pathkeys = options["path-key"].splitlines()
        else:
            pathkeys = defaultKeys(options["blueprint"], name, "path")
        self.pathkey = Matcher(*pathkeys)

        self.stripstring = None
        if "stripstring" in options and options["stripstring"]:
            self.stripstring = options["stripstring"].splitlines()[0]

        self.prependstring = None
        if "prependstring" in options and options["prependstring"]:
            self.prependstring = options["prependstring"].splitlines()[0]

    def __iter__(self):

        for item in self.previous:

            pathkey = self.pathkey(*list(item.keys()))[0]
            stripstring = self.stripstring
            prependstring = self.prependstring

            if not pathkey or not (stripstring or prependstring):
                # not enough info or nothing to do
                yield item
                continue

            path = item[pathkey]

            if stripstring and path.startswith(stripstring):
                str_size = len(stripstring)
                path = path[str_size:]
            if prependstring:
                path = f"{prependstring}{path}"

            # convert the path to str
            item[pathkey] = convert_path(path)

            yield item
