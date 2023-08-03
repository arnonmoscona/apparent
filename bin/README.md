# Testing & building

## Testing

The project uses `unittest` for all its test files and uses the `*tests.py`
pattern. Shell scripts provided:

* `bin/test` runs all unittest tests in `tests/`
* `bin/test-coverage` runs all unittest tests in `tests/` with coverage 
  (requires the `coverage` package)

## HTML documentation

The project uses 
[Google style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings). 
HTML documentation is generated with `pdoc` using the script `bin/build-docs`.

## Version bumping, build, and distribute

The project uses [flit](https://github.com/pypa/flit) and [bumpver](https://pypi.org/project/bumpver/)
and versioning uses the [semver pattern](https://semver.org/).

* to bump the patch version number run `bumpver update --patch`, similarly for minor and major. 
  This is set up to bump the version, commit, and push.
* to publish the project to pypi use `flit publish`

**Caveat emptor: at the time of this writing the sequencing of all of this is not automated yet - so be careful**
