# Quick Release Guide

## TL;DR - Release in 2 Commands

```bash
git tag -a v0.1.3 -m "Your release summary"
git push origin v0.1.3
```

**That's it!** Everything else is automatic.

---

## What Happens Automatically

✅ CHANGELOG.md is generated and committed  
✅ Package is built and verified  
✅ GitHub Release is created with notes  
✅ Package is published to PyPI

**No manual work needed!**

---

## Tips for Better Release Notes

Use conventional commit prefixes:

```bash
git commit -m "feat: new feature description"
git commit -m "fix: bug fix description"
git commit -m "docs: documentation update"
```

These automatically categorize changes in release notes.

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
