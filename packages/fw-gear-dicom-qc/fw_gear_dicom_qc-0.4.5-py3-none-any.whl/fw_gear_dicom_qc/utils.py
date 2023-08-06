"""Utilities module for fw_gear_dicom_qc."""
from flywheel_gear_toolkit import GearToolkitContext


def update_metadata(
    context: GearToolkitContext, rule_results: dict, validation_results: list
):
    """Update qc metadata given results."""
    input_ = context.get_input("dicom")
    for name, res in rule_results.items():
        context.metadata.add_qc_result(
            input_, name, state=res.pop("state", "FAIL"), data=res
        )
    context.metadata.add_qc_result(
        input_,
        "jsonschema-validation",
        state=("PASS" if not len(validation_results) else "FAIL"),
        data=validation_results,
    )
