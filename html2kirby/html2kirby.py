import logging
from html import unescape
from html.parser import HTMLParser

__all__ = ["HTML2Kirby"]


class StackEntry:
    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = attrs
        self.data = ''

    def add_data(self, data):
        self.data += data


class TagStack(list):
    def push(self, tag, attrs):
        """Record a tag

        We're in some sort of state, meaning that we're inside a tag.
        An example for that is the <a> tag, which we can only
        write after encountering the end tag, since the link text
        is inbetween
        """
        self.append(StackEntry(tag=tag, attrs=dict(attrs)))

    def add_data(self, data):
        """Add data to the current state we're in"""
        last = self.peek()
        last.data += data

    def peek(self):
        """Have a look at the current state without removing it"""
        return self[-1]

    def pop(self):
        return super().pop()

    def is_empty(self):
        return len(self) == 0


class HTML2Kirby(HTMLParser):
    tag_map = {
        'b': 'strong',
        'strong': 'strong',
        'h1': 'heading',
        'h2': 'heading',
        'h3': 'heading',
        'h4': 'heading',
        'h5': 'heading',
        'h6': 'heading',
        'img': 'img',
        'br': 'br',
        'i': 'emph',
        'em': 'emph',
        'p': 'p',
        'a': 'a',
        'ul': 'list',
        'ol': 'list',
        'li': 'li',
        'code': 'pre',
        'pre': 'pre',
        'blockquote': 'quote',
        'hr': 'hr'
    }

    keep_tags = [
        'strike',
        'u',
        'abbr',
        'del',
    ]

    passthrough_tags = (
        'svg',
        'table'
    )

    _passthrough_levels = 0
    """Passthrough mode is triggered by self.passthrough_tags and
    will directly output this tag and all children instead of converting them
    to kirbytext
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kirbytext = ""
        self.start_tag_handlers = [t for t in dir(self)
                                   if t.startswith("process_start_")]

        self.end_tag_handlers = [t for t in dir(self)
                                 if t.startswith("process_start_")]
        self.log = logging.getLogger()

        self.tag_stack = TagStack()

    def _reset(self):
        self.__init__()

    @property
    def is_passthrough(self):
        """Whether we're in a passthrough mode"""
        return self._passthrough_levels > 0

    def enable_passthrough_mode(self):
        """Enable passthrough mode

        Enable passthrough mode by counting the levels one up. This enables the
        passthrough tags to be nested
        """
        self._passthrough_levels += 1

    def disable_passthrough_mode(self):
        """Disable passthrough mode"""
        self._passthrough_levels -= 1

    def handle_starttag(self, tag, attrs):
        """Handle the starttag

        See what category the tag is in, if it's a passthrough one, one to
        be kept or one to be converted. Call the corresponding function.
        """
        if tag in self.passthrough_tags:
            # This is a passhtrough tag, start the passthrough,
            self.enable_passthrough_mode()
            self.o(self.tag_to_html(tag, attrs))

        elif self.is_passthrough:
            # We're in passthrough but this is not the tag that started it
            # Just output the tag
            self.o(self.tag_to_html(tag, attrs))

        elif tag in self.tag_map:
            # Normal tag that we'll rewrite
            processor = self.tag_map[tag]
            processor_func = "process_start_{}".format(processor)
            getattr(self, processor_func)(tag, attrs)

        elif tag in self.keep_tags:
            # Tag that we keep as is
            self.keep_start_tag(tag, attrs)

        else:
            # Tag that we ignore
            print("Ignored tag {} with attrs {}".format(
                tag, ",".join(["{}: {}".format(*a) for a in attrs])
            ))

    def handle_endtag(self, tag):
        """Handle the starttag

        See what category the tag is in, if it's a passthrough one, one to
        be kept or one to be converted. Call the corresponding function.
        """
        if self.is_passthrough and tag in self.passthrough_tags:
            # We're in passthrough mode and this tag started it, so
            # we disable the passthrough mode
            self.o(self.end_tag_to_html(tag))
            self.disable_passthrough_mode()

        elif self.is_passthrough:
            # We're in passthrough mode, write the tag directly
            self.o(self.end_tag_to_html(tag))

        elif tag in self.tag_map:
            # Normal tag that is converted
            processor = self.tag_map[tag]
            processor_func = "process_end_{}".format(processor)
            if hasattr(self, processor_func):
                getattr(self, processor_func)(tag)

        elif tag in self.keep_tags:
            # Tags that we keep as is
            self.keep_end_tag(tag)

    def handle_data(self, data):
        """Handle data

        If it's just whitespace data, discard it.
        If we're just plain rewriting, append the data to the result.
        If we have some sort of state, append the data to that state.
        """
        if self.is_passthrough:
            self.o(data)
            return

        if len(data.strip()) == 0:
            return

        data = data.replace("’", "'")
        data = data.replace("`", "'")

        data = unescape(data)

        # those need to be replaced, as ` means code block in kirby

        if self.tag_stack.is_empty():
            self.o(data)
        else:
            if self.tag_stack.peek().tag == 'li':
                # a bit of black magic here:
                # We don't want newlines in the resulting line, but we can't
                # just use .strip() because we want to preserve white spaces
                # when no newline is involved
                data = "".join([d for d in data.split("\n") if len(d.strip())])
            self.tag_stack.add_data(data)

    def tag_pad(self):
        """Pad a tag

        Put whitespace around tags, but not at the beginning of the
        string or line. This is necessary with some tags as _
        """
        if not self.tag_stack.is_empty():
            last = self.tag_stack.peek()

            if not last.data.endswith(' '):
                last.data += ' '
        else:
            if self.kirbytext == '' or self.kirbytext[-1] == "\n":
                return

            if not self.kirbytext.endswith(' '):
                self.o(' ')

    def tag_start_of_line(self):
        """Make sure the tag is at the begininig of a line"""

        if len(self.kirbytext):
            if self.kirbytext[-1] != "\n":
                self.o("\n")

    def p(self):
        """Create blank lines

        Create blank lines, but only if they don't exist. This makes sure that
        in the right places, there are two new lines
        """
        if self.tag_stack.is_empty():
            if not self.kirbytext.endswith("\n\n"):
                if self.kirbytext.endswith("\n"):
                    self.kirbytext += "\n"
                else:
                    self.kirbytext += "\n\n"
        else:
            last = self.tag_stack.peek()
            if not last.data.endswith("\n\n"):
                if last.data.endswith("\n"):
                    last.data += "\n"
                else:
                    last.data += "\n\n"

    def o(self, data):
        """Append data to the result or state

        Append the data to the result if we're plainly rewriting, else
        append it to the current state
        """
        if self.tag_stack.is_empty():
            if self.kirbytext.endswith(' ') and data.startswith(' '):
                data = data.lstrip()
            self.kirbytext += data
        else:
            self.tag_stack.add_data(data)

    def tag_to_html(self, tag, attrs):
        """Convert tag and attr data back to html

        This is used for keeping tags or even passthrough mode
        """
        attrs = ['{}="{}"'.format(*a) for a in attrs]
        attr_str = " " + " ".join(attrs) if len(attrs) else ""
        fmt = "<{tag}{attrs}>".format(tag=tag, attrs=attr_str)

        return fmt

    def end_tag_to_html(self, tag):
        """Format an end tag (</TAGNAME>)"""
        return "</{}>".format(tag)

    def keep_start_tag(self, tag, attrs):
        fmt = self.tag_to_html(tag, attrs)
        self.o(fmt)

    def keep_end_tag(self, tag):
        self.o(self.end_tag_to_html(tag))

    def br(self):
        """Newlines!"""
        self.p()

    def process_start_br(self, tag, attrs):
        self.br()

    def process_start_img(self, tag, attrs):
        attrs = dict(attrs)

        link = ""
        alt = ""
        if not self.tag_stack.is_empty() and self.tag_stack.peek().tag == 'a':
            # we're in a link. Remove that and append the src in the image tag
            link_state = self.tag_stack.pop()
            href = link_state.attrs.get('href', '')

            link = " link: " + href

        if 'alt' in attrs:
            alt = " alt: " + attrs['alt']

        img = "(image: {src}{alt}{link})".format(
            src=attrs.get('src', ''),
            alt=alt,
            link=link
        )
        self.o(img)

    def process_start_heading(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_heading(self, tag):
        state = self.tag_stack.pop()

        tag = state.tag
        data = state.data.strip()

        nr = int("".join(c for c in tag if c.isdigit()))
        self.tag_start_of_line()
        self.o("#" * nr)
        self.o(" ")
        self.o(data)
        self.p()

    def process_start_strong(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_strong(self, tag):
        """Convert strong tags (strong, b)

        Print strong tags as is, except if they contain newlines. If they
        contain newlines, print each line surrounded by ** tags.
        Strip newlines at the beginning or the end, like <b>abc\n</b>
        """
        state = self.tag_stack.pop()
        data = state.data

        lines = [line for line in data.split('\n') if line != '']

        for key, line in enumerate(lines):
            self.tag_pad()
            self.o('**')
            self.o(line.strip('\n'))
            self.o('**')
            self.tag_pad()

            # avoid adding a newline afterwards if this is the last line
            if key < len(lines) - 1:
                self.o("\n")

    def process_start_emph(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_emph(self, tag):
        """Convert emphasis tags (em, i)

        Print emph tags as is, except if they contain newlines. If they
        contain newlines, print each line surrounded by _ tags.
        Strip newlines at the beginning or the end, like <i>abc\n</i>
        """
        state = self.tag_stack.pop()
        data = state.data

        lines = [line for line in data.split('\n') if line != '']

        for key, line in enumerate(lines):
            self.tag_pad()
            self.o('_')
            self.o(line.strip('\n'))
            self.o('_')

            # avoid adding a newline afterwards if this is the last line
            if key < len(lines) - 1:
                self.o("\n")

    def process_start_p(self, tag, attrs):
        self.p()

    def process_end_p(self, tag):
        self.p()

    def process_start_a(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_a(self, tag):
        if self.tag_stack.is_empty() or self.tag_stack.peek().tag != 'a':
            # link was removed. Probably because it's an image link
            return

        state = self.tag_stack.pop()

        href = state.attrs.get('href', '')

        title = (" title: " + state.attrs['title']
                 if 'title' in state.attrs else "")
        text = "text: " + state.data.strip()

        link = "(link: {href}{title} {text})".format(
            href=href, title=title, text=text
        )

        self.tag_pad()
        self.o(link)

    def process_start_list(self, tag, attrs):
        nest_level = len([s for s in self.tag_stack if s.tag == 'ul'])

        attrs.append(('nest_level', nest_level))
        self.tag_stack.push(tag, attrs)

    def process_end_list(self, tag):
        state = self.tag_stack.pop()

        nest_level = state.attrs['nest_level']
        indent = " " * 4 * nest_level

        if nest_level == 0:
            self.p()
        else:
            self.o("\n")

        for line in state.data.split("\n"):
            self.o(indent + line + "\n")

    def process_start_li(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_li(self, tag):
        state = self.tag_stack.pop()

        sign = '*' if self.tag_stack.peek().tag == 'ul' else '1.'

        self.o(sign + " " + state.data.strip())
        self.o("\n")

    def process_start_pre(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_pre(self, tag):
        state = self.tag_stack.pop()

        def print_data(data):
            self.o(state.data.rstrip().strip('\n'))

        if (not self.tag_stack.is_empty()
                and self.tag_stack.peek().tag == 'pre'):
            # seems like we're in a <pre><code> state here (or <pre><pre>)
            # Therefore, we don't add another tag
            print_data(state.data)

        elif tag == 'pre' or len(state.data.split("\n")) > 1:
            # Either multiline code or <pre> code
            # We always want triple backticks for <pre> code
            self.p()
            self.o('```\n')
            print_data(state.data)
            self.o('\n```')
            self.p()

        else:
            self.o("`{}`".format(state.data.strip()))

    def process_start_quote(self, tag, attrs):
        self.tag_stack.push(tag, attrs)

    def process_end_quote(self, tag):
        self.p()
        state = self.tag_stack.pop()
        data = state.data.strip()

        for line in data.split("\n"):
            self.o("> " + line.strip() + "\n")

        self.p()

    def process_start_hr(self, tag, attrs):
        self.p()
        self.o("***")
        self.p()
