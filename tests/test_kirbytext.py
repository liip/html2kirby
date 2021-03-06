import pytest
import sys


def test_img(formatter):
    formatter.feed('<img src="foo.jpg" alt="foobar" />')

    assert formatter.kirbytext == "(image: foo.jpg alt: foobar)"

    formatter._reset()
    formatter.feed('<img src="foo.jpg">')

    assert formatter.kirbytext == "(image: foo.jpg)"


def test_linked_image(formatter):
    formatter.feed('<a href="http://liip.com"><img src="liiplogo.jpg"></a>')

    exp = "(image: liiplogo.jpg link: http://liip.com)"

    assert formatter.kirbytext == exp


def test_wrapped_linked_image(formatter):
    formatter.feed('<strong><a href="http://liip.com"><img src="liiplogo.jpg"></a></strong>')  # noqa: E501

    exp = "**(image: liiplogo.jpg link: http://liip.com)**"

    assert formatter.kirbytext.strip() == exp.strip()


@pytest.mark.parametrize("html,md", [
    ('h1', '#'), ('h2', '##'), ('h3', '###'),
    ('h4', '####'), ('h5', '#####'), ('h6', '######'),
])
def test_headings(formatter, html, md):
    formatter.feed('<{tag}>Heading uno</{tag}>'.format(tag=html))

    assert formatter.kirbytext == "{} Heading uno\n\n".format(md)


def test_headings_begining_of_line(formatter):
    """Make sure the heading is on a new line"""
    formatter.feed('<strong>strong</strong><h1>Heading</h1>')

    assert formatter.kirbytext.strip() == "**strong** \n# Heading"


def test_strong(formatter):
    formatter.feed("<b>lala</b>")
    assert formatter.kirbytext == "**lala** "

    formatter._reset()
    formatter.feed("<strong>lala</strong>")
    assert formatter.kirbytext == "**lala** "

    formatter._reset()
    formatter.feed("<strong>lala</strong>something coming right after")
    assert formatter.kirbytext == "**lala** something coming right after"


@pytest.mark.xfail(reason="Problem with _ followed by text")
def test_italic(formatter):
    formatter.feed("<i>lala</i>")
    assert formatter.kirbytext == "_lala_"

    formatter._reset()
    formatter.feed("<em>lala</em>")
    assert formatter.kirbytext == "_lala_"

    formatter._reset()
    formatter.feed("<em>lala</em>something coming right after")
    assert formatter.kirbytext == "_lala_ something coming right after"


def test_paragraph(formatter):
    formatter.feed("<p>some paragraph</p>")

    assert formatter.kirbytext == "\n\nsome paragraph\n\n"


def test_link(formatter):
    formatter.feed("""<a href="http://www.google.ch" title="Alternative">
    Google</a>""")

    res = "(link: http://www.google.ch title: Alternative text: Google)"
    assert formatter.kirbytext == res

    formatter._reset()
    formatter.feed("""<a href="http://www.google.ch">Google</a>""")

    res = "(link: http://www.google.ch text: Google)"
    assert formatter.kirbytext == res


def test_bold_link(formatter):
    formatter.feed("""<a href="foo"><b>bar</b></a>""")

    assert formatter.kirbytext == "(link: foo text: **bar**)"

    formatter._reset()
    formatter.feed("""<b><a href="foo">bar</a></b>""")

    assert formatter.kirbytext == "** (link: foo text: bar)** "


def test_list(formatter):
    formatter.feed("""
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
    """)

    exp = "* First item\n* Second item"
    assert exp == formatter.kirbytext.strip()


def test_nested_lists(formatter):
    formatter.feed("""
        <ul>
            <li>First item
                <ul>
                    <li>Child item</li>
                    <li>Second child item</li>
                </ul>
            </li>
            <li>Second item</li>
        </ul>
    """)

    exp = """* First item
    * Child item
    * Second child item
* Second item"""

    assert exp == formatter.kirbytext.strip()


def test_complicated_lists(formatter):
    formatter.feed("""
        <ul>
            <li>First <b>Item bold</b></li>
            <li>Second item has a <a href="">Link</a></li>
        </ul>""")

    exp = """* First **Item bold**
* Second item has a (link:  text: Link)"""

    assert exp == formatter.kirbytext.strip()


def test_ordered_list(formatter):
    formatter.feed("""
        <ol>
            <li>First item</li>
            <li>Second item</li>
        </ol>
    """)

    exp = "1. First item\n1. Second item"
    assert exp == formatter.kirbytext.strip()


def test_blocks(formatter):
    """TODO: improve this test with the newlines
    """
    formatter.feed("""
        <pre>
            from winterfell import jon

            assert jon.knows == "nothing"
        </pre>
    """)

    exp = """


```
            from winterfell import jon

            assert jon.knows == "nothing"
```

"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_code(formatter):
    formatter.feed("""<code>git blame</code>""")

    exp = "`git blame`"

    assert exp == formatter.kirbytext


def test_quotes(formatter):
    formatter.feed("""
    <blockquote>
        Welcome. Welcome to City 17.
        You have chosen or been chosen to relocate into one of our
        finest remaining urban centres
    </blockquote>
    """)

    exp = """> Welcome. Welcome to City 17.
> You have chosen or been chosen to relocate into one of our
> finest remaining urban centres

