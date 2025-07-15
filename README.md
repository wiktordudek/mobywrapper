<div align="center">
    <h1>🛡️ mObywrapper</h1>
</div>

## 📝 What is this?

mObywrapper is a Python wrapper that replicates the functionality of the official [Polish eID verificator website](https://weryfikator.mobywatel.gov.pl/). It allows you to programmatically verify Polish eIDs using the publicly available verification API.  **This is intended for educational and testing purposes only.**

## 🚀 Quick Start

**Installation:**

You can install `mobywrapper` using `uv` (recommended) or `pip`.

⚡️ `uv pip install git+https://github.com/wiktordudek/mobywrapper.git`

🐢 `pip install git+https://github.com/wiktordudek/mobywrapper.git`

**Usage Example:**

There are 2 demo examples available:
- [demo/demo_simple.py](demo_simple.py) – A simple example application demonstrating the core verification flow.
- [demo/demo_full.py](demo_full.py) – A more comprehensive library usage demo that provides a complete demonstration of an example application's functionality.

## ⚠️ Disclaimers

- This is an *unofficial* implementation and is not endorsed by or affiliated with the Polish government or the mObywatel app developers;
- The accuracy and reliability of the verification process depend on the official API and the correctness of the implementation.  Always verify the results with the official website.
- Before collecting other people's data, make sure you meet all the GDPR requirements. Storing personal data makes you a personal data administrator.

## 🤝 Contributing

Contributions are welcome!  If you've found a bug or have a suggestion for improvement, please submit an issue or pull request.

For code formatting please use [Ruff](https://docs.astral.sh/ruff/formatter/) with default settings – a [Ruff VSCode extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) is available.

## 📄 License

mObywrapper is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.