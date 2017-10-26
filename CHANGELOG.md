# Changelog

## Version 0.2

### Added

* Handling of SVG blocks
* Handling of `<pre><code>` blocks

### Fixed

* Handling of newlines in `<em>`/`<i>` and `<strong>`/`<b>` tags
* Make sure headings are always at the beginning of a line
* Linked images that were inside a formatting tag
* Better handling of whitespace in `<li>` elements
* Content in `<table>` is now preserved and not converted, since kirby doesn't interpret it

### Notes

* Code is now style enforced with flake8
* Added editorconfig


## Version 0.1-1

Make sure the package is installable in pip
