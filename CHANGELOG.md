# Changelog

All notable changes to this project will be documented in this file.
`pterradactyl` adheres to [Semantic Versioning](http://semver.org/).

#### 1.x Releases
- `1.3.x` Releases - [1.3.0](#130) | [1.3.1](#131)
- `1.2.x` Releases - [1.2.7](#127) | [1.2.8](#128) | [1.2.10](#1210) | [1.2.11](#1211) 

---
## Unreleased

#### Added

#### Updated

#### Deprecated

#### Removed

#### Fixed


---
## 1.3.1
#### Fixed
- Fixed import error related to importing metadata from importlib
  - Fixed by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike) in Pull Request [#14](https://github.com/Nike-Inc/pterradactyl/pull/14)

#### Removed
- Remove unused python-interface and MarkUpSafe dependencies
  - Removed by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike) in Pull Request [#14](https://github.com/Nike-Inc/pterradactyl/pull/14)

## 1.3.0
#### Updated
- Updated poetry version to 1.4.1
  - Updated by [Marcin Zalewski](https://github.com/marcinjzalewski) in Pull Request [#13](https://github.com/Nike-Inc/pterradactyl/pull/13)

#### Removed
- Removed support for python versions < 3.10.10
  - Removed by [Marcin Zalewski](https://github.com/marcinjzalewski) in Pull Request [#13](https://github.com/Nike-Inc/pterradactyl/pull/13)

## 1.2.11

#### Fixed
- Allow non-semantic versioning in the terraform provider plugin configuration.
  - Fixed by [Marcin Zalewski](https://github.com/marcinjzalewski) in Pull Request [#6](https://github.com/Nike-Inc/pterradactyl/pull/6)

---
## 1.2.10

#### Fixed
- Fixed backward compatibility issue caused due to unknown parameters in logging.BasicConfig introduced in python 3.9+.
  - Fixed by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike) in Pull Request [#5](https://github.com/Nike-Inc/pterradactyl/pull/5)

#### Added
- Added new lines in examples and test configs.
  - Added by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike) in Pull Request [#5](https://github.com/Nike-Inc/pterradactyl/pull/5)


---
## 1.2.8

#### Added
- Added check-version GitHub action.
  - Added by [Marcin Zalewski](https://github.com/marcinjzalewski)

#### Fixed
- Fix CoveCov token
  - Added by [Marcin Zalewski](https://github.com/marcinjzalewski)
- Fix relative links to absolute urls in README.md
  - Added by [Marcin Zalewski](https://github.com/marcinjzalewski)

---
## 1.2.7

#### Added
- Added Pterradactyl documentation and init Pterradactyl version for OSS
  - Added by [Marcin Zalewski](https://github.com/marcinjzalewski)

---

## 1.2.14
#### Fixed
- Fix replace log.info to print as it adds additional line in yaml file.
  - Added by [Marcin Zalewski](https://github.com/marcinjzalewski)