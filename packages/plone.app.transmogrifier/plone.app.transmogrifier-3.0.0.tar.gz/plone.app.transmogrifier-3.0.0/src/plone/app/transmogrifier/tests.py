from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.sections.tests import _marker
from collective.transmogrifier.sections.tests import MockObjectManager as Base
from collective.transmogrifier.sections.tests import SampleSource
from collective.transmogrifier.sections.tests import sectionsSetUp as ctSectionsSetup
from collective.transmogrifier.tests import tearDown
from DateTime.DateTime import DateTime
from plone.uuid.interfaces import IMutableUUID
from Zope2.App import zcml
from zope.component import adapter
from zope.component import provideUtility
from zope.interface import implementer
from zope.interface import provider

import doctest
import posixpath
import unittest


# Doctest support

optionflags = doctest.REPORT_NDIFF


def sectionsSetUp(test):
    ctSectionsSetup(test)
    import plone.app.transmogrifier

    zcml.load_config("configure.zcml", plone.app.transmogrifier)


class MockObjectManager(Base):
    def _getOb(self, id_, default=_marker):
        obj = super()._getOb(id_, default=default)
        if getattr(obj, "_path", "").endswith("/notatcontent"):
            return object()
        return obj

    def hasObject(self, id_):
        path = posixpath.join(self._path, id_)
        if path[0] == "/":
            return False  # path is absolute
        if path == "not/existing/bar":
            return False
        return True


def portalTransformsSetUp(test):
    sectionsSetUp(test)

    class MockPortalTransforms:
        def __call__(self, transform, data):
            return f"Transformed {data!r} using the {transform} transform"

        def convertToData(self, target, data, mimetype=None):
            if mimetype is not None:
                return f"Transformed {data!r} from {mimetype} to {target}"
            else:
                return f"Transformed {data!r} to {target}"

    test.globs["plone"].portal_transforms = MockPortalTransforms()


def workflowUpdaterSetUp(test):
    sectionsSetUp(test)

    from Products.CMFCore.WorkflowCore import WorkflowException

    class MockPortal(MockObjectManager):
        @property
        def portal_workflow(self):
            return self

        updated = []

        workflow_history = {}

        def doActionFor(self, ob, action):
            assert isinstance(ob, self.__class__)
            if action == "nonsuch":
                raise WorkflowException("Test exception")
            self.updated.append((self._last_path[0], action))

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class WorkflowSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(_path="/spam/eggs/foo", _transitions="spam"),
                dict(_path="/spam/eggs/baz", _transitions=("spam", "eggs")),
                dict(
                    _path="not/existing/bar",
                    _transitions=("spam", "eggs"),
                    title="Should not be updated, not an existing path",
                ),
                dict(
                    _path="spam/eggs/incomplete",
                    title="Should not be updated, no transitions",
                ),
                dict(
                    _path="/spam/eggs/nosuchtransition",
                    _transitions=("nonsuch",),
                    title="Should not be updated, no such transition",
                ),
                dict(
                    _path="/spam/eggs/bla",
                    _transitions=(
                        {
                            "action": "spam",
                            "review_state": "spammed",
                            "time": DateTime("2014-06-20"),
                        },
                    ),
                ),
            )

    provideUtility(WorkflowSource, name="plone.app.transmogrifier.tests.workflowsource")


def browserDefaultSetUp(test):
    sectionsSetUp(test)

    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

    @implementer(ISelectableBrowserDefault)
    class MockPortal(MockObjectManager):

        updated = []

        def setLayout(self, layout):
            self.updated.append((self._last_path[0], "layout", layout))

        def setDefaultPage(self, defaultpage):
            self.updated.append((self._last_path[0], "defaultpage", defaultpage))

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class BrowserDefaultSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(_path="/spam/eggs/foo", _layout="spam"),
                dict(_path="/spam/eggs/bar", _defaultpage="eggs"),
                dict(_path="/spam/eggs/baz", _layout="spam", _defaultpage="eggs"),
                dict(
                    _path="not/existing/bar",
                    _layout="spam",
                    title="Should not be updated, not an existing path",
                ),
                dict(
                    _path="spam/eggs/incomplete",
                    title="Should not be updated, no layout or defaultpage",
                ),
                dict(
                    _path="spam/eggs/emptylayout",
                    _layout="",
                    title="Should not be updated, no layout or defaultpage",
                ),
                dict(
                    _path="spam/eggs/emptydefaultpage",
                    _defaultpage="",
                    title="Should not be updated, no layout or defaultpage",
                ),
            )

    provideUtility(
        BrowserDefaultSource,
        name="plone.app.transmogrifier.tests.browserdefaultsource",
    )


