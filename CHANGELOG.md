# Changelog

This is the changelog of `rstcheck-core`. Releases and their respective
changes are listed here. The order of releases is time and **not** version based!
For a list of all available releases see the
[tags section on Github](https://github.com/rstcheck/rstcheck-core/tags).
Links on the versions point to PyPI.

<!-- Valid subcategories
NOTE: please use them in this order.
### BREAKING CHANGES
### New features
### Bugfixes
### Documentation
### Miscellaneous
-->

## Unreleased

[diff v1.0.0rc1...main](https://github.com/rstcheck/rstcheck-core/compare/v1.0.0rc1...main)

### New features

- Non-existing paths are filtered out before checking and are logged as warning ([#10](https://github.com/rstcheck/rstcheck-core/pull/10))
- Use `<stdin>` for source in error messages instead of `-` ([#11](https://github.com/rstcheck/rstcheck-core/pull/11))
- Add constructor function for `IgnoreDict` ([#12](https://github.com/rstcheck/rstcheck-core/pull/12))

## v1.0.0rc1 (2022-05-28)

[diff split...v1.0.0](https://github.com/rstcheck/rstcheck-core/compare/split...v1.0.0rc1)

- Initial version after code base split from [rstcheck/rstcheck](https://github.com/rstcheck/rstcheck)
