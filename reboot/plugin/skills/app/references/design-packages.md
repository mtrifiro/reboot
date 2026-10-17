---
title: Splitting the Domain Model into Packages
impact: MEDIUM
impactDescription: Read when `model_diff.py` lists a package under _Packages_: one with six domain objects or more, or packages that import each other in a circle. The split is a suggestion in the handoff's Notes, never done unasked.
tags: design, packages, architecture, model diff
---

## Splitting the Domain Model into Packages

`model_diff.py` lists, under _Packages_, a package that holds six
domain objects or more, and packages that import each other in a
circle. Either goes into the handoff's **Notes** as a suggestion, one
line each, never as a question of its own and never done unasked:

- **Split by area:** one package per area of the work (for a hotel,
  `rooms.v1`, `reservations.v1`, `staff.v1`), and one on top that
  joins them (`hotel.v1`), imported by none. The dashboard's Models
  page then shows each area on its own, and the calls between them as
  the joins.
- **A circle:** layer the packages so the one on top imports the
  others and none imports back.
- **What it costs,** said with it: a method can't declare an error
  from another package (reboot#258), so the top package keeps its own
  copy of each error it passes on; each package needs its own
  `.mypy.ini` entry; the dashboard links and `design.md` move to the
  new names.
- **When:** before the first deploy, while the data is demo data. A
  domain object's full name includes its package, so moving one after
  deploy is likely a rename, which
  `python/references/api-schema-evolution.md` counts as a delete and
  an add.

On the user's yes it is a design change like any other: the split,
`design.md` with the new names, a decisions entry, and acceptance
([`accept-design.md`](accept-design.md)).
