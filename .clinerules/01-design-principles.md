# Design principles

- **Simplicity and predictability.** Each script is a pure input -> output transform:
  give it a `.mrs`/`.dms` file, get a beautified `.f.mrs` (and optionally a `.upd.mrs`)
  file back. Keep the scripts focused on formatting/normalizing the input; avoid
  turning them into general-purpose DMS/mrStudio tooling.
- Modularity: Prefer self-contained, cohesive components with clearly defined inputs and outputs.
- Testing: Accompany new features and behavioral changes with appropriate automated tests.
- Dependencies: Avoid unnecessary dependencies.
- Consistency: Follow existing project conventions and avoid unrelated changes.
