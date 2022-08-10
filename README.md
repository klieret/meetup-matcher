# Match small groups of people for coffee, tea, or whatever

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<!-- [![Documentation Status](https://readthedocs.org/projects/meetup-matcher/badge/?version=latest)](https://meetup-matcher.readthedocs.io/) -->
<!-- [![Pypi status](https://badge.fury.io/py/meetup-matcher.svg)](https://pypi.org/project/meetup-matcher/) -->
[![gh actions](https://github.com/klieret/meetup-matcher/actions/workflows/test.yaml/badge.svg)](https://github.com/klieret/meetup-matcher/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/klieret/meetup-matcher/main.svg)](https://results.pre-commit.ci/latest/github/klieret/meetup-matcher/main)
[![gitmoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg)](https://gitmoji.dev)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/github/license/klieret/meetup-matcher)](https://github.com/klieret/meetup-matcher/blob/master/LICENSE.txt)
[![PR welcome](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg)](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project)

A script to facilitate networking by matching people for meetups in small groups.

This works in three steps:

1. You obtain a list of email addresses of everyone interested
2. You run this script to match groups of three[^1] people together and to send them an email
3. Each group decides what to do, and where and when to meet on their own.

[^1]: Of course, depending on the number of people, you cannot have
all groups having three people. The script will add up to two groups of four people, or,
if there are very few people, one group of two people. Take a look at `_solve_numeric`
for the exact algorithm.

## 📦 Installation

Clone this repository and run

```bash
pip3 install .
```

## 🔥 Running the command line tool

After your installation you should have a `meetup-matcher` command in your path.
Run

```bash
meetup-matcher your-input.csv
```

## 🧰 Development setup

```bash
pip3 install -e .
gitmoji -i  # npm install gitmoji
pre-commit install  # pip3 install pre-commit
```

## 💖 Contributing

Your help is greatly appreciated! Suggestions, bug reports and feature requests are best opened as [github issues](https://github.com/klieret/meetup-matcher/issues). You are also very welcome to submit a [pull request](https://github.com/klieret/meetup-matcher/pulls)!

Bug reports and pull requests are credited with the help of the [allcontributors bot](https://allcontributors.org/).

<!-- ## ✨ Contributors -->
<!--  -->
<!-- Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)): -->
<!--  -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
<!--  -->
<!-- This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome! -->
