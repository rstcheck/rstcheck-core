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

[diff v1.0.1...main](https://github.com/rstcheck/rstcheck-core/compare/v1.0.1...main)

## [1.0.1 (2022-05-30)](https://pypi.org/project/rstcheck/1.0.1)

[diff v1.0.0...v1.0.1](https://github.com/rstcheck/rstcheck-core/compare/v1.0.0...v1.0.1)

### New features

- Add function to create dummy `SPhinx` app ([#13](https://github.com/rstcheck/rstcheck-core/pull/13))

### Bugfixes

- Fix `sourcecode` directive being ignored, when Sphinx support is active ([#13](https://github.com/rstcheck/rstcheck-core/pull/13))

### Documentation

- Add section to FAQ about issue with language-less code blocks with sphinx ([#13](https://github.com/rstcheck/rstcheck-core/pull/13))

### Miscellaneous

- Changed log level for unparsable GCC style messages from WARNING to DEBUG to reduce noise.
- Log CRITICAL on AttributeError with sphinx support on, which mostly probably comes from
  language-less code blocks ([#13](https://github.com/rstcheck/rstcheck-core/pull/13))

## v1.0.0 (2022-05-29)

[diff v1.0.0rc1...v1.0.0](https://github.com/rstcheck/rstcheck-core/compare/v1.0.0rc1...v1.0.0)

### New features

- Non-existing paths are filtered out before checking and are logged as warning ([#10](https://github.com/rstcheck/rstcheck-core/pull/10))
- Use `<stdin>` for source in error messages instead of `-` ([#11](https://github.com/rstcheck/rstcheck-core/pull/11))
- Add constructor function for `IgnoreDict` ([#12](https://github.com/rstcheck/rstcheck-core/pull/12))

## v1.0.0rc1 (2022-05-28)

[diff split...v1.0.0](https://github.com/rstcheck/rstcheck-core/compare/split...v1.0.0rc1)

- Initial version after code base split from [rstcheck/rstcheck](https://github.com/rstcheck/rstcheck)
