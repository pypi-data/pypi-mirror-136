<!-- markdownlint-disable MD033 MD041 -->
<h1 align="center">
    Cryptolytics
</h1>

<p align="center">
    <strong>Fundamental analysis for blockchain and crypto projects</strong>
</p>

<p align="center">
    <a href="https://pypi.org/project/cryptolytics/" title="PyPi Version"><img src="https://img.shields.io/pypi/v/cryptolytics?color=green&style=flat"></a>
    <a href="https://pypi.org/project/cryptolytics/" title="Python Version"><img src="https://img.shields.io/badge/Python-3.6%2B-blue&style=flat"></a>
    <a href="https://github.com/lukasmasuch/cryptolytics/blob/main/LICENSE" title="Project License"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
    <a href="https://github.com/lukasmasuch/cryptolytics/actions?query=workflow%3Abuild-pipeline" title="Build status"><img src="https://img.shields.io/github/workflow/status/lukasmasuch/cryptolytics/build-pipeline?style=flat"></a>
    <a href="https://twitter.com/lukasmasuch" title="Follow on Twitter"><img src="https://img.shields.io/twitter/follow/lukasmasuch.svg?style=social&label=Follow"></a>
</p>

<p align="center">
  <a href="#getting-started">Getting Started</a> •
  <a href="#features">Features</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support--feedback">Support</a> •
  <a href="https://github.com/lukasmasuch/cryptolytics/issues/new?labels=bug&template=01_bug-report.md">Report a Bug</a> •
  <a href="#contribution">Contribution</a> •
  <a href="https://github.com/lukasmasuch/cryptolytics/releases">Changelog</a>
</p>

Calculate quality scores for open-source blockchain and crypto projects based on developer and social activity. Metadata is collected from a variety of different data sources. The goal is to get a list of the best projects for long-term investment based on the current project fundamentals.

## Highlights

_TBD_

## Getting Started

_TBD_

## Support & Feedback

Please understand that we won't be able to provide individual support via email. We also believe that help is much more valuable if it's shared publicly so that more people can benefit from it.

| Type                     | Channel                                              |
| ------------------------ | ------------------------------------------------------ |
| 🚨&nbsp; **Bug Reports**       | <a href="https://github.com/lukasmasuch/cryptolytics/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3Abug+sort%3Areactions-%2B1-desc+" title="Open Bug Report"><img src="https://img.shields.io/github/issues/lukasmasuch/cryptolytics/bug.svg?label=bug"></a>                                 |
| 🎁&nbsp; **Feature Requests**  | <a href="https://github.com/lukasmasuch/cryptolytics/issues?q=is%3Aopen+is%3Aissue+label%3Afeature+sort%3Areactions-%2B1-desc" title="Open Feature Request"><img src="https://img.shields.io/github/issues/lukasmasuch/cryptolytics/feature.svg?label=feature%20request"></a>                                 |
| 👩‍💻&nbsp; **Usage Questions**   |  <a href="https://github.com/lukasmasuch/cryptolytics/issues?q=is%3Aopen+is%3Aissue+label%3Asupport+sort%3Areactions-%2B1-desc" title="Open Support Request"> <img src="https://img.shields.io/github/issues/lukasmasuch/cryptolytics/support.svg?label=support%20request"></a> |
| 📢&nbsp; **Announcements**  | <a href="https://twitter.com/lukasmasuch" title="Follow me on Twitter"><img src="https://img.shields.io/twitter/follow/lukasmasuch.svg?style=social&label=Follow"> |

## Features

_TBD_

## Documentation

_TBD_

## Contribution

- Pull requests are encouraged and always welcome. Read our [contribution guidelines](https://github.com/lukasmasuch/cryptolytics/tree/main/CONTRIBUTING.md) and check out [help-wanted](https://github.com/lukasmasuch/cryptolytics/issues?utf8=%E2%9C%93&q=is%3Aopen+is%3Aissue+label%3A"help+wanted"+sort%3Areactions-%2B1-desc+) issues.
- Submit Github issues for any [feature request and enhancement](https://github.com/lukasmasuch/cryptolytics/issues/new?assignees=&labels=feature&template=02_feature-request.md&title=), [bugs](https://github.com/lukasmasuch/cryptolytics/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/lukasmasuch/cryptolytics/issues/new?assignees=&labels=documentation&template=03_documentation.md&title=) problems.
- By participating in this project, you agree to abide by its [Code of Conduct](https://github.com/lukasmasuch/cryptolytics/blob/main/.github/CODE_OF_CONDUCT.md).
- The [development section](#development) below contains information on how to build and test the project after you have implemented some changes.

## Development

To build the project and run the style/linter checks, execute:

```bash
pip install universal-build
python build.py --make --check
```

Alternatively, you can also run all necessary steps (build, check, test, and release) within a containerized environment by executing the following in the project root folder (this requires [Docker](https://docs.docker.com/get-docker/) and [Act](https://github.com/nektos/act#installation)):

```bash
act -b -j build
```

Refer to our [contribution guides](https://github.com/lukasmasuch/cryptolytics/blob/main/CONTRIBUTING.md#development-instructions) for more detailed information on our build scripts and development process.

---

Licensed **MIT**.
