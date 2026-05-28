# Contributing to AI Daily News Trend Hunter

First off, thank you for taking the time to contribute! Contributions are what make the open-source community such an amazing place to learn, inspire, and create.

All types of contributions are welcome: bug fixes, feature requests, documentation improvements, and structural refactoring.

---

## 🗺️ Git Branching Strategy

We follow a structured branching model to maintain a stable `main` branch.

1.  **Branch Naming Convention:**
    *   Features: `feature/short-description` (e.g., `feature/add-telegram-notifier`)
    *   Bugfixes: `bugfix/issue-description` (e.g., `bugfix/fix-date-parsing`)
    *   Documentation: `docs/readme-cleanup`
2.  **Workflow Steps:**
    *   Fork the repository and create your branch from `main`.
    *   Make changes locally and test.
    *   Commit with clear, imperative-style commit messages (e.g., `feat: integrate slack dispatch helper`).
    *   Open a Pull Request (PR) targeting the `main` branch.

---

## 🛠️ Local Development Setup

To set up a local development sandbox:

1.  **Fork and Clone:**
    ```bash
    git clone https://github.com/your-username/daily-news-hunter.git
    cd daily-news-hunter
    ```
2.  **Set Up Virtual Env:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
3.  **Install Dev Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Local Testing:**
    Configure a local `.env` file containing mock values (or valid development keys) and verify execution using `python main.py`.

---

## 📝 Coding Standards

To maintain a clean and maintainable codebase, we enforce standard guidelines:

*   **PEP 8 Compliance:** Follow standard Python PEP 8 formatting rules.
*   **Docstrings:** All public functions, modules, and classes must contain clear docstrings explaining their arguments, returns, and purpose.
*   **Type Hints:** Where appropriate, use PEP 484 type hints.
*   **No Code Blocks in AI Output:** When calling Gemma 4, ensure templates are set to prevent markdown wrapping (````json ... ````) inside the JSON extractor helper.

---

## 🚀 Pull Request Checklist

Before submitting your PR, please verify:

- [ ] Code is formatted cleanly and adheres to PEP 8 standards.
- [ ] No syntax errors or import exceptions.
- [ ] Requirements files are updated if new dependencies were introduced.
- [ ] The change has been manually tested and does not crash on missing env variables.
- [ ] Commit history is squashed and messages follow standard conventions.

Thank you for contributing! Your efforts help improve the pipeline for everyone.
