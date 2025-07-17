# Contributing

We welcome contributions and aim to maintain a clear and reliable release process that adheres to semantic versioning and Git best practices.

---

## 🧠 Semantic Versioning via Commit Messages

We follow **[Semantic Versioning](https://semver.org/)** using [Commitizen](https://commitizen-tools.github.io/commitizen/) to automatically determine the next release version based on commit messages:

- **`MAJOR`** version bumps (e.g., `2.0.0`) are triggered by commits with a `BREAKING CHANGE` footer or `!` in the commit type.
- **`MINOR`** version bumps (e.g., `1.2.0`) are triggered by `feat:` commits.
- **`PATCH`** version bumps (e.g., `1.2.3`) are triggered by `fix:` commits.
- Other types (e.g., `docs:`, `chore:`, `refactor:`) do not trigger a version bump unless combined with `BREAKING CHANGE`.

To ensure proper versioning:
- Follow the [Conventional Commits](https://www.conventionalcommits.org/) format.
- Use `cz commit` (or `cz c`) to generate compliant commit messages.

Example commit messages:
```text
feat(pdf): support markdown export
fix(scraper): handle private post detection
refactor: migrate to asyncio for scraping
```

## 🛠 Releasing a New Version

We follow a two-step release process to ensure clean tagging, accurate changelogs, and reproducibility.

### 🔧 Step 1: Prepare the Release (bump version and changelog)

1. Go to **Actions → Prepare Release PR → Run workflow**
2. This:
   - Bumps the version in `pyproject.toml` and `uv.lock`
   - Updates `CHANGELOG.md` `_release_notes.md`
   - Commits to a new branch: `release/vX.Y.Z`

3. Open a PR from `release/vX.Y.Z` → `main`, review the changes and merge.

### 🏷️ Step 2: Tag the Release

After the PR is merged:

```bash
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```
