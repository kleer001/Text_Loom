import urwid

class SplitPane(urwid.WidgetWrap):
    def __init__(self, *widgets):
        self.widgets = list(widgets)
        self.selected = 0
        self._update_widget()
        super().__init__(self.widget)

    def _update_widget(self):
        self.widget = urwid.Pile(
            [urwid.AttrWrap(widget, 'body') for widget in self.widgets]
        )

    def resize_pane(self, delta):
        if len(self.widgets) > 1:
            if 0 < self.selected < len(self.widgets) - 1:
                self._resize_selected(delta)
            elif self.selected == 0:
                self._resize_first(delta)
            else:
                self._resize_last(delta)
            self._update_widget()

    def _resize_selected(self, delta):
        if self.widgets[self.selected].body.size[0] + delta > 0:
            self.widgets[self.selected].body.size = (
                self.widgets[self.selected].body.size[0] + delta,
            )
            self.widgets[self.selected + 1].body.size = (
                self.widgets[self.selected + 1].body.size[0] - delta,
            )

    def _resize_first(self, delta):
        if self.widgets[0].body.size[0] + delta > 0:
            self.widgets[0].body.size = (self.widgets[0].body.size[0] + delta,)
            self.widgets[1].body.size = (self.widgets[1].body.size[0] - delta,)

    def _resize_last(self, delta):
        if self.widgets[-1].body.size[0] + delta > 0:
            self.widgets[-1].body.size = (self.widgets[-1].body.size[0] + delta,)
            self.widgets[-2].body.size = (self.widgets[-2].body.size[0] - delta,)

    def switch_pane(self, direction):
        self.selected = (self.selected - 1) % len(self.widgets) if direction == 'up' else (self.selected + 1) % len(self.widgets)
        self._update_widget()


class MainLoop:
    def __init__(self):
        self.edit1 = urwid.Edit("Editor 1\n")
        self.edit2 = urwid.Edit("Editor 2\n")
        self.split_pane = SplitPane(self.edit1, self.edit2)
        self.main_widget = urwid.Frame(self.split_pane)
        self.loop = urwid.MainLoop(self.main_widget, unhandled_input=self.handle_input)

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key in ('up', 'down'):
            self.split_pane.switch_pane('up' if key == 'up' else 'down')
        elif key in ('+', 'plus'):
            self.split_pane.resize_pane(1)
        elif key in ('-', 'minus'):
            self.split_pane.resize_pane(-1)

    def run(self):
        self.loop.run()


if __name__ == "__main__":
    MainLoop().run()
