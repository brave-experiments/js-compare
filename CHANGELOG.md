JS Compare
===

0.0.5
---

Add `--threshold` option, to control how large a subtree must be before we
consider it a potential match across code units.

Switch to better `pylintrc`.

0.0.4
---

Temporarily address issue with incorrectly normalized values by inefficiently,
redundantly tracking matched/attributed nodes in the overlap-checking
method (temporary because the algorithm should prevent this possibility, and
so there must be an implementation issue there I haven't found yet).

0.0.3
---

Correct errors in README.txt, and make minor change to default `Path` arguments
so produce a nice `--help` output.

0.0.2
---

Initial public version.
