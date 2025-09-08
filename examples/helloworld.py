"""

    lucy-ui  -  Pygame UI & Layout Library

    This file is a part of the lucy-ui
    project and distributed under MIT license.
    https://github.com/kadir014/lucy-ui

"""

# This example is meant to be a "hello world" introduction to Lucy UI library.
# It shows the barebones usage, layout management and few widgets as a simple
# building skeleton for your applications.

import pygame

from lucyui.core import __version__
from lucyui.core import Size, StackDirection, SizeBehavior, LayoutDistribution
from lucyui.widgets import TextInput, TextButton, Label
from lucyui.layouts import Stack


# Create a resizable window.
# As you resize the window, you will see the UI layout realign itself and the widgets.
WINDOW_SIZE = (480, 360)
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
pygame.display.set_caption(f"Pygame-CE {pygame.ver} and LucyUI {__version__}")
clock = pygame.Clock()
font = pygame.Font("assets/FiraCode-Regular.ttf", 14)


# The root layout which will hold all the UI elements.
# Currently it's a vertical stack, however it can be any other layout type.
root_lyt = Stack(StackDirection.VERTICAL, WINDOW_SIZE)

label = Label(font, "Hello world!")
root_lyt.add_widget(label)

score = 0
score_button = TextButton(font, text=f"Score: {score}")
root_lyt.add_widget(score_button)

# Now we want the text input and clear button to be next to each other.
# So we create a child layout, which will hold the next widgets, and add it to root layout.
sub_lyt = Stack(StackDirection.HORIZONTAL)
sub_lyt.vertical_behavior = SizeBehavior.FIXED
root_lyt.add_layout(sub_lyt)

text_input = TextInput(font, placeholder="You can write here.")
sub_lyt.add_widget(text_input)

clear_button = TextButton(font, text="Clear")
sub_lyt.add_widget(clear_button)


# Widget hooks are basically actions that fire under certain events.
# You can connect multiple callback functions to a single hook.
@score_button.clicked.connect
def clicked_callback():
    global score
    score += 1
    score_button.text = f"Score: {score}"

# And of course they don't have to be used as decorators.
clear_button.clicked.connect(text_input.clear)


if __name__ == "__main__":
    is_running = True

    while is_running:
        clock.tick(60)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.WINDOWRESIZED:
                new_width, new_height = event.x, event.y

                # Change the root layout's size to resized window dimensions
                # and update its content by requestion a realign.
                root_lyt.current_size = Size(new_width, new_height)
                root_lyt.realign()
        
        # Update our root layout with the pygame event list.
        root_lyt.update(events)

        screen.fill((255, 255, 255))

        # Render our root layout onto the display surface.
        root_lyt.render(screen)

        pygame.display.flip()

    pygame.quit()