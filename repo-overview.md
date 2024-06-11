## Overview of repositories

* Irrelevant repos:
  * PowerGridModel/power-grid-model: C++ libraries, Renovate cannot scan them, project is _not_ using a central repo like https://conan.io/
  * PowerGridModel/power-grid-model-io: Python project, but dependencies are _not pinned_
  * EVerest/libocpp: see power-grid-mode. There are only updates for GHA workflows
  * seapath/meta-seapath: uses BitBake, a language not supported by Renovate
* Relevant repos:
  * sogno-platform/dpsim: ca. 10 Python deps
  * EVerest/everest-admin-panel: > 25 JavaScript deps
  * EVerest/everest-core: most of its code is C++ (no deps found), but there are various other languages (e.g. Rust, JS) with dependency updates
  * EVerest/EVerest: seems to be a pure automation-related repo (> 4 GitHub Actions workflow updates)
  * sogno-platform/cimgen: >7 Python deps
  * openeemeter/eemeter: > 3 Python deps
  * com-pas/compas-open-scd: > 60 TS/JS dependencies
  * com-pas/compas-scl-data-service: > 7 Java deps
  * com-pas/compas-scl-auto-alignment: > 7 Java deps
  * com-pas/compas-core: > 7 Java deps
  * com-pas/compas-sct: > 19 Java deps
