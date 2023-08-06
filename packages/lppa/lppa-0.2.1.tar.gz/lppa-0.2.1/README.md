# lppa

Command line tool to create Launchpad PPAs and push deb source packages to them

## Installation

```
pip install lppa
```

## Usage

lppa ships an `lppa` command line application to interact with Launchpad PPAs.
Run

```
lppa --help
```

for additional information.

### Create a new PPA

To create a new PPA, run

```
lppa create PPA_NAME [all|arch, ...]
```

where arch is a Launchpad processor (you can pass multiple architectures here)
or `all` to enable all available architectures.

The currently available Launchpad processors are

- amd64
- arm64
- s390x
- ppc64el
- armhf
- armel
- i386
- powerpc

### Delete an existing PPA

```
lppa delete PPA_NAME
```

### List user's PPAs

```
lppa list
```

This will print a list with the names of the user's available PPAs

### Fetch PPA information

Often, you may want to retrieve an URL for a PPA packages page or quickly fetch
a dput command to upload packages to a PPA. That can be achieved through the
`info` command.

```
lppa info PPA_NAME
```

Moreover, passing the `-v` option to the info command will also display the
architectures for which the PPA can build packages.

## Development

Run `make devel` to set the development environment up (a python virtual
environment is recommended).

Run `make check` to run the test suite and ensure the development environment
is up to date.

You can use `make coverage` to ensure code coverage is not drastically reduced
by new changes (if proposing changes, try to write some tests for them).

For instance, a complete bootstrap script would look like:

```
# apt install -y python3-virtualenv python3-virtualenvwrapper
$ mkvirtualenv lppa
$ workon lppa
$ make devel
$ make check
```

### Releasing

- Change `lppa/__init__.py` to set the version to be published
- Create a new git tag for the new version
- Run `make publish` to build a new version and push it to PyPI
- Change `lppa/__init__.py` to set the version to the next development version