def urlNormalizerSetUp(test):
    sectionsSetUp(test)

    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

    @implementer(ISelectableBrowserDefault)
    class MockPortal(MockObjectManager):
        pass

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class URLNormalizerSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(title="mytitle"),
                dict(title="Is this a title of any sort?"),
                dict(title="Put some <br /> $1llY V4LUES -- here&there"),
                dict(title="What about \r\n line breaks (system)"),
                dict(title="Try one of these --------- oh"),
                dict(language="My language is de"),
                dict(language="my language is en"),
            )

    provideUtility(
        URLNormalizerSource, name="plone.app.transmogrifier.tests.urlnormalizersource"
    )


def criteriaSetUp(test):
    sectionsSetUp(test)

    from Products.ATContentTypes.interface import IATTopic

    @implementer(IATTopic)
    class MockPortal(MockObjectManager):

        criteria = []

        def addCriterion(self, field, criterion):
            self.criteria.append((self._last_path[0], field, criterion))

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class CriteriaSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(_path="/spam/eggs/foo", _criterion="bar", _field="baz"),
                dict(
                    _path="not/existing/bar",
                    _criterion="bar",
                    _field="baz",
                    title="Should not be updated, not an existing path",
                ),
                dict(
                    _path="spam/eggs/incomplete",
                    title="Should not be updated, no criterion or field",
                ),
            )

    provideUtility(CriteriaSource, name="plone.app.transmogrifier.tests.criteriasource")


def mimeencapsulatorSetUp(test):
    sectionsSetUp(test)

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class EncapsulatorSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(_data="foobarbaz", _mimetype="application/x-test-data"),
                dict(_mimetype="skip/nodata"),
                dict(portrait="skip, no mimetypeset"),
                dict(portrait="someportraitdata", _portrait_mimetype="image/jpeg"),
            )

    provideUtility(
        EncapsulatorSource, name="plone.app.transmogrifier.tests.encapsulatorsource"
    )

    from OFS.Image import File

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class OFSFilePrinter:

        """Prints out data on any OFS.Image.File object in the item"""

        def __init__(self, transmogrifier, name, options, previous):
            self.previous = previous

        def __iter__(self):
            for item in self.previous:
                for key, value in item.items():
                    if isinstance(value, File):
                        print(f"{key}: ({value.content_type}) {str(value)}")
                yield item

    provideUtility(OFSFilePrinter, name="plone.app.transmogrifier.tests.ofsfileprinter")


def uidSetUp(test):
    sectionsSetUp(test)
    from plone.uuid.interfaces import IAttributeUUID

    @implementer(IAttributeUUID, IMutableUUID)
    @adapter(IAttributeUUID)
    class MockPortal(MockObjectManager):
        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == "/":
                return False  # path is absolute
            if path == "not/existing/bar":
                return False
            if path.endswith("/notatcontent"):
                return object()
            return True

        uids_set = []
        _uid = "xyz"

        def set(self, uid):
            self.uids_set.append((self._path, uid))
            self._uid = uid

        def get(self):
            return self._uid

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class UIDSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(
                    _path="/spam/eggs/foo",
                    _uid="abc",
                ),  # will be set
                dict(
                    _path="/spam/eggs/bar",
                    _uid="xyz",
                ),  # same as default
                dict(
                    _path="not/existing/bar",
                    _uid="def",
                ),  # not found
                dict(
                    _uid="geh",
                ),  # no path
                dict(
                    _path="/spam/eggs/baz",
                ),  # no uid
                dict(
                    _path="/spam/notatcontent",
                    _uid="ijk",
                ),
                # not referenceable
            )

    provideUtility(UIDSource, name="plone.app.transmogrifier.tests.uidsource")


def reindexObjectSetup(test):
    sectionsSetUp(test)

    from Products.CMFCore.CMFCatalogAware import CatalogAware

    @implementer(ISection)
    class MockPortal(MockObjectManager, CatalogAware):
        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == "/":
                return False  # path is absolute
            if path == "not/existing/bar":
                return False
            if path == "not/a/catalog/aware/content":
                return False
            return True

        @property
        def portal_catalog(self):
            return self

        reindexed = []

        def reindexObject(self, ob, idxs=[]):
            self.reindexed.append(
                (
                    self._last_path[0],
                    "reindexed",
                    "indexes: {}".format("all" if not idxs else ", ".join(idxs)),
                )
            )

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class ReindexObjectSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(_path="/spam/eggs/foo"),  # will be set
                dict(_path="/spam/eggs/bar"),  # will be set
                dict(_path="/spam/eggs/baz"),  # will be set
                dict(
                    _path="not/a/catalog/aware/content",
                    title="Should not be reindexed, not a CMFCatalogAware content",
                ),
                dict(
                    _path="not/existing/bar",
                    title="Should not be reindexed, not an existing path",
                ),
            )

    provideUtility(
        ReindexObjectSource, name="plone.app.transmogrifier.tests.reindexobjectsource"
    )


