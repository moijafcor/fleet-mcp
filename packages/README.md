# packages/

Third-party package adapters for this project.

Each subdirectory is a governance bridge between
a third-party package and harnessable conventions.
The package lives where installed. The adapter lives here.

## Discovery

  ls packages/*/PACKAGE.md       # installed adapters
  ls packages/*/skills/*.md      # available commands

## Installing a package adapter

Run install.sh --update after adding the adapter
to the harnessable framework source, or manually
copy from framework/packages/{name}/.

See framework/packages/README.md for the convention.
