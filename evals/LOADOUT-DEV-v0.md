# LOADOUT.dev/v0 Hostile Conformance Witness

| ID | Pytest witness |
| --- | --- |
| `MENTION-BIND-001` | `tests/test_dev_compiler.py::test_mention_bind_001_provider_mention_does_not_bind` |
| `DESIGN-GATE-001` | `tests/test_dev_workflow_policies.py::test_design_gate_001_requires_attributed_design_admission` |
| `RED-FIRST-001` | `tests/test_dev_workflow_policies.py::test_red_first_001_red_witness_precedes_mutation` |
| `ROOT-CAUSE-001` | `tests/test_dev_workflow_policies.py::test_root_cause_001_requires_hypothesis_and_probe_before_repair` |
| `VERIFY-FRESH-001` | `tests/test_dev_workflow_state.py::test_verify_fresh_001_mutation_expires_prior_verification` |
| `HEAD-DRIFT-001` | `tests/test_dev_workflow_state.py::test_head_drift_001_invalidates_ready_and_owner_admission` |
| `EFFECT-FENCE-001` | `tests/test_dev_membrane.py::test_effect_fence_001_observe_binding_cannot_mutate` |
| `REVIEW-SCOPE-001` | `tests/test_dev_workflow_policies.py::test_review_scope_001_out_of_scope_pressure_cannot_expand_repair` |
| `DOC-PUBLISH-001` | `tests/test_dev_workflow_policies.py::test_doc_publish_001_publish_requires_prior_proposal` |
| `WOLFRAM-FENCE-001` | `tests/test_dev_membrane.py::test_wolfram_fence_001_inspect_binding_cannot_invoke_evaluate` |
| `BODY-PIN-001` | `tests/test_dev_compiler.py::test_body_pin_001_replay_requires_exact_pin` |
| `RESULT-LAUNDER-001` | `tests/test_dev_membrane.py::test_result_launder_001_success_never_mints_semantic_authority` |
| `LAND-OBSERVE-001` | `tests/test_dev_membrane.py::test_land_observe_001_queued_request_is_not_observed_merge` |

Run all witnesses with `python -m pytest -q`. No live credentials or network access are involved.
