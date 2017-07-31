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


@pytest.mark.parametrize("html,md", [
    ('h1', '#'), ('h2', '##'), ('h3', '###'),
    ('h4', '####'), ('h5', '#####'), ('h6', '######'),
])
def test_headings(formatter, html, md):
    formatter.feed('<{tag}>Heading uno</{tag}>'.format(tag=html))

    assert formatter.kirbytext == "{} Heading uno\n\n".format(md)


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


@pytest.mark.skipif(sys.version_info < (3,5),
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
