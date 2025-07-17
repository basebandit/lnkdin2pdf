# Contributing

## 🛠 Releasing a New Version

We follow a two-step release process to ensure clean tagging, accurate changelogs, and reproducibility.

### 🔧 Step 1: Prepare the Release (bump version and changelog)

1. Go to **Actions → Prepare Release PR → Run workflow**
2. This:
   - Bumps the version in `pyproject.toml`
   - Updates `CHANGELOG.md`
   - Commits to a new branch: `release/vX.Y.Z`

3. Open a PR from `release/vX.Y.Z` → `main`, review the changelog, and merge.

### 🏷️ Step 2: Tag the Release

After the PR is merged:

```bash
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```
