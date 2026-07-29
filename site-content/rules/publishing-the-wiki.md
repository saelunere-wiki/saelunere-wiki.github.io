---
type: rule
name: Publishing the Wiki
label: Guide
group: For the Archivist
order: 8
summary: How a local Markdown edit ends up live on this site - cloning, pulling, editing, and pushing, for the Archivist and the DM alike.
---

# Publishing the Wiki

> **Contains no secrets.** These are the same commands anyone with access to the
> repository would use - nothing here is private.

This site isn't edited through a web form. It's plain Markdown files in a **git
repository**; whoever has access edits the files on their own computer and
**pushes** the change, and the live site rebuilds itself automatically within a
minute or two. This page is the whole loop, start to finish.

## One-time setup (do this once, ever)

1. Install **Git**: [git-scm.com](https://git-scm.com) (Windows/Mac/Linux all
   supported - on Windows this also gives you "Git Bash", a terminal that
   understands the commands below).
2. Make sure you've been added as a **collaborator** on the repository (ask
   whoever administers the campaign account if you haven't).
3. Clone the repository - this downloads your own local copy:

   ```
   git clone https://github.com/saelunere-wiki/saelunere-wiki.github.io.git
   cd saelunere-wiki.github.io
   ```

4. The first time you push, Git will ask you to sign in. Use a **Personal
   Access Token** as the password (not your account password - GitHub no
   longer accepts those for git operations). Create one under **Settings →
   Developer settings → Personal access tokens**, scoped to just this
   repository with **Contents: Read and write**.

## Previewing locally

The site is one self-contained HTML file, built from the Markdown in
`site-content/` by a small Python script. No install beyond Python itself:

```
python build_site.py
```

This creates (or updates) `campaign_site.html` in the project folder - open it
in any browser to see exactly what you just changed, before anyone else does.

## Making a change and publishing it

```
git pull                          # get everyone else's latest changes first
# ...edit files under site-content/ in any text editor...
python build_site.py              # rebuild and preview locally
git add site-content/
git commit -m "Describe what changed, e.g. 'Update Samuel Greaves after Ep.3'"
git push
```

That's it. The push triggers an automated build-and-deploy - no one needs to
touch `campaign_site.html` or the live site directly. Give it a minute, then
refresh the site.

## If your push is rejected

This means someone else pushed a change since your last `git pull`. Fix:

```
git pull --rebase
git push
```

If the same file was edited by both of you in the same place, Git will ask you
to resolve the conflict by hand - it'll mark the conflicting lines in the file
with `<<<<<<<` / `=======` / `>>>>>>>`; edit it down to what it should say, then:

```
git add <the file>
git rebase --continue
git push
```

## Quick command reference

| I want to… | Command |
|---|---|
| Get the latest changes | `git pull` |
| See what I've changed | `git status` |
| Stage my changes | `git add site-content/` |
| Save a checkpoint | `git commit -m "message"` |
| Publish | `git push` |
| See recent history | `git log --oneline` |

## The DM's copy

The DM keeps a separate, private set of notes - hidden motives, future plot,
session prep - that never lives in this repository. He pulls this repo's
public Markdown the same way (`git pull`) to keep his own private wiki in sync
with what's now public, then reconciles the two on his own machine. Nothing
about that process touches this site.
