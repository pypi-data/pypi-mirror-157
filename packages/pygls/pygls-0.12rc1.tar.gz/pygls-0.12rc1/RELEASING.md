# Releasing a new version of Pygls

Pygls is hosted as a package at https://pypi.org/project/pygls

Releases follow https://keepachangelog.com/en/1.0.0 and https://semver.org/spec/v2.0.0.html

Release notes are kept in CHANGELOG.md

## Steps to release

  * Install:
      * Python's [build module](https://pypa-build.readthedocs.io/en/latest/) with Pip or your
        OS's package manager
      * [Twine](https://twine.readthedocs.io/en/stable/) for interacting with pypi.org 
  * It's probably best to make a dedicated release branch, but not essential
  * Update CHANGELOG.md


```sh
# Create a git tag of the new version, eg; v0.0.1
git tag v0.0.1

# Build the project into the Source and Wheel formats (they go into `./dist`)
python -m build

# Upload to Pypi
# You'll also need, or have access to, the Pygls Pypi org or account. Likely from @dgreisen
twine upload dist/*
```
