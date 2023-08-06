# Changelog

## 1.0.3

- **FIX**: Remove version check which is not compatible with Material Insiders. Material will completely be responsible
  for ensuring the correct version of `docums-material-extensions`.
- **FIX**: No longer specify `docums-material` as a dependency as `docums-material` specifies these extensions as a
  dependency. This created a circular dependency. While `pip` has no issues with such scenarios, this created issues
  for some versioning packages. `docums-material` (the only package this works with) will now manage which version of
  `docums-material-extensions` it needs.
- **FIX**: Ensure we don't modify the original icon path setting.

## 1.0

- **NEW**: First stable release.
