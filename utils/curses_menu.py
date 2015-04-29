#!/usr/bin/env python
import sys
import curses


def curses_menu(menu_items, title="Title", top_instructions="", bottom_instructions=""):
    screen = curses.initscr()
    curses.noecho()
    screen.keypad(1)
    curses.start_color()

    # Terminal windows smaller than 80x24 will give a sub optimal experience
    max_y, max_x = screen.getmaxyx()
    if max_x < 80 and max_y < 24:
        curses.endwin()
        sys.exit("Minimum terminal size require to run this script is 80x24. "
                 "Resize the terminal window and run the script again.")

    user_input = None

    position = 0
    list_length = max_y - 10
    top_position = 0
    bottom_position = top_position + list_length

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    highlight_text = curses.color_pair(1)
    normal_text = curses.A_NORMAL

    while user_input != ord('\n'):
        screen.clear()
        screen.addstr(2, 2, title[:75], curses.A_STANDOUT)
        screen.addstr(4, 2, top_instructions[:75], curses.A_BOLD)
        if len(menu_items) > list_length:
            screen.addstr(list_length + 6, 6, "...More Items...", curses.A_BOLD)
        screen.addstr(list_length + 8, 2, bottom_instructions[:75], curses.A_BOLD)

        x = 0
        for item in menu_items:
            # Only show items between the top and bottom positions
            if (x >= top_position) and (x < bottom_position):
                # Detect what is highlighted from position variable
                if position == x:
                    screen.addstr(6 + int(x) - top_position, 4, str(item), highlight_text)
                else:
                    screen.addstr(6 + int(x) - top_position, 4, str(item), normal_text)
            x += 1

        screen.refresh()
        user_input = screen.getch()

        # If the user entered the down arrow
        if user_input == 258:
            if position < len(menu_items) - 1:
                # Set the position to the next item
                position += 1
                # Update the page top and bottom if the user goes below the last item on the screen
                if position == bottom_position:
                    top_position += 1
                    bottom_position += 1
            else:
                position = 0
                top_position = 0
                bottom_position = list_length
        # If the user entered the up arrow
        elif user_input == 259:
            if position > 0:
                # Update the page top and bottom if the user goes above the first item on the screen
                if position == top_position:
                    top_position += -1
                    bottom_position += -1
                # Set the position to the previous item
                position += -1
            else:
                position = len(menu_items) - 1
                # If the number of items is less than the visible list size then don't update the top and bottom
                if len(menu_items) > (bottom_position - top_position):
                    top_position = len(menu_items) - list_length
                    bottom_position = len(menu_items)
        # If the user enter something other than the up/down arrows and the return key
        elif user_input != ord('\n'):
            curses.flash()
    # If the user presses return then exit the loop and return the index item that was selected
    curses.endwin()
    return position