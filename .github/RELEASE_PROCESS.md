# Release Process Documentation

## Overview

The release process is **fully automated**. You only need to create and push a git tag.

## Quick Release (2 Commands)

```bash
# 1. Create and push tag with your release message
git tag -a v0.1.3 -m "Add new search features and improve CLI"
git push origin v0.1.3

# 2. That's it! Everything else is automatic ✨
```

## What Happens Automatically

When you push a tag, the workflow:

1. ✅ **Generates CHANGELOG.md** from git commit history
2. ✅ **Commits CHANGELOG.md** back to the repository
3. ✅ **Builds** the package
4. ✅ **Creates GitHub Release** with categorized changes
5. ✅ **Publishes to PyPI** automatically

**No manual changelog maintenance needed!**

## Release Notes Are Auto-Generated

The workflow automatically categorizes your commits:

- **Features** - Commits starting with `feat:`
- **Bug Fixes** - Commits starting with `fix:`
- **Documentation** - Commits starting with `docs:`
- **Other Changes** - All other commits

### Example Commit Messages

```bash
git commit -m "feat: add new regex search functionality"
git commit -m "fix: resolve Windows path issues"
git commit -m "docs: update installation instructions"
git commit -m "refactor: simplify embedding service"
git commit -m "chore: update dependencies"
```

Using these prefixes makes release notes cleaner and more organized.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **v0.1.0** → **v0.1.1** - Bug fixes (PATCH)
- **v0.1.1** → **v0.2.0** - New features (MINOR)
- **v0.2.0** → **v1.0.0** - Breaking changes (MAJOR)

## Complete Example

```bash
# Work on your features
git add .
git commit -m "feat: add support for custom embeddings"
git commit -m "fix: handle empty search results"
git commit -m "docs: update README with new examples"
git push

# When ready to release
git tag -a v0.1.3 -m "Enhanced search and fixed bugs"
git push origin v0.1.3

# Wait 2-3 minutes and check:
# - GitHub Releases: https://github.com/starthackHQ/Contextinator/releases
# - PyPI: https://pypi.org/project/contextinator/
# - CHANGELOG.md will be auto-updated
```

## Monitoring Release

Track progress:

1. Go to [GitHub Actions](https://github.com/starthackHQ/Contextinator/actions)
2. Watch the "Release and Publish" workflow
3. Should complete in 2-3 minutes

## Tag Message Tips

Your tag message appears in the release title. Make it descriptive:

```bash
# ❌ Bad
git tag -a v0.1.3 -m "new release"

# ✅ Good
git tag -a v0.1.3 -m "Add CLI improvements and search filters"
git tag -a v0.2.0 -m "Major refactor with breaking changes"
```

## Troubleshooting

### Release Created but PyPI Upload Failed

Check if `PYPI_API_TOKEN` is set:

1. Go to Settings → Secrets and variables → Actions
2. Verify `PYPI_API_TOKEN` exists
3. Re-run the failed workflow

### Wrong Version Number

Delete and recreate tag:

```bash
git tag -d v0.1.3
git push origin :refs/tags/v0.1.3
git tag -a v0.1.3 -m "Your message"
git push origin v0.1.3
```

### Need to Update CHANGELOG Manually

Even though it's auto-generated, you can edit CHANGELOG.md anytime:

```bash
# Edit CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: update changelog with additional notes"
git push
```

The next release will preserve your changes and add new sections.

## Manual PyPI Upload (Emergency)

Only if automation completely fails:

```bash
python -m build
twine upload dist/*
```

## Best Practices

1. ✅ Use conventional commit prefixes (`feat:`, `fix:`, `docs:`)
2. ✅ Write clear, descriptive commit messages
3. ✅ Test your changes before tagging
4. ✅ Use semantic versioning
5. ✅ Push commits before creating tags
6. ✅ Use annotated tags (`-a` flag)
