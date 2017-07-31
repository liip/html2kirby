# HTML2Kirby

[![Build Status](https://travis-ci.org/liip/html2kirby.svg?branch=master)](https://travis-ci.org/liip/html2kirby)

This is a html to [Kirbytext](https://getkirby.com/docs/content/text#links) 
converter for python.

It is currently in heavy development.


## Installation

TBD

## Usage

To use this package, simply import the package and feed it some html:

```
from html2kirby import HTML2Kirby

formatter = HTML2Kirby()
formatter.feed("""<img src="https://placekitten.com/200/300" alt="kittens are cute" />""")
```

You can then access the result via `.kirbytext` attribute:

```
print(formatter.kirbytext)
# prints (image: https://placekitten.com/200/300 alt: kittesn are cute)
```

## Testing

Make sure you have Pytest installed (`pip install pytest`). Then just
invoke it:

```
pytest
```

## Supported Markup

As of now, following tags are supported:

* Simple formatting (`<b>`, `<strong>`, `<i>`, `<em>`)
* Headings (`<h1>`, `<h2>`, ...)
* Images (`<img>`)
* line breaks (`<br>`)
* Paragraphs (`<p>`)
* Blocks (`<pre>`)
* Links (`<a>`)
