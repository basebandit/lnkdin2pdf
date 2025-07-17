# Contributing

We welcome contributions of all kinds! This guide will help you get started with development and ensure consistency across all changes.

---

## 🤝 How to Contribute Code

We follow a structured development process to keep the codebase clean, consistent, and production-ready.

### 1. Fork and Clone

Start by [forking the repository](https://github.com/basebandit/lnkdin2pdf) and cloning your fork:

```bash
git clone https://github.com/your-username/lnkdin2pdf.git
cd linkedin-to-pdf
```

### 2. Create a Branch

Create a feature or fix branch:

```bash
git checkout -b feat/my-new-feature
```

Use descriptive prefixes like `feat/`, `fix/`, or `docs/`.

### 3. Make Your Changes

* Follow [PEP8](https://peps.python.org/pep-0008/)
* Use type hints and docstrings
* Keep changes small and focused

### 4. Format, Lint, and Type Check

Before committing, all code must pass pre-commit checks. Run them locally:

```bash
pre-commit run --all-files
```

This runs:

* ✅ `ruff` for linting and autofix
* ✅ `black` for formatting
* ✅ `mypy` for type checking
* ✅ `commitizen` for commit message validation

These also run automatically on commit, so your commit may be rejected if any check fails.

### 5. Use Conventional Commits

We use [Commitizen](https://commitizen-tools.github.io/commitizen/) to enforce [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). This ensures semantic versioning and changelog generation work correctly.

To commit:

```bash
cz commit
```

Or manually use this format:

```text
<type>(<scope>): short description

e.g.:
feat(scraper): add image extraction for posts
```

Types include `feat`, `fix`, `docs`, `chore`, `refactor`, etc.

---

## 🛠 Releasing a New Version

We use [Commitizen](https://github.com/commitizen-tools/commitizen) to manage [semantic versioning](https://semver.org/) based on commit messages.

### What triggers a version bump?

* `fix:` → bumps **patch**
* `feat:` → bumps **minor**
* `BREAKING CHANGE:` → bumps **major**

### 🔧 Step 1: Prepare the Release

1. Go to **GitHub Actions → Prepare Release PR → Run workflow**

2. This will:

   * Analyze commits
   * Bump version in `pyproject.toml` and `uv.lock`
   * Update `CHANGELOG.md` and `_release_notes.md`
   * Commit to `release/vX.Y.Z` branch

3. Open a PR from `release/vX.Y.Z` to `main`, review changes, and merge.

### 🏷️ Step 2: Tag the Release

Once the PR is merged, tag the release manually:

```bash
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

This triggers the release pipeline.

---

## ✅ Summary of Pre-Commit Hooks

The following checks run automatically on commit:

* `ruff` — Lints and optionally autofixes Python code
* `black` — Formats code
* `mypy` — Runs static type checks
* `commitizen-check` — Validates commit messages for semantic versioning

Install them with:

```bash
pre-commit install
```

---

Thank you for contributing 🙌
