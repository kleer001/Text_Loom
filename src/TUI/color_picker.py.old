import curses
import colorsys

class ColorMixer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.rgb = [0, 0, 0]
        self.hsv = [0, 0, 0]
        self.saved_colors = []
        self.setup_colors()

    def setup_colors(self):
        curses.start_color()
        curses.use_default_colors()
        for i in range(256):
            curses.init_pair(i + 1, curses.COLOR_WHITE, i)
        curses.init_pair(257, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 5.0, g / 5.0, b / 5.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return [int(h * 15), int(s * 5), int(v * 5)]

    def hsv_to_rgb(self, h, s, v):
        h, s, v = h / 15.0, s / 5.0, v / 5.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return [int(r * 5), int(g * 5), int(b * 5)]

    def draw_slider(self, x, y, value, max_value, label, color):
        for i in range(6):
            for j in range(3):
                self.stdscr.addch(y + i, x + j, ' ', curses.color_pair(color + 1))
            if i >= 5 - value:
                self.stdscr.addch(y + i, x + 1, ' ', curses.color_pair(257))
        self.stdscr.addstr(y + 6, x, f"{value:3d}")
        self.stdscr.addstr(y + 7, x + 1, label)

    def draw_color_square(self, x, y, color):
        for i in range(8):
            for j in range(12):
                self.stdscr.addch(y + i, x + j, ' ', curses.color_pair(color + 1))

    def draw_interface(self):
        height, width = self.stdscr.getmaxyx()
        if height < 20 or width < 60:
            self.stdscr.addstr(0, 0, "Terminal too small. Needs to be at least 20x60.")
            return

        # Draw RGB sliders
        self.draw_slider(1, 1, self.rgb[0], 5, "R", 16 + self.rgb[0] * 36)
        self.draw_slider(5, 1, self.rgb[1], 5, "G", 16 + self.rgb[1] * 6)
        self.draw_slider(9, 1, self.rgb[2], 5, "B", 16 + self.rgb[2])

        # Draw HSV sliders
        self.draw_slider(15, 1, self.hsv[0], 15, "H", 16 + self.hsv[0] * 16)
        self.draw_slider(19, 1, self.hsv[1], 5, "S", 16 + self.hsv[0] * 16 + self.hsv[1])
        self.draw_slider(23, 1, self.hsv[2], 5, "V", 232 + self.hsv[2] * 3)

        # Draw mixed color
        color = 16 + self.rgb[0] * 36 + self.rgb[1] * 6 + self.rgb[2]
        self.draw_color_square(30, 1, color)
        self.stdscr.addstr(10, 30, f"Color: {color:3d}")
        hex_color = f"#{self.rgb[0]*51:02X}{self.rgb[1]*51:02X}{self.rgb[2]*51:02X}"
        self.stdscr.addstr(11, 30, f"Hex: {hex_color}")

        # Draw saved colors
        for i, saved_color in enumerate(self.saved_colors):
            if i < 3:  # Limit to 3 saved colors
                self.draw_color_square(45 + i * 15, 1, saved_color)
                self.stdscr.addstr(10, 45 + i * 15, f"Color: {saved_color:3d}")
                r = (saved_color - 16) // 36
                g = ((saved_color - 16) % 36) // 6
                b = (saved_color - 16) % 6
                hex_saved = f"#{r*51:02X}{g*51:02X}{b*51:02X}"
                self.stdscr.addstr(11, 45 + i * 15, f"Hex: {hex_saved}")

        # Draw helpful text
        #self.stdscr.addstr(13, 1, "-" * (width - 2))
        self.stdscr.addstr(12, 1, "Controls:", curses.A_BOLD)
        self.stdscr.addstr(13, 1, "R: q/a  G: w/s  B: e/d  H: u/j  S: i/k  V: o/l")
        self.stdscr.addstr(14, 1, "Space: Save color  Ctrl+Q: Quit")

        self.stdscr.refresh()

    def run(self):
        while True:
            self.draw_interface()
            key = self.stdscr.getch()
            if key == ord('q'):
                self.rgb[0] = min(5, self.rgb[0] + 1)
            elif key == ord('a'):
                self.rgb[0] = max(0, self.rgb[0] - 1)
            elif key == ord('w'):
                self.rgb[1] = min(5, self.rgb[1] + 1)
            elif key == ord('s'):
                self.rgb[1] = max(0, self.rgb[1] - 1)
            elif key == ord('e'):
                self.rgb[2] = min(5, self.rgb[2] + 1)
            elif key == ord('d'):
                self.rgb[2] = max(0, self.rgb[2] - 1)
            elif key == ord('u'):
                self.hsv[0] = min(15, self.hsv[0] + 1)
            elif key == ord('j'):
                self.hsv[0] = max(0, self.hsv[0] - 1)
            elif key == ord('i'):
                self.hsv[1] = min(5, self.hsv[1] + 1)
            elif key == ord('k'):
                self.hsv[1] = max(0, self.hsv[1] - 1)
            elif key == ord('o'):
                self.hsv[2] = min(5, self.hsv[2] + 1)
            elif key == ord('l'):
                self.hsv[2] = max(0, self.hsv[2] - 1)
            elif key == ord(' '):
                color = 16 + self.rgb[0] * 36 + self.rgb[1] * 6 + self.rgb[2]
                if len(self.saved_colors) < 3:
                    self.saved_colors.append(color)
                else:
                    self.saved_colors = self.saved_colors[1:] + [color]
            elif key == 17:  # Ctrl+Q
                break

            # Update RGB and HSV mutually
            if key in [ord('q'), ord('a'), ord('w'), ord('s'), ord('e'), ord('d')]:
                self.hsv = self.rgb_to_hsv(*self.rgb)
            elif key in [ord('u'), ord('j'), ord('i'), ord('k'), ord('o'), ord('l')]:
                self.rgb = self.hsv_to_rgb(*self.hsv)

def main(stdscr):
    curses.curs_set(0)
    mixer = ColorMixer(stdscr)
    mixer.run()

curses.wrapper(main)
