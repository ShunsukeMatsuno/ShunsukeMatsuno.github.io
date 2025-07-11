# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal academic website built with [Hugo](https://gohugo.io/) and deployed to GitHub Pages. The site supports English and Japanese content and uses the `hugo-sleek` theme.

## Key Commands

### Development
- `hugo server` - Start local development server
- `hugo` - Build the site (outputs to `docs/` directory)
- `hugo --gc --ignoreCache --minify --destination docs` - Production build

### Deployment
- **Manual trigger**: Run `./update_pages.sh` to trigger the GitHub Actions deployment workflow
- **GitHub Actions**: Use "Deploy Hugo Website to GitHub Pages" workflow (manual trigger only)

### CV Management
- CV source files are in `assets/cv/`
- Edit `assets/cv/cv.tex` and related files in `assets/cv/cv_data/`
- GitHub Actions automatically compiles LaTeX CV when changes are detected and copies to `static/cv/`

## Architecture

### Directory Structure
- `content/` - Website content (Markdown files)
- `assets/cv/` - LaTeX CV source files
- `static/` - Static assets (images, PDFs, etc.)
- `themes/hugo-sleek/` - Hugo theme
- `layouts/` - Custom layout overrides
- `config.yaml` - Hugo configuration
- `docs/` - Generated site output (GitHub Pages source)

### Multilingual Setup
- Default language: English (`en`)
- Secondary language: Japanese (`ja`)
- Language-specific content in subdirectories

### GitHub Actions Workflow
The deployment process consists of three jobs:
1. **cv_change_detection**: Detects changes in CV files by comparing against `cv-snapshot` branch
2. **build_cv**: Compiles LaTeX CV if changes detected, commits PDF to main branch
3. **build_website**: Builds Hugo site and deploys to `gh-pages` branch

### Branch Structure
- `main` - Source code and content
- `cv-snapshot` - Tracks CV changes for comparison
- `gh-pages` - Deployed site (auto-generated)

## Configuration Notes

- Site config in `config.yaml`
- Uses Hugo modules (see `go.mod`) with `hugomods/images` for image processing
- Theme: `hugo-sleek` with custom SCSS overrides
- Publishing directory: `docs/` (configured for GitHub Pages)
- Google Analytics integration available via `GOOGLE_ANALYTICS_ID` environment variable

## Analytics
The `ANALYTICS/` directory contains Python scripts for website analytics data processing, separate from the main Hugo site.