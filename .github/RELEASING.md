# Quick Release Guide

## TL;DR - Release in 2 Commands + 1 Click

```bash
git tag -a v0.1.3 -m "Your release summary"
git push origin v0.1.3
```

Then go to GitHub → Releases, edit the draft notes, and click **Publish release**.

---

## What Happens Automatically

✅ On tag push: package is built and verified, and a **draft GitHub Release** is created  
✅ On release publish: package is built again, artifacts are attached, and the package is published to PyPI

**You write the release notes (once) in the draft, then publish.**

---

## Tips for Better Release Notes

Use conventional commit prefixes:

```bash
git commit -m "feat: new feature description"
git commit -m "fix: bug fix description"
git commit -m "docs: documentation update"
```

These automatically categorize changes in release notes.

Tip: since release notes are now human-written, you can still use conventional commits, but you’re not forced to.

---

## Version Bumping

- Bug fixes: `v0.1.1` → `v0.1.2`
- New features: `v0.1.2` → `v0.2.0`
- Breaking changes: `v0.2.0` → `v1.0.0`

---

## Monitor Release

Watch progress: [GitHub Actions](https://github.com/starthackHQ/Contextinator/actions)

Check results:

- [GitHub Releases](https://github.com/starthackHQ/Contextinator/releases)
- [PyPI Package](https://pypi.org/project/contextinator/)

---

For detailed information, see [RELEASE_PROCESS.md](.github/RELEASE_PROCESS.md)
