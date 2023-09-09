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

[diff v1.1.0...main](https://github.com/rstcheck/rstcheck-core/compare/v1.1.0...main)

## [1.1.0 (2023-09-09)](https://github.com/rstcheck/rstcheck-core/releases/v1.1.0)

[diff vv1.0.3...v1.1.0](https://github.com/rstcheck/rstcheck-core/compare/vv1.0.3...v1.1.0)

### Bugfixes

- Auto discover pyproject.toml file on py311 and up

### Documentation

- Update inv file for pydantic links ([#60](https://github.com/rstcheck/rstcheck-core/pull/60))

### Miscellaneous

- Ignore "no newline at end of file" errors when C++ code is checked by clang (such as on macOS) ([#45](https://github.com/rstcheck/rstcheck-core/pull/45))
- Drop python 3.7 ([#52](https://github.com/rstcheck/rstcheck-core/pull/52))
- Drop support for Sphinx v2 and v3 ([#51](https://github.com/rstcheck/rstcheck-core/pull/51))
- Add tox environments for v6 and v7 ([#51](https://github.com/rstcheck/rstcheck-core/pull/51))
- Add basic pydantic v2 support ([#53](https://github.com/rstcheck/rstcheck-core/pull/53))
- Update Sphinx Theme Version and remove outdated Dark Mode Lib ([#51](https://github.com/rstcheck/rstcheck-core/pull/51))
- Switch from poetry to setuptools ([#59](https://github.com/rstcheck/rstcheck-core/pull/59))
- Change test file naming convention ([#60](https://github.com/rstcheck/rstcheck-core/pull/60))
- Change dev tooling ([#60](https://github.com/rstcheck/rstcheck-core/pull/60))
- Drop pydantic v1 support ([#60](https://github.com/rstcheck/rstcheck-core/pull/60))
- Add python 3.12 to CI ([#60](https://github.com/rstcheck/rstcheck-core/pull/60))

## [1.0.3 (2022-11-12)](https://github.com/rstcheck/rstcheck-core/releases/v1.0.3)

[diff v1.0.2...v1.0.3](https://github.com/rstcheck/rstcheck-core/compare/v1.0.2...v1.0.3)

### Documentation

- Update release docs for changed release script
- Restructure FAQ in docs

### Miscellaneous

- Fix release script's changelog insertion
- Add pre-commit-ci badge to README
- Update development tooling dependencies
- Update GHA workflows ([#22](https://github.com/rstcheck/rstcheck-core/issues/22))
- Add support for python 3.11 ([#21](https://github.com/rstcheck/rstcheck-core/issues/21))
- Update docutils version constraint ([#20](https://github.com/rstcheck/rstcheck-core/issues/20))

## [1.0.2 (2022-05-30)](https://pypi.org/project/rstcheck-core/1.0.2)

[diff v1.0.1.post2...v1.0.2](https://github.com/rstcheck/rstcheck-core/compare/v1.0.1.post2...v1.0.2)

### Miscellaneous

- Add tox envs to test with sphinx v5.
- Widen version range for `sphinx` extra to include v5.
- Update `sphinx` `extlinks` config for v5.
- Print error message on non-zero exit code ([#15](https://github.com/rstcheck/rstcheck-core/pull/15))
- Add integration tests based off of cli tests from `rstcheck` cli app ([#16](https://github.com/rstcheck/rstcheck-core/pull/16))

## 1.0.1.post2 (2022-05-30)

[diff v1.0.1.post1...v1.0.1.post2](https://github.com/rstcheck/rstcheck-core/compare/v1.0.1.post1...v1.0.1.post2)

### Miscellaneous

- Fix link for PyPI in changelog for 1.0.1 release.
- Fix link for PyPI in release script.

## 1.0.1.post1 (2022-05-30)

[diff v1.0.1...v1.0.1.post1](https://github.com/rstcheck/rstcheck-core/compare/v1.0.1...v1.0.1.post1)

### Miscellaneous

- Update changelog with missing notes

## [1.0.1 (2022-05-30)](https://pypi.org/project/rstcheck-core/1.0.1)

[diff v1.0.0...v1.0.1](https://github.com/rstcheck/rstcheck-core/compare/v1.0.0...v1.0.1)

### New features

- Add function to create dummy `Sphinx` app ([#13](https://github.com/rstcheck/rstcheck-core/pull/13))

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
