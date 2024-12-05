# Themes - Textual


Changing the theme
-----------------------------------------------------------

The theme can be changed at runtime via the Command Palette (Ctrl+P).

You can also programmatically change the theme by setting the value of `App.theme` to the name of a theme:

```
class MyApp(App):
    def on_mount(self) -> None:
        self.theme = "nord"

```


A theme must be _registered_ before it can be used. Textual comes with a selection of built-in themes which are registered by default.

Registering a theme
-------------------------------------------------------------

A theme is a simple Python object which maps variable names to colors. Here's an example:

```
from textual.theme import Theme

arctic_theme = Theme(
    name="arctic",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)

```


You can register this theme by calling `App.register_theme` in the `on_mount` method of your `App`.

```
from textual.app import App

class MyApp(App):
    def on_mount(self) -> None:
        # Register the theme
        self.register_theme(arctic_theme)  # (1)!

        # Set the app's theme
        self.theme = "arctic"  # (2)!

```


1.  Register the theme, making it available to the app (and command palette)
2.  Set the app's theme. When this line runs, the app immediately refreshes to use the new theme.

Theme variables
-----------------------------------------------------

Themes consist of up to 11 _base colors_, (`primary`, `secondary`, `accent`, etc.), which Textual uses to generate a broad range of CSS variables. For example, the `textual-dark` theme defines the _primary_ base color as `#004578`.

Here's an example of CSS which uses these variables:

```
MyWidget {
    background: $primary;
    color: $foreground;
}

```


On changing the theme, the values stored in these variables are updated to match the new theme, and the colors of `MyWidget` are updated accordingly.

Base colors
---------------------------------------------

When defining a theme, only the `primary` color is required. Textual will attempt to generate the other base colors if they're not supplied.

The following table lists each of 11 base colors (as used in CSS) and a description of where they are used by default.



* Color: $primary
  * Description: The primary color, can be considered the branding color. Typically used for titles, and backgrounds for strong emphasis.
* Color: $secondary
  * Description: An alternative branding color, used for similar purposes as $primary, where an app needs to differentiate something from the primary color.
* Color: $foreground
  * Description: The default text color, which should be legible on $background, $surface, and $panel.
* Color: $background
  * Description: A color used for the background, where there is no content. Used as the default background color for screens.
* Color: $surface
  * Description: The default background color of widgets, typically sitting on top of $background.
* Color: $panel
  * Description: A color used to differentiate a part of the UI form the main content. Used sparingly in Textual itself.
* Color: $boost
  * Description: A color with alpha that can be used to create layers on a background.
* Color: $warning
  * Description: Indicates a warning. Typically used as a background color. $text-warning can be used for foreground.
* Color: $error
  * Description: Indicates an error. Typically used as a background color. $text-error can be used for foreground.
* Color: $success
  * Description: Used to indicate success. Typically used as a background color. $text-success can be used for foreground.
* Color: $accent
  * Description: Used sparingly to draw attention. Typically contrasts with $primary and $secondary.


Shades
-----------------------------------

For every color, Textual generates 3 dark shades and 3 light shades.

*   Add `-lighten-1`, `-lighten-2`, or `-lighten-3` to the color's variable name to get lighter shades (3 is the lightest).
*   Add `-darken-1`, `-darken-2`, and `-darken-3` to a color to get the darker shades (3 is the darkest).

For example, `$secondary-darken-1` is a slightly darkened `$secondary`, and `$error-lighten-3` is a very light version of the `$error` color.

Light and dark themes
-----------------------------------------------------------------

Themes can be either _light_ or _dark_. This setting is specified in the `Theme` constructor via the `dark` argument, and influences how Textual generates variables. Built-in widgets may also use the value of `dark` to influence their appearance.

Text color
-------------------------------------------

The default color of text in a theme is `$foreground`. This color should be legible on `$background`, `$surface`, and `$panel` backgrounds.

There is also `$foreground-muted` for text which has lower importance. `$foreground-disabled` can be used for text which is disabled, for example a menu item which can't be selected.

You can set the text color via the color CSS property.

The available text colors are:

*   `$text-primary`
*   `$text-secondary`
*   `$text-accent`
*   `$text-warning`
*   `$text-error`
*   `$text-success`

### Ensuring text legibility

