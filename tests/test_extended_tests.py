import pytest
import glob

from html2kirby import HTML2Kirby

files = []

for f in glob.glob("extended_tests/*.html"):
    html = f
    txt = f.replace(".html", ".txt")

    files.append((html, txt))


@pytest.mark.parametrize("html,kirby", files)
def test_file(html, kirby):
    formatter = HTML2Kirby()

    with open(html, 'r') as html_file:
        formatter.feed(html_file.read())

    with open(kirby, 'r') as kirby_file:
        expected_result = kirby_file.read()

    assert formatter.markdown.strip() == expected_result.strip()
