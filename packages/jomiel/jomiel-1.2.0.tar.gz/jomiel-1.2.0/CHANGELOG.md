# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.2.0](https://github.com/guendto/jomiel/compare/v1.1.0...v1.2.0) (2022-01-28)


### Features

* notify if --logger-ident did not match the logger identities ([d2cf98e](https://github.com/guendto/jomiel/commit/d2cf98ec51d00a06e6cac85b07c257df731fee23))

## [1.1.0](https://github.com/guendto/jomiel/compare/v1.0.4...v1.1.0) (2021-10-04)


### Features

* add support for env.var. BROKER_DEALER_ENDPOINT ([42db6e9](https://github.com/guendto/jomiel/commit/42db6e93971caaa12b2cb620edcacde275a36d67))
* add support for env.var. BROKER_ROUTER_ENDPOINT ([f4487c2](https://github.com/guendto/jomiel/commit/f4487c28f437087c98768c527f123c941e78ed56))


### Bug Fixes

* **subsys/broker/worker:** write errors using the error logging level ([8a40b3b](https://github.com/guendto/jomiel/commit/8a40b3bf1cca1c9bd016c9e10ddf9df5332a7133))
* **subsys/broker:** write errors using the error logging level ([b25a06f](https://github.com/guendto/jomiel/commit/b25a06ff07f050dab87ac22a2e9b3928ecf00faf))

## [v1.0.4] - 2021-09-17

### Fixed

* subsys/broker/worker: close dangling socket (8e3be09)

## [v1.0.3] - 2021-07-01

### Fixed

* plugin/youtube: workaround the age-gate (HTTP/404) (e269c41)

## [v1.0.2] - 2021-05-26

### Fixed

* plugin/youtube: frequent HTTP/404s while retrieving data (56704d0)

### Improved

* plugin/youtube: add an alt. pipeline to make video info requests

## [v1.0.1] - 2021-04-25

### Fixed

* Recover from incorrectly constructed Inquiry message (639966d)

### Changed

* Move ResponseBuilder class into subsys/broker/response
* setup.cfg: classifiers: Add "py39"
* README.md: Rewrite to be more concise
* README.md: demo.svg: Update to show `jomiel` working together with `yomiel`

## [v1.0.0] - 2021-01-08

### Added

* Packaging: new prerequisite [jomiel-comm]
* Packaging: new prerequisite [jomiel-kore]

[jomiel-comm]: https://pypi.org/project/jomiel-comm
[jomiel-kore]: https://pypi.org/project/jomiel-kore

### Removed

* git-subtrees for `jomiel-comm` and `jomiel-kore`

## [v0.999] - 2020-09-14

### Added

* Documentation/HOWTO: "build a release from the repo"
* Packaging: new prerequisite "jomiel-messages"
* Packaging: modernize setup with PEP-517+518

### Changed

* Use src/ layout from now on

### Removed

* jomiel-proto from the subtrees, don't dist `*_pb2.py` anymore
* requirements.[txt,in], use setup.cfg and `install_requires`

## [v0.4.2] - 2020-07-27

### Added

* Document: `jomiel` is a spiritual successor to libquvi

## [v0.4.1] - 2020-06-25

### Added

* Packaging: new prerequisite "ujson"

### Changed

* Use "ujson" instead of "json" package for improved performance
* Regenerate pinned package requirements

## [v0.4.0] - 2020-05-16

### Changed

* Reformat code according to pre-commit (with added) hooks
* Regenerate pinned package requirements

## [v0.3.0] - 2020-03-17

### Added

* Packaging: new prerequisite "importlib-resources"
* jomiel/data package

### Changed

* jomiel-keygen: disable --print-config (redundant)
* Use restructured .proto files (jomiel-proto)
* Regenerate pinned package requirements

### Fixed

* jomiel-keygen: output filename arg count check (9939599)

## [v0.2.1] - 2019-12-20

### Added

* Packaging: new prerequisite "importlib-metadata"

### Changed

* Use importlib-metadata for querying package metadata
* Make improvements to plugin.media.youtube.parser
* Regenerate pinned package requirements
* jomiel now requires py36+

### Fixed

* plugin.media.youtube.parser: skip token check if none is found

## [v0.2.0] - 2019-11-11

### Added

* pre-commit files
* tox files

### Changed

* Use black, instead of yapf, for code formatting from now on
* Reformat code according to pre-commit hooks

## [v0.1.3] - 2019-11-01

### Changed

* Use "Invalid input URI value given" for InvalidInputError
* Use new default port value "5514" for broker router
* Documentation: replace animated `*.png` files with a single .svg
* Packaging: bump requirements (protobuf, configargparse)
* Packaging: use pip-compile for pinning packages

## [v0.1.2] - 2019-09-30

### Added

* --broker-input-allow-any option
* Packaging: new prerequisite "validators"

### Changed

* Validate the value of incoming "input URL" by default from now on
* Packaging: bump requirements (protobuf, pyzmq, ruamel.yaml)

## [v0.1.1] - 2019-08-29

### Added

* --logger-idents-verbose option
* README.md: add HOWTO

### Changed

* --plugin-list no longer print redundant (info-level) messages
* --plugin-list now prints in the yaml format
* Packaging: bump requirements (protobuf, pyzmq, ruamel.yaml)
* Packaging: produce py3-only dist packages from now on

### Fixed

* plugin/media/youtube/parser: "KeyError: 'videoDetails'"
* plugin/media/youtube/parser: "KeyError: 'title'"

## [v0.1.0] - 2019-07-30

* First public preview release.

[v1.0.4]: https://github.com/guendto/jomiel/compare/v1.0.3..v1.0.4
[v1.0.3]: https://github.com/guendto/jomiel/compare/v1.0.2..v1.0.3
[v1.0.2]: https://github.com/guendto/jomiel/compare/v1.0.1..v1.0.2
[v1.0.1]: https://github.com/guendto/jomiel/compare/v1.0.0..v1.0.1
[v1.0.0]: https://github.com/guendto/jomiel/compare/v0.999..v1.0.0
[v0.999]: https://github.com/guendto/jomiel/compare/v0.4.2..v0.999
[v0.4.2]: https://github.com/guendto/jomiel/compare/v0.4.1..v0.4.2
[v0.4.1]: https://github.com/guendto/jomiel/compare/v0.4.0..v0.4.1
[v0.4.0]: https://github.com/guendto/jomiel/compare/v0.3.0..v0.4.0
[v0.3.0]: https://github.com/guendto/jomiel/compare/v0.2.1..v0.3.0
[v0.2.1]: https://github.com/guendto/jomiel/compare/v0.2.0..v0.2.1
[v0.2.0]: https://github.com/guendto/jomiel/compare/v0.1.3..v0.2.0
[v0.1.3]: https://github.com/guendto/jomiel/compare/v0.1.2..v0.1.3
[v0.1.2]: https://github.com/guendto/jomiel/compare/v0.1.1..v0.1.2
[v0.1.1]: https://github.com/guendto/jomiel/compare/v0.1.0..v0.1.1
[v0.1.0]: https://github.com/guendto/jomiel/releases/tag/v0.1.0