In some cases, the background color of a widget is unpredictable, so we cannot be certain our text will be readable against it.

The theme system defines three CSS variables which you can use to ensure that text is legible on any background.

*   `$text` is set to a slightly transparent black or white, depending on which has better contrast against the background the text is on.
*   `$text-muted` sets a slightly faded text color. Use this for text which has lower importance. For instance a sub-title or supplementary information.
*   `$text-disabled` sets faded out text which indicates it has been disabled. For instance, menu items which are not applicable and can't be clicked.

### Colored text

Colored text is also generated from the base colors, which is guaranteed to be legible against a background of `$background`, `$surface`, and `$panel`. For example, `$text-primary` is a version of the `$primary` color tinted to ensure legibility.

Output (Theme: textual-dark)colored\_text.py

ColoredText $text-primary $text-secondary $text-accent $text-warning $text-error $text-success

colored\_text.py

```
from textual.app import App, ComposeResult
from textual.widgets import Label

COLORS = ("primary", "secondary", "accent", "warning", "error", "success")


class ColoredText(App[None]):
    CSS = "\n".join(f".text-{color} {{color: $text-{color};}}" for color in COLORS)

    def compose(self) -> ComposeResult:
        for color in COLORS:
            yield Label(f"$text-{color}", classes=f"text-{color}")


app = ColoredText()
if __name__ == "__main__":
    app.run()

```


These colors are also be guaranteed to be legible when used as the foreground color of a widget with a _muted color_ background.

Muted colors
-----------------------------------------------

Muted colors are generated from the base colors by blending them with `$background` at 70% opacity. For example, `$primary-muted` is a muted version of the `$primary` color.

Textual aims to ensure that the colored text it generates is legible against the corresponding muted color. In other words, `$text-primary` text should be legible against a background of `$primary-muted`:

Output (Theme: textual-dark)muted\_backgrounds.py

MutedBackgrounds $text-primary on $primary-muted $text-secondary on $secondary-muted $text-accent on $accent-muted $text-warning on $warning-muted $text-error on $error-muted $text-success on $success-muted

muted\_backgrounds.py

```
from textual.app import App, ComposeResult
from textual.widgets import Label

COLORS = ("primary", "secondary", "accent", "warning", "error", "success")


class MutedBackgrounds(App[None]):
    CSS = "\n".join(
        f".text-{color} {{padding: 0 1; color: $text-{color}; background: ${color}-muted;}}"
        for color in COLORS
    )

    def compose(self) -> ComposeResult:
        for color in COLORS:
            yield Label(f"$text-{color} on ${color}-muted", classes=f"text-{color}")


app = MutedBackgrounds()
if __name__ == "__main__":
    app.run()

```


The available muted colors are:

*   `$primary-muted`
*   `$secondary-muted`
*   `$accent-muted`
*   `$warning-muted`
*   `$error-muted`
*   `$success-muted`

Additional variables
---------------------------------------------------------------

Textual uses the base colors as default values for additional variables used throughout the framework. These variables can be overridden by passing a `variables` argument to the `Theme` constructor. This also allows you to override variables such as `$primary-muted`, described above.

In the Gruvbox theme, for example, we override the foreground color of the block cursor (the cursor used in widgets like `OptionList`) to be `$foreground`.

```
Theme(
    name="gruvbox",
    primary="#85A598",
    secondary="#A89A85",
    warning="#fabd2f",
    error="#fb4934",
    success="#b8bb26",
    accent="#fabd2f",
    foreground="#fbf1c7",
    background="#282828",
    surface="#3c3836",
    panel="#504945",
    dark=True,
    variables={
        "block-cursor-foreground": "#fbf1c7",
        "input-selection-background": "#689d6a40",
    },
)

```


Here's a comprehensive list of these variables, their purposes, and default values:

### Border


|Variable       |Purpose                                           |Default Value             |
|---------------|--------------------------------------------------|--------------------------|
|$border        |The border color for focused widgets with a border|$primary                  |
|$border-blurred|The border color for unfocused widgets            |Slightly darkened $surface|


### Cursor



* Variable: $block-cursor-foreground
  * Purpose: Text color for block cursor (e.g., in OptionList)
  * Default Value: $text
