# lucy-ui
A modern, easy-to-use user interface and layout management library for Pygame(-CE).



# Examples
TODO



# Installation
TODO



# Glossary
### Widget
Base graphical user interface element each component in the library builds on.

### Space
In the documentation, you'll see references to different kinds of "spaces" (coordinate systems). These describe the frame of reference used for transforms:
- **Screen space**: This is your regular coordinates in the Pygame window (viewport). The top-left corner is (0, 0), and the bottom-right corner is (window_width, window_height)
- **World space**: This is used interchangebly with screen space.
- **Widget space**: The local coordinate system of a widget, relative to its own geometry. For example, (0, 0) is always the top-left corner inside that widget, no matter where it is on the screen.
- **Local space**: Same as widget space.

### Hook
Widget hooks are basically actions that fire under certain events that the user can connect callbacks to so they can listen to these certain actions. Such as button widget's `clicked` hook.


# License
[MIT](LICENSE) © Kadir Aksoy