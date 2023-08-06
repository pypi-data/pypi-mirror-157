from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Tuple


@dataclass
class NodeRef:
    """
    Used so we can more easily modify the QueryTree by inserting and removing nodes, e.g.
    def subtree_rewrite(subtree_node_ref):
        subtree_node_ref.node = NewNode(subtree_node_ref.node)
    """

    node: "QueryNode"

    @property
    def inputs(self):
        return self.node.inputs

    def as_str(self, verbose: bool = False) -> str:
        return self.node.as_str(verbose)

    def pretty_print(self, verbose: bool = False, indents=0):
        return self.node.pretty_print(verbose, indents)


class QueryNode(ABC):
    # used for recursing through the tree for tree rewrites
    @property
    @abstractmethod
    def inputs(self) -> Tuple[NodeRef]:
        pass

    @abstractmethod
    def as_str(self, verbose: bool) -> str:
        """
        Prints contents of this node and calls recursively on its inputs.
        Used by tecton.DataFrame.explain
        """
        pass

    # TODO: update this placeholder printing logic with something that looks beautiful
    def pretty_print(self, verbose: bool = False, indents=0) -> str:
        s = ""
        lines = self.as_str(verbose=verbose).rstrip()
        for line in lines.split("\n"):
            s += "  " * indents + line + "\n"
        if len(self.inputs) == 1:
            s += self.inputs[0].pretty_print(verbose, indents + 1)
        else:
            for i in self.inputs:
                s += i.pretty_print(verbose, indents + 1)
        return s
