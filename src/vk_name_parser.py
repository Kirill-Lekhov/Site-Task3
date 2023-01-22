from html.parser import HTMLParser


class VKNameParser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.name = ""
        self.handling = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'h2':
            for name, value in attrs:
                if name == 'class' and value == 'op_header':
                    self.handling = True
                    break

    def handle_endtag(self, tag: str) -> None:
        if tag == 'h2' and self.handling:
            self.handling = False

    def handle_data(self, data):
        if self.handling:
            self.name = data
