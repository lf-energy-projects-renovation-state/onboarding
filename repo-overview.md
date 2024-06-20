## Overview of repositories

* Irrelevant repos:
  * PowerGridModel/power-grid-model:
    * C++ libraries, Renovate cannot scan them, project is _not_ using a central repo like https://conan.io/
    * Contains Python code, but its requirements.txt does not **pin** the versions, thus Renovate does not find updates
  * PowerGridModel/power-grid-model-io: Python project, but dependencies are _not pinned_
  * EVerest/libocpp:
    * See power-grid-model. There are only updates for GHA workflows
    * Contains some python scripts that import 3rd party modules, but there is no requirements.txt that declares them
  * seapath/meta-seapath: uses BitBake, a language not supported by Renovate
* Relevant repos:
  * sogno-platform/dpsim: a few Python packages, and a few JavaScript deps (hugo docs)
  * EVerest/everest-admin-panel: > 25 JavaScript deps
  * EVerest/everest-core: most of its code is C++ (no deps found), but there are various other languages (e.g. Rust, JS) with dependency updates
  * EVerest/EVerest: seems to be a pure automation-related repo (> 4 GitHub Actions workflow updates)
  * sogno-platform/cimgen: >7 Python deps
  * openeemeter/eemeter:
    * A few Python deps
    * Uses Pipfile in which it has not pinned anything (although the Pipfile.lock has the pins), the few Python deps found by Renovate are for the docs-generation (docs/rtd-requirements.txt)
  * com-pas/compas-open-scd: > 60 TS/JS dependencies
  * com-pas/compas-scl-data-service: > 7 Java deps (Maven project)
  * com-pas/compas-scl-auto-alignment: > 7 Java deps (Maven project)
  * com-pas/compas-core: > 7 Java deps (Maven project)
  * com-pas/compas-sct: > 19 Java deps (Maven project)
