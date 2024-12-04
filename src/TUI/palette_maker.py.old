import curses

# Control variables for color square size
SQUARE_WIDTH = 4
SQUARE_HEIGHT = 4

def get_color_components(color_number):
    if color_number < 16:
        return color_number, color_number, color_number
    elif color_number < 232:
        color_number -= 16
        b = color_number % 6
        g = (color_number // 6) % 6
        r = color_number // 36
        return r, g, b
    else:
        gray = color_number - 232
        return gray, gray, gray

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    
    for i in range(256):
        curses.init_pair(i + 1, curses.COLOR_WHITE, i)

    stdscr.clear()

    # Display 16 standard colors
    for i in range(16):
        for y in range(SQUARE_HEIGHT):
            for x in range(SQUARE_WIDTH):
                stdscr.addstr(y, i * SQUARE_WIDTH + x, " ", curses.color_pair(i + 1))
        stdscr.addstr(SQUARE_HEIGHT // 2, i * SQUARE_WIDTH + SQUARE_WIDTH // 2 - 1, f"{i:2}", curses.color_pair(i + 1))

    # Display 6x6x6 color cube
    for cube in range(6):
        for y in range(6):
            for x in range(6):
                color = 16 + cube * 36 + y * 6 + x
                start_y = SQUARE_HEIGHT + 1 + cube * (SQUARE_HEIGHT + 1) + y * SQUARE_HEIGHT
                start_x = x * SQUARE_WIDTH
                for dy in range(SQUARE_HEIGHT):
                    for dx in range(SQUARE_WIDTH):
                        stdscr.addstr(start_y + dy, start_x + dx, " ", curses.color_pair(color + 1))
                stdscr.addstr(start_y + SQUARE_HEIGHT // 2, start_x + SQUARE_WIDTH // 2 - 1, f"{color:3}", curses.color_pair(color + 1))

    # Display grayscale colors
    grayscale_start_y = SQUARE_HEIGHT + 1 + 6 * (SQUARE_HEIGHT + 1) + SQUARE_HEIGHT + 1
    for i in range(24):
        color = 232 + i
        start_y = grayscale_start_y
        start_x = i * SQUARE_WIDTH
        for y in range(SQUARE_HEIGHT):
            for x in range(SQUARE_WIDTH):
                stdscr.addstr(start_y + y, start_x + x, " ", curses.color_pair(color + 1))
        stdscr.addstr(start_y + SQUARE_HEIGHT // 2, start_x + SQUARE_WIDTH // 2 - 1, f"{color:3}", curses.color_pair(color + 1))

    stdscr.addstr(grayscale_start_y + SQUARE_HEIGHT + 1, 0, "Press any key to exit...")
    stdscr.getch()

curses.wrapper(main)
