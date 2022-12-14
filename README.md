# Match small groups of people for coffee, tea, or whatever

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
<!-- ALL-CONTRIBUTORS-BADGE:END -->

[![Documentation Status](https://readthedocs.org/projects/meetup-matcher/badge/?version=latest)](https://meetup-matcher.readthedocs.io/en/latest/?badge=latest)
[![PR welcome](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg)](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project)
[![License](https://img.shields.io/github/license/klieret/meetup-matcher)](https://github.com/klieret/meetup-matcher/blob/master/LICENSE.txt)

<!-- [![Pypi status](https://badge.fury.io/py/meetup-matcher.svg)](https://pypi.org/project/meetup-matcher/) -->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/klieret/meetup-matcher/main.svg)](https://results.pre-commit.ci/latest/github/klieret/meetup-matcher/main)
[![gh actions](https://github.com/klieret/meetup-matcher/actions/workflows/test.yaml/badge.svg)](https://github.com/klieret/meetup-matcher/actions)
[![link checker](https://github.com/klieret/meetup-matcher/actions/workflows/check-links.yaml/badge.svg)](https://github.com/klieret/meetup-matcher/actions)
[![codecov](https://codecov.io/gh/klieret/meetup-matcher/branch/main/graph/badge.svg?token=3MKA387NOH)](https://codecov.io/gh/klieret/meetup-matcher)
[![gitmoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg)](https://gitmoji.dev)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

A script to facilitate networking by matching people for meetups in small groups.
Optimizing these groups in terms of overlapping schedules is a non-trivial matching problem.
Currently in use by the Princeton Postdoc Council with more than 100 participants matched.

Setting up a meetup works as follows:

1. Obtain a list of email addresses of everyone interested, optionally together with availabilities and extra information.
2. Run this script to match groups of three people and to send them an email.
3. Each group decides what to do on their own.

## Match-making

### Finding the right group sizes

The overwhelming majority of participants prefers groups of three and a non-negligible fraction vetos groups of two. However, the number of participants is not always divisible by three. Therefore, for sufficiently large numbers of participants, up to two groups of four are added. For very low (< 5) participants, a single group of two might be added if permitted by the vetos.

### Matching people and optimizing joint availabilities

If availabilities are surveyed in the sign-up form, then the groups are matched based on these availabilities. This means optimizing an objective function of the mutual availabilities of each group. More weight is given to avoiding groups of very low mutual availabilities.

This optimization problem reminds of the 3-dimensional version of the [stable roommates problem](https://en.wikipedia.org/wiki/Stable_roommates_problem), however the optimization goal does not necessarily lead to stable matches.

To be precise, the objective function is the tuple of number of removed people, number of groups with one joint availability, number of groups with two joint availabilities, etc. [Lexicographically ordering](https://en.wikipedia.org/wiki/Lexicographic_order) is applied to the tuples, that is, `(0, 1, 2, 3) < (0, 1, 3, 2)`, etc.

Currently, the optimization is performed by sampling the possibility space with heuristic weights:

1. Take the participant of lowest availability to start a group.
2. Iteratively add participants until the group size is reached. The probability for each participant is adjusted based on the joint availability with the already existing group members. It increases with high joint availability but also decreases when the participant would "waste" a lot of their availabilities (see below).
3. Step 1-2 are repeated until all groups are formed or until we know that we are doing worse than the best solution found so far (this is very simple because of the lexicographical ordering). As a result, only a very, very small[^1] percentage of trials forms all groups. This greatly speeds up the sampling process.
4. The global cost function is calculated for all groups.
5. Steps 1-4 are repeated many times to sample the possibility space.

To be precise, the weight from step 2 is currently chosen to be

![weight formula](<https://latex.codecogs.com/svg.image?p_k=\frac{\min(5,|\bigcap_{j\in&space;G\cup&space;{k}}A_j|)}{3&space;+&space;|A_k|}>)

where G represents the indices of the already added group members and A denotes the availabilities as a set.
The numbers 5 and 3 have been heuristically chosen.

[^1]: For a recent matching with 50 participants, 200k trials were performed, but only 16 of them were built completely.

## 📦 Installation

Clone this repository and run

```bash
pip3 install .
```

## 🔥 Running the command line tool

After your installation you should have a `meetup-matcher` command in your path.
A very simple run looks like

```bash
meetup-matcher your-input.csv
```

for more information, see [the documentation](https://meetup-matcher.readthedocs.io/en/latest/).

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
