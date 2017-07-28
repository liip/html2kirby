import logging

from html.parser import HTMLParser

__all__ = ['HTML2Kirby']

class HTML2Kirby(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.markdown = ""
        self.start_tag_handlers = [t for t in dir(self)
                                   if t.startswith("process_start_")]

        self.end_tag_handlers = [t for t in dir(self)
                                 if t.startswith("process_start_")]
        self.log = logging.getLogger()

        self.states = []

        self.tag_map = {
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
            'a': 'a'
        }

    def _reset(self):
        self.__init__()

    def handle_starttag(self, tag, attrs):
        """Handle the starttag

        See if we have a handler for given tag. If so, call it's start
        function
        """
        if tag in self.tag_map:
            processor = self.tag_map[tag]
            processor_func = "process_start_{}".format(processor)
            getattr(self, processor_func)(tag, attrs)

    def handle_endtag(self, tag):
        """Handle the starttag

        See if we have a handler for given tag. If so, call it's end
        function
        """
        if tag in self.tag_map:
            processor = self.tag_map[tag]
            processor_func = "process_end_{}".format(processor)
            if hasattr(self, processor_func):
                getattr(self, processor_func)(tag)

    def handle_data(self, data):
        """Handle data

        If we're just plain rewriting, append the data to the result.
        If we have some sort of state, append the data to that state.
        """
        if len(self.states) == 0:
            self.o(data)
        else:
            self.state_add_data(data)

    def tag_pad(self):
        """Pad a tag

        Put whitespace around tags, but not at the beginning of the
        string or line. This is necessary with some tags as _
        """
        if self.markdown == '' or self.markdown[-1] == "\n":
            return

        if not self.markdown.endswith(' '):
            self.o(' ')

    def state_start(self, tag, attrs):
        """Record a state

        We're in some sort of state, push that to the stack.
        An example for that is the <a> tag, which we can only
        write after encountering the end tag, since the link text
        is inbetween
        """
        self.states.append({
            'tag': tag,
            'attrs': dict(attrs),
            'data': ''
        })

    def state_add_data(self, data):
        """Add data to the current state we're in"""
        last = self.states[-1]
        last['data'] += data

    def state_end(self):
        """End a state

        This means that the end tag has been encountered
        """
        return self.states.pop()

    def o(self, data):
        """Append data to the result or state

        Append the data to the result if we're plainly rewriting, else
        append it to the current state
        """
        if len(self.states) == 0:
            self.markdown += data
        else:
            self.state_add_data(data)

    def br(self):
        """Newlines!"""
        self.o("\n\n")

    def process_start_br(self, tag, attrs):
        self.br()

    def process_start_img(self, tag, attrs):
        attrs = dict(attrs)

        if 'alt' not in attrs:
            img = "(image: {src})".format(
                src=attrs.get('src', '')
            )
            self.o(img)
            return

        img = "(image: {src} alt: {alt})".format(
            src=attrs.get('src', ''),
            alt=attrs.get('alt', '')
        )
        self.o(img)

    def process_start_heading(self, tag, attrs):
        nr = int("".join(c for c in tag if c.isdigit()))
        self.o("#" * nr)
        self.o(" ")

    def process_end_heading(self, tag):
        self.br()

    def process_start_strong(self, tag, attrs):
        self.tag_pad()
        self.o('**')

    def process_end_strong(self, tag):
        self.o('**')
        self.tag_pad()

    def process_start_emph(self, tag, attrs):
        self.tag_pad()
        self.o('_')

    def process_end_emph(self, tag):
        self.o('_')
        self.tag_pad()

    def process_start_p(self, tag, attrs):
        self.o("\n\n")

    def process_end_p(self, tag):
        self.o("\n\n")

    def process_start_a(self, tag, attrs):
        self.state_start(tag, attrs)

    def process_end_a(self, tag):
        state = self.state_end()

        href = state['attrs'].get('href', '')

        title = (" title: " + state['attrs']['title']
                 if 'title' in state['attrs'] else "")
        text = "text: " + state['data'].strip()

        link = "(link: {href}{title} {text})".format(
            href=href, title=title, text=text
        )

        self.o(link)
