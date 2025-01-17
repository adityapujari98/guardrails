import pytest
from lxml.etree import Element, SubElement, tostring

from guardrails.utils.reask_utils import (
    FieldReAsk,
    gather_reasks,
    get_pruned_tree,
    prune_obj_for_reasking,
)
from guardrails.validators import FailResult, PydanticReAsk

# FIXME: These tests are not exhaustive.
# They only add missing coverage from the 0.2 release
# We really should strive for close to 100% unit test coverage
#   and use Integration tests for mimicking user flows


def test_gather_reasks():
    reask = PydanticReAsk()
    reask["failed_prop"] = FieldReAsk(
        path=["$.failed_prop.child"],
        fail_results=[
            FailResult(error_message="child should not be None", outcome="fail")
        ],
        incorrect_value=None,
    )

    gathered_reasks = gather_reasks(reask)

    assert len(gathered_reasks) == 1
    assert gathered_reasks[0] == reask["failed_prop"]


empty_root = Element("root")
non_empty_root = Element("root")
property = SubElement(non_empty_root, "property")
property.attrib["format"] = "two-words"
child = SubElement(property, "child")
child.attrib["format"] = "two-words"
non_empty_output = Element("root")
output_property = SubElement(non_empty_output, "property")
output_child = SubElement(output_property, "child")
output_child.attrib["format"] = "two-words"


@pytest.mark.parametrize(
    "root,reasks,expected_output",
    [(empty_root, None, empty_root), (non_empty_root, [child], non_empty_output)],
)
def test_get_pruned_tree(root, reasks, expected_output):
    actual_output = get_pruned_tree(root, reasks)

    assert tostring(actual_output) == tostring(expected_output)


def test_prune_obj_for_reasking():
    reask = FieldReAsk(
        path=["$.failed_prop.child"],
        fail_results=[
            FailResult(error_message="child should not be None", outcome="fail")
        ],
        incorrect_value=None,
    )
    reasks = [reask, "not a reask"]

    pruned_reasks = prune_obj_for_reasking(reasks)

    assert len(pruned_reasks) == 1
    assert pruned_reasks[0] == reask
