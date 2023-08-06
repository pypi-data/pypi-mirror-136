from drb import DrbNode

from drb.factory import DrbFactory
from drb_impl_java.drb_impl_java_node import DrbJavaBaseNode


class DrbJavaFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        return DrbJavaBaseNode(base_node=node)