* Variable: $block-cursor-background
  * Purpose: Background color for block cursor
  * Default Value: $primary
* Variable: $block-cursor-text-style
  * Purpose: Text style for block cursor
  * Default Value: "bold"
* Variable: $block-cursor-blurred-foreground
  * Purpose: Text color for unfocused block cursor
  * Default Value: $text
* Variable: $block-cursor-blurred-background
  * Purpose: Background color for unfocused block cursor
  * Default Value: $primary with 30% opacity
* Variable: $block-cursor-blurred-text-style
  * Purpose: Text style for unfocused block cursor
  * Default Value: "none"
* Variable: $block-hover-background
  * Purpose: Background color when hovering over a block
  * Default Value: $boost with 5% opacity


### Input



* Variable: $input-cursor-background
  * Purpose: Background color of the input cursor
  * Default Value: $foreground
* Variable: $input-cursor-foreground
  * Purpose: Text color of the input cursor
  * Default Value: $background
* Variable: $input-cursor-text-style
  * Purpose: Text style of the input cursor
  * Default Value: "none"
* Variable: $input-selection-background
  * Purpose: Background color of selected text
  * Default Value: $primary-lighten-1 with 40% opacity
* Variable: $input-selection-foreground
  * Purpose: Text color of selected text
  * Default Value: $background


### Scrollbar



* Variable: $scrollbar
  * Purpose: Color of the scrollbar
  * Default Value: $panel
* Variable: $scrollbar-hover
  * Purpose: Color of the scrollbar when hovered
  * Default Value: $panel-lighten-1
* Variable: $scrollbar-active
  * Purpose: Color of the scrollbar when active (being dragged)
  * Default Value: $panel-lighten-2
* Variable: $scrollbar-background
  * Purpose: Color of the scrollbar track
  * Default Value: $background-darken-1
* Variable: $scrollbar-corner-color
  * Purpose: Color of the scrollbar corner
  * Default Value: Same as $scrollbar-background
* Variable: $scrollbar-background-hover
  * Purpose: Color of the scrollbar track when hovering over the scrollbar area
  * Default Value: Same as $scrollbar-background
* Variable: $scrollbar-background-active
  * Purpose: Color of the scrollbar track when the scrollbar is active
  * Default Value: Same as $scrollbar-background


### Links


|Variable              |Purpose                               |Default Value       |
|----------------------|--------------------------------------|--------------------|
|$link-background      |Background color of links             |"initial"           |
|$link-background-hover|Background color of links when hovered|$primary            |
|$link-color           |Text color of links                   |$text               |
|$link-style           |Text style of links                   |"underline"         |
|$link-color-hover     |Text color of links when hovered      |$text               |
|$link-style-hover     |Text style of links when hovered      |"bold not underline"|



|Variable                      |Purpose                                        |Default Value|
|------------------------------|-----------------------------------------------|-------------|
|$footer-foreground            |Text color in the footer                       |$foreground  |
|$footer-background            |Background color of the footer                 |$panel       |
|$footer-key-foreground        |Text color for key bindings in the footer      |$accent      |
|$footer-key-background        |Background color for key bindings in the footer|"transparent"|
|$footer-description-foreground|Text color for descriptions in the footer      |$foreground  |
|$footer-description-background|Background color for descriptions in the footer|"transparent"|
|$footer-item-background       |Background color for items in the footer       |"transparent"|


### Button


|Variable                |Purpose                              |Default Value |
|------------------------|-------------------------------------|--------------|
|$button-foreground      |Foreground color for standard buttons|$foreground   |
|$button-color-foreground|Foreground color for colored buttons |$text         |
|$button-focus-text-style|Text style for focused buttons       |"bold reverse"|


App-specific variables
-------------------------------------------------------------------

The variables above are defined and used by Textual itself. However, you may also wish to expose other variables which are specific to your application.

You can do this by overriding `App.get_theme_variable_defaults` in your `App` subclass.

This method should return a dictionary of variable names and their default values. If a variable defined in this dictionary is also defined in a theme's `variables` dictionary, the theme's value will be used.

Previewing colors
---------------------------------------------------------

Run the following from the command line to preview the colors defined in the color system:

Inside the preview you can change the theme via the Command Palette (Ctrl+P), and view the base variables and shades generated from the theme.