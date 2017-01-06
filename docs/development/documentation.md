# Documentation

The documentation for Alliance Auth uses [Sphinx](http://www.sphinx-doc.org/) to build documentation. When a new commit
 to specific branches is made (master, primarily), the repository is automatically pulled, docs built and deployed on
 [readthedocs.org](https://readthedocs.org/).


Documentation was migrated from the Github wiki pages and into the repository to allow documentation changes to be
included with pull requests. This means that documentation can be guaranteed to be updated when a pull request is
accepted rather than hoping documentation is updated afterwards or relying on maintainers to do the work. It also
allows for documentation to be maintained at different versions more easily.

## Building Documentation
If you're developing new documentation, its likely you'll want or need to test build it before committing to your
branch. To achieve this you can use Sphinx to build the documentation locally as it appears on Read the Docs.

Activate your virtual environment (if you're using one) and install the documentation requirements found in
`docs/requirements.txt` using pip, e.g. `pip install -r docs/requirements.txt`.

You can then build the docs by changing to the `docs/` directory and running `make html` or `make dirhtml`, depending
on how the Read the Docs project is configured. Either should work fine for testing. You can now find the output of the
build in the `/docs/_build/` directory.

Occasionally you may need to fully rebuild the documents by running `make clean` first, usually when you add or
rearrange toctrees.


## Documentation Format

CommonMark Markdown is the current preferred format, via [recommonmark](https://github.com/rtfd/recommonmark).
reStructuredText is supported if required, or you can execute snippets of reST inside Markdown by using a code block:

    ```eval_rst
    reStructuredText here
    ```

Markdown is used elsewhere on Github so it provides the most portability of documentation from Issues and Pull Requests
as well as providing an easier initial migration path from the Github wiki.
