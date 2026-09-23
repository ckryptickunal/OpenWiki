#!/usr/bin/env bash
# Publish site/ to the gh-pages branch, which GitHub Pages serves.
# Use this while GitHub Actions is unavailable; pages.yml does the same job when Actions runs.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
sha=$(git subtree split --prefix site)
git push origin "$sha:refs/heads/gh-pages"
echo "Deployed site/ ($sha) to gh-pages (GitHub Pages mirror; the main site deploys on Vercel)"
