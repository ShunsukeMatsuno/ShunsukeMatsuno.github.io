# Personal Website
### https://shunsukematsuno.github.io/

This website is built with [Hugo](https://gohugo.io/).


# Memo
## assets
- `scss` overrides the default bootstrap configurations of the theme
- `cv` contains the tex sources of cv. Edit cv here. In the build workflow, only `cv.pdf` is copied to `static`.

## Hugo mod
- Run `hugo mod get -u` to update mod. Can delete old checksums from `go.sum`.
  - Currently only [hugo image mod](https://github.com/hugomods/images) is used.


# Personal Website with Hugo and GitHub Pages

This repository hosts the source code and GitHub Actions workflow for deploying my personal website using [Hugo](https://gohugo.io/) and [GitHub Pages](https://pages.github.com/).

---

## Workflow Summary

### TL;DR
After updating files in the `main` branch, commit and push the changes. Then, trigger the `hugo-deploy.yml` workflow manually from the GitHub UI.

### Deploy Hugo Website to GitHub Pages (`hugo-deploy.yml`)
Trigger this workflow manually from the GitHub UI.

#### **1. `cv_change_detection`**
Detects changes in `cv.tex` and related files under `./assets/cv/`. Outputs a flag indicating if the CV has changed.

#### **2. `build_cv`**
If changes are detected, compiles the CV using LaTeX (`xelatex`) and moves the output PDF to `./static/cv/`. Updates the `cv-snapshot` branch for future comparisons.

#### **3. `build_website`**
Builds the Hugo website and deploys it to the `gh-pages` branch using `peaceiris/actions-gh-pages@v4`.

### pages-build-deployment 
The deployment workflow runs automatically after the `hugo-deploy.yml` job is run successfully. The workflow automatically publishes the `gh-pages` branch as github pages.

---

## Setup and Deployment

1. Ensure GitHub Pages is configured to serve the site from the `gh-pages` branch.
2. To trigger the workflow manually, go to **Actions** > **Deploy Hugo Website to GitHub Pages** > **Run workflow**.

---

## Required Secrets

- `GITHUB_TOKEN`: Provided automatically by GitHub Actions.
- `GOOGLE_ANALYTICS_ID`: (Optional) Used for analytics in Hugo.

---

## Branches

- **`main`**: Contains source code and website content.
- **`cv-snapshot`**: Tracks previous CV versions.
- **`gh-pages`**: Deployment branch for GitHub Pages.

---

## Author

**Shunsuke Matsuno**  
