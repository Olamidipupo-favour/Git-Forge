# GitMod 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

A smart Git commit generator that creates realistic, conventional commit messages for testing and demonstration purposes. GitMod analyzes your repository changes and generates appropriate commit messages that follow industry standards.

## ✨ Features

- **Smart Commit Messages**: Generates conventional commit messages based on actual file changes
- **File Type Analysis**: Understands different file types (Python, JavaScript, HTML, CSS, etc.)
- **Conventional Commits**: Follows the [Conventional Commits](https://www.conventionalcommits.org/) specification
- **Configurable Authors**: Support for multiple authors with config file or environment variables
- **Flexible Configuration**: JSON-based configuration with CLI overrides
- **Automatic Pushing**: Optional automatic push to remote repositories
- **Dry Run Mode**: Preview changes without actually creating commits

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd GitMod
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a configuration file** (`commit_config.json`):
   ```json
   {
     "repo_path": "./your-repo",
     "authors": [
       {"name": "Ada Lovelace", "email": "ada@example.com"},
       {"name": "Alan Turing", "email": "alan@example.com"}
     ],
     "commits": 20,
     "days_spread": 10,
     "push": true,
     "remote": "origin",
     "branch": "main"
   }
   ```

4. **Run GitMod**:
   ```bash
   python main.py
   ```

## 📖 Usage

### Basic Usage

```bash
# Use default configuration
python main.py

# Preview what would be done
python main.py --dry-run

# Use custom config file
python main.py --config my_config.json

# Override specific values
python main.py --commits 5 --days-spread 3
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to configuration file | `commit_config.json` |
| `--repo-path` | `-p` | Override repository path from config | From config |
| `--commits` | | Override number of commits from config | From config |
| `--days-spread` | | Override days spread from config | From config |
| `--dry-run` | | Preview changes without creating commits | `False` |

### Configuration File

The `commit_config.json` file supports the following options:

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `repo_path` | string | Path to the git repository | `"."` |
| `authors` | array | List of author objects with name and email | Default authors |
| `commits` | integer | Number of commits to create | `10` |
| `days_spread` | integer | Days to spread commits over | `10` |
| `push` | boolean | Whether to push to remote after commits | `false` |
| `remote` | string | Remote repository name | `"origin"` |
| `branch` | string | Branch name to push to | `"main"` |

### Author Configuration

You can specify authors in two ways:

1. **Configuration file** (recommended):
   ```json
   {
     "authors": [
       {"name": "John Doe", "email": "john@example.com"},
       {"name": "Jane Smith", "email": "jane@example.com"}
     ]
   }
   ```

2. **Environment variable**:
   ```bash
   export GIT_AUTHORS="John Doe:john@example.com,Jane Smith:jane@example.com"
   ```

## 🎯 Commit Message Examples

GitMod generates intelligent commit messages based on your changes:

### File Additions
- `feat: add Python module`
- `docs: add documentation`
- `config: add configuration files`

### File Modifications
- `fix: update Python code`
- `docs: update documentation`
- `config: update configuration`

### File Deletions
- `refactor: remove unused files`

### File Renames
- `refactor: rename files`

## 🔧 Advanced Usage

### Custom Configuration

Create a custom configuration file for different scenarios:

```json
{
  "repo_path": "./my-project",
  "authors": [
    {"name": "Your Name", "email": "your.email@example.com"}
  ],
  "commits": 50,
  "days_spread": 30,
  "push": false
}
```

### Environment Variables

Set up environment variables for consistent author information:

```bash
export GIT_AUTHORS="Your Name:your.email@example.com"
```

### Integration with CI/CD

Use GitMod in your CI/CD pipeline for testing:

```yaml
# GitHub Actions example
- name: Generate test commits
  run: |
    python main.py --config test_config.json --dry-run
```

## 📁 Project Structure

```
GitMod/
├── main.py              # CLI entry point
├── strategies.py        # Core Git strategy implementation
├── requirements.txt     # Python dependencies
├── commit_config.json   # Configuration file
├── LICENSE             # MIT License
└── README.md           # This file
```

## 🛠️ Development

### Prerequisites

- Python 3.7+
- Git repository
- Required Python packages (see `requirements.txt`)

### Dependencies

- `click`: CLI framework
- `faker`: Fake data generation
- `GitPython`: Git repository manipulation

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with dry-run to test
python main.py --dry-run
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is intended for testing, demonstration, and educational purposes. Please ensure you have proper permissions before using it on repositories you don't own or control.

## 🐛 Troubleshooting

### Common Issues

1. **Repository not found**: Ensure the `repo_path` in your config points to a valid Git repository
2. **Permission denied**: Make sure you have write permissions to the repository
3. **Push failed**: Verify your remote repository is properly configured and accessible

### Getting Help

If you encounter any issues:

1. Check the configuration file format
2. Ensure all dependencies are installed
3. Verify Git repository permissions
4. Use `--dry-run` to preview changes

---

**Happy committing! 🎉** 