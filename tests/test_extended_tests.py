import pytest
import glob
import os

from html2kirby import HTML2Kirby

files = []

path = os.path.dirname(os.path.abspath(__file__))

extended_tests_path = os.path.join(path, "extended_tests/*.html")

for f in glob.glob(extended_tests_path):
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

    assert formatter.kirbytext.strip() == expected_result.strip()
