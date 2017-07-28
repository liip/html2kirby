import pytest


def test_img(formatter):
    formatter.feed('<img src="foo.jpg" alt="foobar" />')

    assert formatter.markdown == "(image: foo.jpg alt: foobar)"

    formatter._reset()
    formatter.feed('<img src="foo.jpg">')

    assert formatter.markdown == "(image: foo.jpg)"


@pytest.mark.parametrize("html,md", [
    ('h1', '#'), ('h2', '##'), ('h3', '###'),
    ('h4', '####'), ('h5', '#####'), ('h6', '######'),
])
def test_headings(formatter, html, md):
    formatter.feed('<{tag}>Heading uno</{tag}>'.format(tag=html))

    assert formatter.markdown == "{} Heading uno\n\n".format(md)


def test_strong(formatter):
    formatter.feed("<b>lala</b>")
    assert formatter.markdown == "**lala** "

    formatter._reset()
    formatter.feed("<strong>lala</strong>")
    assert formatter.markdown == "**lala** "

    formatter._reset()
    formatter.feed("<strong>lala</strong>something coming right after")
    assert formatter.markdown == "**lala** something coming right after"


def test_italic(formatter):
    formatter.feed("<i>lala</i>")
    assert formatter.markdown == "_lala_ "

    formatter._reset()
    formatter.feed("<em>lala</em>")
    assert formatter.markdown == "_lala_ "

    formatter._reset()
    formatter.feed("<em>lala</em>something coming right after")
    assert formatter.markdown == "_lala_ something coming right after"


def test_paragraph(formatter):
    formatter.feed("<p>some paragraph</p>")

    assert formatter.markdown == "\n\nsome paragraph\n\n"


def test_link(formatter):
    formatter.feed("""<a href="http://www.google.ch" title="Alternative">
    Google</a>""")

    res = "(link: http://www.google.ch title: Alternative text: Google)"
    assert formatter.markdown == res

    formatter._reset()
    formatter.feed("""<a href="http://www.google.ch">Google</a>""")

    res = "(link: http://www.google.ch text: Google)"
    assert formatter.markdown == res


def test_bold_link(formatter):
    formatter.feed("""<a href="foo"><b>bar</b></a>""")

    assert formatter.markdown == "(link: foo text: **bar**)"

    formatter._reset()
    formatter.feed("""<b><a href="foo">bar</a></b>""")

    assert formatter.markdown == "** (link: foo text: bar)** "


def test_list(formatter):
    formatter.feed("""
        <ul>
            <li>First item</li>
            <li>Second item</li>
        </ul>
    """)

    exp = "* First item\n* Second item"
    assert exp == formatter.markdown.strip()


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

    assert exp == formatter.markdown.strip()


def test_complicated_lists(formatter):
    formatter.feed("""
        <ul>
            <li>First <b>Item bold</b></li>
            <li>Second item has a <a href="">Link</a></li>
        </ul>""")

    exp = """* First **Item bold**
* Second item has a (link:  text: Link)"""

    assert exp == formatter.markdown.strip()


def test_ordered_list(formatter):
    formatter.feed("""
        <ul>
            <ol>First item</ol>
            <ol>Second item</ol>
        </ul>
    """)

    exp = "1. First item\n1. Second item"
    assert exp == formatter.markdown.strip()
