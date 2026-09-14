---
name: Algorithm proposal
description: Propose a new algorithm for the lab
title: "[algo] "
labels: [enhancement]
body:
  - type: input
    attributes: { label: "Algorithm + family", description: "e.g. DES / encryption" }
    validations: { required: true }
  - type: textarea
    attributes: { label: "Spec reference", description: "Link to the standard/paper (FIPS, RFC…)" }
  - type: textarea
    attributes: { label: "Step design", description: "How will the step tape expose the internals? (phases, snapshots)" }
    validations: { required: true }
  - type: textarea
    attributes: { label: "Parameters", description: "Inputs the UI must collect (names + defaults)" }
  - type: textarea
    attributes: { label: "Security caveats", description: "Any teaching simplifications and how they will be labeled" }
    validations: { required: true }
