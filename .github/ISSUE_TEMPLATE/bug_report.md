---
name: Bug report
description: Report a reproducible defect
title: "[bug] "
labels: [bug]
body:
  - type: input
    attributes: { label: "Version / commit", description: "e.g. master @ abc1234" }
    validations: { required: true }
  - type: textarea
    attributes:
      label: "Reproduction"
      description: "Exact API payload or UI steps (for API bugs include the JSON body)"
      placeholder: |
        POST /api/simulate
        {"algorithm": "rsa", "input": "Hi"}
    validations: { required: true }
  - type: textarea
    attributes: { label: "Expected vs actual", description: "What should happen vs what happens" }
    validations: { required: true }
  - type: input
    attributes: { label: "Environment", description: "OS, Python/Node versions, browser" }