def redirectorSetUp(test):
    sectionsSetUp(test)
    from plone.app.redirector import interfaces
    from plone.app.redirector import storage

    provideUtility(
        storage.RedirectionStorage(), provides=interfaces.IRedirectionStorage
    )


def pathfixerSetUp(test):
    sectionsSetUp(test)

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class SchemaSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(_path="/spam/eggs/foo"),
                dict(_path="relative/path"),
                dict(_path="/spam/eggs/another"),
            )

    provideUtility(SchemaSource, name="plone.app.transmogrifier.tests.schemasource")


def datesupdaterSetUp(test):  # noqa: C901
    sectionsSetUp(test)

    class MockPortal(MockObjectManager):

        updated = []

        @property
        def creation_date(self):
            return DateTime()

        @creation_date.setter
        def creation_date(self, val):
            self.updated.append((self._last_path[0], "creation_date", val))

        @property
        def modification_date(self):
            return DateTime()

        @modification_date.setter
        def modification_date(self, val):
            self.updated.append((self._last_path[0], "modification_date", val))

        @property
        def effective_date(self):
            return DateTime()

        @effective_date.setter
        def effective_date(self, val):
            self.updated.append((self._last_path[0], "effective_date", val))

        @property
        def expiration_date(self):
            return DateTime()

        @expiration_date.setter
        def expiration_date(self, val):
            self.updated.append((self._last_path[0], "expiration_date", val))

    test.globs["plone"] = MockPortal()
    test.globs["transmogrifier"].context = test.globs["plone"]

    @provider(ISectionBlueprint)
    @implementer(ISection)
    class SchemaSource(SampleSource):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.sample = (
                dict(
                    _path="/spam/eggs/foo",
                    creation_date=DateTime("2010/10/10 UTC"),
                    modification_date=DateTime("2011/11/11 UTC"),
                    effective_date=DateTime("2010/10/10 UTC"),
                    expiration_date=DateTime("2012/12/12 UTC"),
                ),
                dict(  # only creation date updated
                    _path="/spam/eggs/bar",
                    creation_date=DateTime("2010/10/10 UTC"),
                ),
                dict(  # only modification date updated
                    _path="/spam/eggs/baz",
                    modification_date=DateTime("2011/11/11 UTC"),
                ),
                dict(  # only effective date updated
                    _path="/spam/eggs/qux",
                    effective_date=DateTime("2010/10/10 UTC"),
                ),
                dict(  # only expiration date updated
                    _path="/spam/eggs/norf",
                    expiration_date=DateTime("2012/12/12 UTC"),
                ),
                dict(  # Should not be updated, not an existing path
                    _path="not/existing/bar",
                    creation_date=DateTime("2010/10/10 UTC"),
                    modification_date=DateTime("2011/11/11 UTC"),
                    effective_date=DateTime("2010/10/10 UTC"),
                    expiration_date=DateTime("2012/12/12 UTC"),
                ),
                dict(  # Should not be updated, no path
                    creation_date=DateTime("2010/10/10 UTC"),
                    modification_date=DateTime("2011/11/11 UTC"),
                    effective_date=DateTime("2010/10/10 UTC"),
                    expiration_date=DateTime("2012/12/12 UTC"),
                ),
            )

    provideUtility(SchemaSource, name="plone.app.transmogrifier.tests.schemasource")


def test_suite():
    suite = unittest.TestSuite(
        (
            doctest.DocFileSuite(
                "uidupdater.rst",
                optionflags=optionflags,
                setUp=uidSetUp,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "portaltransforms.rst",
                optionflags=optionflags,
                setUp=portalTransformsSetUp,
                tearDown=tearDown,
                checker=doctest.OutputChecker(),
            ),
            doctest.DocFileSuite(
                "workflowupdater.rst",
                optionflags=optionflags,
                setUp=workflowUpdaterSetUp,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "browserdefault.rst",
                optionflags=optionflags,
                setUp=browserDefaultSetUp,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "urlnormalizer.rst",
                optionflags=optionflags,
                setUp=urlNormalizerSetUp,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "mimeencapsulator.rst",
                optionflags=optionflags,
                setUp=mimeencapsulatorSetUp,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "reindexobject.rst",
                optionflags=optionflags,
                setUp=reindexObjectSetup,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "redirector.rst",
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF,
                setUp=redirectorSetUp,
                tearDown=tearDown,
            ),
            doctest.DocFileSuite(
                "pathfixer.rst",
                optionflags=optionflags,
                setUp=pathfixerSetUp,
                tearDown=tearDown,
                checker=doctest.OutputChecker(),
            ),
            doctest.DocFileSuite(
                "datesupdater.rst",
                optionflags=optionflags,
                setUp=datesupdaterSetUp,
                tearDown=tearDown,
            ),
        )
    )
    return suite
