# Docurial Extensions

Markdown extension resources for [Docurial][docurial]

## Install

Generally, just installing Docums Material will automatically install `docurial-extensions`. But if you had a
need to manually install it, you can use pip.

```
pip install docurial-extensions
```

But make sure you've also installed Docums Material as well as this won't work without it. 

```
pip install docurial
```

## Inline SVG Icons

Docums Material provides numerous icons from Material, FontAwesome, and Octicons, but it does so by inlining the SVG
icons into the source. Currently there is no easy way access these icons and arbitrarily insert them into Markdown
content. Users must include the icon fonts themselves and do it with HTML.

This module allows you to use PyMdown Extensions' [Emoji][emoji] extension to enable easy insertion of Docurial's
SVG assets using simple `:emoji-syntax:`.  This is done by creating our own [emoji index][emoji-index] and
[emoji generator][emoji-generator]. The custom index provides a modified version of the Emoji extensions Twemoji
index.

In addition to the custom index, you must also specify the associated custom generator. This will will find the
appropriate icon and insert it into your Markdown content as an inlined SVG.

Example:

```yaml
markdown_extensions:
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
```

Then, using the folder structure of Material's `.icons` folder, you can specify icons:

```
We can use Material Icons :material-airplane:.

We can also use Fontawesome Icons :fontawesome-solid-ambulance:.

That's not all, we can also use Octicons :octicons-octoface:.
```

## Using Local Custom Icons

In Docums, you can override theme assets locally, and even add assets to the theme. Unfortunately, the Markdown parsing
process isn't aware of the Docums environment. Luckily, if you are using PyMdown Extensions 7.1, you can pass in custom
icon paths that will be used when constructing the emoji index and include your custom SVG assets. If a folder path of
`theme/my_icons` was given to the index builder, all icons under `my_project/my_icons`, even in sub-folders, would
become part of the index.

```yaml
markdown_extensions:
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
      options:
        custom_icons:
          - theme/my_icons
```

If given an icon at `my_project/my_icons/animals/bird.svg`, the icon would be available using the emoji syntax as
`:animals-bird:`. Notice that the base folder that is provided doesn't contribute to the icon's name. Also, folders
are separated with `-`. Folder names and icon names should be compatible with the emoji syntax, so special characters
should be avoided -- `-` and `_` are okay.

You can provide as many paths as you would like, and they will be evaluated in the order that they are specified. The
Material theme's own icons will be evaluated after all custom paths. This allows a user to override Material's icons if
desired.

If an icon name is already in the index, the icon will not be added. It is recommended to always have your icons in
sub-folders to help namespace them to avoid name collisions. In the example above, `bird` was under `animals` which
created the name `:animals-bird:` and helped create a more unique name with less of a chance of creating a duplicate
name with existing emoji and Material icons.

[emoji]: https://facelessuser.github.io/pymdown-extensions/extensions/emoji/
[emoji-index]: https://facelessuser.github.io/pymdown-extensions/extensions/emoji/#custom-emoji-indexes
[emoji-generator]: https://facelessuser.github.io/pymdown-extensions/extensions/emoji/#custom-emoji-generators
[docurial]: https://github.com/squidfunk/docurial
