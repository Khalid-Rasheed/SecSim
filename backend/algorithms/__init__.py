"""Algorithm plug-in packages.

Each subpackage (encryption / hashing / attacks) holds self-registering
algorithm modules. A module joins the platform by defining the contract
(simulate / analyze / COMPLEXITY / DETAILS) and calling register() once —
app.services.registry.discover() imports every module here automatically,
so no central file ever needs editing. See README "Adding an algorithm".
"""
