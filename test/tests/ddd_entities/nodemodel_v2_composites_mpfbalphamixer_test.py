import bpy, os
from pytest import approx
from .. import dynamic_import
from .. import ObjectService
from .. import NodeService
NodeWrapperMpfbAlphaMixer = dynamic_import("mpfb.entities.nodemodel.v2.composites.nodewrappermpfbalphamixer", "NodeWrapperMpfbAlphaMixer")
def test_composite_is_available():
    assert NodeWrapperMpfbAlphaMixer

def test_composite_can_create_instance():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree)
    assert node
    assert node.node_tree.name == "MpfbAlphaMixer"
    assert "Group Output" in node.node_tree.nodes
    assert "Group Input" in node.node_tree.nodes
    assert "LowerLayerBackground" in node.node_tree.nodes
    assert "UpperPremultiplied" in node.node_tree.nodes
    assert "LowerAttenuated" in node.node_tree.nodes
    assert "Composite" in node.node_tree.nodes
    assert "Math" in node.node_tree.nodes
    has_link_to_output = False
    for link in node.node_tree.links:
        if link.to_node.name == "Group Output":
            has_link_to_output = True
    assert has_link_to_output
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_composite_validate_tree():
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree)
    assert NodeWrapperMpfbAlphaMixer.validate_tree_against_original_def()
    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)

def test_composite_uses_premultiplied_over_compositing():
    # Regression guard for issue #269: the group must do "premultiplied over"
    # compositing, not the legacy quadratic-alpha mix. A correct graph has
    # UpperLayerAlpha driving UpperPremultiplied (premultiply U by uA),
    # LowerAttenuated (attenuate LB by 1-uA), and an ADD-blended Composite
    # node summing the two — anything else would re-introduce the white fringe.
    node_tree_name = ObjectService.random_name()
    node_tree = NodeService.create_node_tree(node_tree_name)
    node = NodeWrapperMpfbAlphaMixer.create_instance(node_tree)
    inner = node.node_tree

    composite = inner.nodes["Composite"]
    assert composite.blend_type == "ADD"
    assert composite.data_type == "RGBA"
    factor_input = next(s for s in composite.inputs if s.identifier == "Factor_Float")
    assert factor_input.default_value == approx(1.0)

    def has_link(from_node, from_socket, to_node, to_socket):
        for link in inner.links:
            if (link.from_node.name == from_node and link.from_socket.name == from_socket
                    and link.to_node.name == to_node and link.to_socket.name == to_socket):
                return True
        return False

    # UpperPremultiplied = mix(black, U, uA) → uA * U
    assert has_link("Group Input", "UpperLayerColor", "UpperPremultiplied", "B")
    assert has_link("Group Input", "UpperLayerAlpha", "UpperPremultiplied", "Factor")
    # LowerAttenuated = mix(LB, black, uA) → (1-uA) * LB
    assert has_link("LowerLayerBackground", "Result", "LowerAttenuated", "A")
    assert has_link("Group Input", "UpperLayerAlpha", "LowerAttenuated", "Factor")
    # Composite = LowerAttenuated + UpperPremultiplied → (1-uA)*LB + uA*U
    assert has_link("LowerAttenuated", "Result", "Composite", "A")
    assert has_link("UpperPremultiplied", "Result", "Composite", "B")
    assert has_link("Composite", "Result", "Group Output", "ResultingColor")

    node_tree.nodes.remove(node)
    NodeService.destroy_node_tree(node_tree)
