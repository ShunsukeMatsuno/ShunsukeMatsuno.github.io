# Hugo Minimal Modern Theme

## Overview
This is a minimal and modern theme for Hugo, a static site generator. The theme is designed to be clean and simple, making it easy to customize and extend.

## Features
- Responsive design
- Customizable SCSS
- Integrated with Bootstrap 5
- SEO optimized
- Google Analytics support
- Custom fonts and icons
- Sidebar navigation
- Footer section

## Installation
To install this theme, clone the repository into your Hugo site's `themes` directory:

```sh
git clone https://github.com/shunsukematsuno/hugo-sleek.git themes/hugo-sleek
```

## Configuration
Update your site's configuration file to use the theme:

```toml
theme = "hugo-sleek"
```

## Customization
### SCSS
You can customize the SCSS by modifying the files in the `assets/scss` directory. The main SCSS file is `style.scss`, which imports various components and variables.

### Additional CSS
To add additional CSS, create a new partial template (e.g., `additional_css.html`) and include it in the `header_css` block in your base template:

```html
{{ block "header_css" . }}
    {{ partial "additional_css.html" . }}
{{ end }}
```

### JavaScript
Custom JavaScript files can be added to the `assets/js` directory and processed using Hugo's built-in asset pipeline.


