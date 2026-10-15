#!/bin/sh
# Publish the Gazetteer's web site (https://rouental.github.io/Valsora-HOI4/): the map data of the last build and the
# page, as the next commit of the gh-pages branch, which GitHub Pages serves. Run from the repo root after a build:
#     sh scripts/publish_site.sh "Commit message"
# The message is the commit's (with its trailers, if the commit needs them). Nothing is committed when the site is
# unchanged. Pages redeploys in a minute or two; github.io itself can't be reached from Claude's sandbox.
set -e
MSG=${1:?"give the commit message: sh scripts/publish_site.sh \"The Gazetteer: ...\""}
retry() {   # network steps: 4 tries, 2, 4 and 8 s apart
    n=0
    until "$@"; do
        n=$((n + 1))
        [ $n -lt 4 ] || return 1
        sleep $((1 << n))
    done
}
python3 scripts/facts_export.py
python3 scripts/gazetteer_site.py
retry git fetch origin gh-pages
git worktree remove --force work/gh-pages 2>/dev/null || true
rm -rf work/gh-pages
git worktree prune
git worktree add --detach work/gh-pages origin/gh-pages
(
    cd work/gh-pages
    git rm -rq .
    cp -r ../gazetteer_site/. .
    git add -A
    if git diff --cached --quiet; then
        echo "the site is unchanged: nothing to publish"
    else
        git diff --cached --stat | tail -3
        git commit -q -m "$MSG"
        retry git push origin HEAD:gh-pages
        echo "published: $(git log --oneline -1)"
    fi
)
git worktree remove --force work/gh-pages