"""

    assert exp == formatter.kirbytext


def test_keep_strike(formatter):
    code = """<strike>fu</strike>"""
    formatter.feed(code)

    assert code == formatter.kirbytext


@pytest.mark.skipif(sys.version_info < (3, 5),
                    reason="Only works in 3.5 upwards")
def test_unescape(formatter):
    formatter.feed("GottaGo &#8211; iPhone bring me home")

    exp = "GottaGo – iPhone bring me home"
    assert exp == formatter.kirbytext


def test_apostrophe(formatter):
    text = "I'm `proud' to present one of the first swiss-made native iPhone applications, called `<strong>GottaGo</strong>'"  # noqa: E501

    formatter.feed(text)

    exp = "I'm 'proud' to present one of the first swiss-made native iPhone applications, called ' **GottaGo** '"  # noqa: E501

    assert exp == formatter.kirbytext


def test_horizontal_ruler(formatter):
    formatter.feed("<hr>")

    exp = "\n\n***\n\n"

    assert exp == formatter.kirbytext


def test_code_enclosed_svg(formatter):
    formatter.feed("<code><svg></svg></code>")

    exp = "`<svg></svg>`"

    assert exp == formatter.kirbytext


def test_code_enclosed_svg_attrs(formatter):
    formatter.feed("""<code><svg preserveaspectratio="xMinYmin" version="1.1"></svg></code>""")  # noqa: E501

    exp = """`<svg preserveaspectratio="xMinYmin" version="1.1"></svg>`"""

    assert exp == formatter.kirbytext


def test_pre_block_no_single_line(formatter):
    """Pre blocks must not be converted to one-liners, even if
    they are in the source"""

    formatter.feed("""<pre>foo bar</pre>""")

    exp = """
```
foo bar
```
        """

    assert exp.strip() == formatter.kirbytext.strip()


def test_pre_code_block(formatter):
    """Test that <pre><code> blocks only convert to one back tick triple"""

    formatter.feed("""<pre><code>pip install html2kirby</code></pre>""")

    exp = """
```
pip install html2kirby
```
    """

    assert exp.strip() == formatter.kirbytext.strip()


def test_useless_newlines_in_strong(formatter):
    """Test the case when a <strong> tag ends with a <br /> tag
    which is totally useless
    """

    formatter.feed("""<strong>This is not 'Nam. This is bowling. There are rules<br/></strong>""")  # noqa: E501

    exp = """**This is not 'Nam. This is bowling. There are rules**"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_ok_newlines_in_strong(formatter):
    """Test the case where there actually are senseful newlines in strong"""

    formatter.feed("""<strong>This is not 'Nam. This is bowling.<br />
There are rules<br/></strong>""")

    # ** tags are padded with whitespace, which is why we add it here
    exp = """**This is not 'Nam. This is bowling.**\u0020
**There are rules**"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_ok_newlines_in_strong2(formatter):
    """Test the case where there actually are senseful newlines in strong"""

    formatter.feed("""<strong>This is not 'Nam. This is bowling.<br />
There are rules<br/></strong> Text goes on""")

    # ** tags are padded with whitespace, which is why we add it here
    exp = """**This is not 'Nam. This is bowling.**\u0020
**There are rules** Text goes on"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_useless_newlines_in_em(formatter):
    """Test the case when a <em> tag ends with a <br /> tag
    which is totally useless
    """

    formatter.feed("""<em>This is not 'Nam. This is bowling. There are rules<br/></em>""")  # noqa: E501

    exp = """_This is not 'Nam. This is bowling. There are rules_"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_ok_newlines_in_em(formatter):
    """Test the case where there actually are senseful newlines in em"""

    formatter.feed("""<em>This is not 'Nam. This is bowling.<br />
There are rules<br/></em>""")

    # _ tags are padded with whitespace, which is why we add it here
    exp = """_This is not 'Nam. This is bowling._
_There are rules_"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_ok_newlines_in_em2(formatter):
    """Test the case where there actually are senseful newlines in em"""

    formatter.feed("""<em>This is not 'Nam. This is bowling.<br />
There are rules<br/></em> Text goes on""")

    # _ tags are padded with whitespace, which is why we add it here
    exp = """_This is not 'Nam. This is bowling._
_There are rules_ Text goes on"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_whitespace_after_link(formatter):
    """Test that whitespace after a link is preserved"""

    formatter.feed("""A <a href="#">link</a> helps to navigate""")

    exp = """A (link: # text: link) helps to navigate"""

    assert exp.strip() == formatter.kirbytext.strip()


def test_whitespace_after_link_in_list(formatter):
    str = """<ul><li>We do some async compression of images with <a href="https://github.com
/google/zopfli">zopflipng</a>, <a href="https://pngquant.org/">pngquant</a> and <a href="https://github.com/mozilla/mozjpeg">mozjpeg</a> to make the images even smaller bytewise.</li></ul>
"""  # noqa: E501

    formatter.feed(str)

    exp = """* We do some async compression of images with (link: https://github.com
/google/zopfli text: zopflipng), (link: https://pngquant.org/ text: pngquant) and
(link: https://github.com/mozilla/mozjpeg text: mozjpeg) to make the images even smaller bytewise."""  # noqa: E501

    assert exp.strip().replace("\n", " ") == (
        formatter.kirbytext.strip().replace("\n", " "))


def test_passthrough_with_mapped_tags(formatter):
    _str = """<table><tr><td><strong>fette sache</strong></td></tr></table>"""

    formatter.feed(_str)

    assert _str == formatter.kirbytext


def test_passthrough_with_mapped_tags_ending(formatter):
    _str = """<table><tr><td><strong>fette sache</strong></td></tr></table>
<strong>Fettere Sache</strong>"""

    formatter.feed(_str)

    exp = """<table><tr><td><strong>fette sache</strong></td></tr></table> **Fettere Sache**"""   # noqa: E501

    assert exp.strip() == formatter.kirbytext.strip()


def test_nested_passthrouh(formatter):
    _str = """<table><tr><td><table><tr><td></td></tr></table></td></tr></table>"""  # noqa: E501

    formatter.feed(_str)

    assert _str == formatter.kirbytext
