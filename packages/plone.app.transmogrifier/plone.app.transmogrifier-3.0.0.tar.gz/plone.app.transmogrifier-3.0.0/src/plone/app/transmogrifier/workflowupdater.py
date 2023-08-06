from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import traverse
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.interface import implementer
from zope.interface import provider


# XXX Weird things may happen if you have multiple workflows.
# Needs investigating and solving //regebro


@provider(ISectionBlueprint)
@implementer(ISection)
class WorkflowUpdaterSection:
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, "portal_workflow")

        self.pathkey = defaultMatcher(options, "path-key", name, "path")
        self.transitionskey = defaultMatcher(
            options, "transitions-key", name, "transitions"
        )

    def __iter__(self):  # noqa: C901
        for item in self.previous:
            keys = list(item.keys())
            pathkey = self.pathkey(*keys)[0]
            transitionskey = self.transitionskey(*keys)[0]

            if not (pathkey and transitionskey):  # not enough info
                yield item
                continue

            path, transitions = item[pathkey], item[transitionskey]
            if isinstance(transitions, str):
                transitions = (transitions,)

            obj = traverse(self.context, str(path).lstrip("/"), None)
            if obj is None:  # path doesn't exist
                yield item
                continue

            for transition in transitions:
                if not isinstance(transition, str):
                    state = transition["review_state"]
                    time = transition["time"]
                    action = transition.get("action")
                    # no action if initial state
                    if action:
                        try:
                            self.wftool.doActionFor(obj, action)
                        except WorkflowException:
                            pass
                    history = getattr(obj, "workflow_history", None)
                    if history:
                        for wf in history:
                            for wf_state in history[wf]:
                                if wf_state["review_state"] == state:
                                    wf_state["time"] = time
                        obj.workflow_history = history
                else:
                    try:
                        self.wftool.doActionFor(obj, transition)
                    except WorkflowException:
                        pass

            yield item
