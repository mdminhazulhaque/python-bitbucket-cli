# Bitbucket CLI

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

A modern, feature-rich command-line interface for interacting with Bitbucket repositories. Manage repositories, branches, commits, pipelines, and variables directly from your terminal.

## ✨ Features

- 🏢 **Repository Management**: List and explore repositories in workspaces
- 🌿 **Branch Operations**: View and manage repository branches
- 📝 **Commit History**: Browse commit history with detailed information
- 🚀 **Pipeline Control**: List, monitor, and trigger Bitbucket Pipelines
- ⚙️ **Variable Management**: Manage pipeline variables with secure handling
- 📊 **Multiple Output Formats**: Plain text and table formats
- 🔐 **Secure Authentication**: App password-based authentication
- 🎯 **Type-Safe**: Written with modern Python type hints
- 🛠️ **Error Handling**: Comprehensive error handling and user-friendly messages

## 🚀 Installation

### From Source

```bash
git clone https://github.com/mdminhazulhaque/python-bitbucket-cli.git
cd python-bitbucket-cli
pip install -e .
```

### From PyPI

```bash
pip install python-bitbucket-cli
```

## 🔐 Authentication

The CLI uses Bitbucket App Passwords for authentication. Generate one from your [Bitbucket Account Settings](https://bitbucket.org/account/settings/app-passwords/).

### Required Permissions

Ensure your app password has the following permissions:

- ✅ **Workspace** → Read
- ✅ **Projects** → Read
- ✅ **Repositories** → Read
- ✅ **Pipelines** → Read, Write *(for triggering pipelines), Edit variables *(for managing variables)*
- ✅ **Issues** → Read *(optional, for future features)*
- ✅ **Pull requests** → Read *(optional, for future features)*

### Environment Setup

Export your credentials as an environment variable:

```bash
export BITBUCKET_AUTH="username:app_password"
```

Add this to your shell profile (`.bashrc`, `.zshrc`, etc.) for persistence:

```bash
echo 'export BITBUCKET_AUTH="username:app_password"' >> ~/.zshrc
source ~/.zshrc
```

## 📖 Usage

The CLI provides several commands with consistent options and helpful output formatting.

### Global Options

- `--help`, `-h`: Show help message
- `--version`: Show version information

### Command-Specific Options

Most commands support:
- `--table`, `-t`: Display output in table format
- `--workspace`, `-w`: Specify Bitbucket workspace
- `--repo`, `-r`: Specify repository name

## 📚 Commands Reference

### List Repositories

```bash
# List all repositories in a workspace
bitbucket-cli repos -w myworkspace

# Display in table format
bitbucket-cli repos -w myworkspace --table
```

**Example Output:**
```
frontend-v2
backend-api
mobile-app
documentation
infrastructure
```

### List Branches

```bash
# List branches in a repository
bitbucket-cli branches -w myworkspace -r frontend-v2

# Table format
bitbucket-cli branches -w myworkspace -r frontend-v2 -t
```

**Example Output:**
```
master
develop
feature/user-auth
hotfix/login-bug
release/v2.1.0
```

### List Commits

```bash
# List commits from master branch
bitbucket-cli commits -w myworkspace -r frontend-v2

# List commits from specific branch
bitbucket-cli commits -w myworkspace -r frontend-v2 -b develop

# Fetch all commits (not just first page)
bitbucket-cli commits -w myworkspace -r frontend-v2 --all

# Table format with detailed information
bitbucket-cli commits -w myworkspace -r frontend-v2 -t
```

**Example Output:**
```
bd4ed959 2024-12-21T11:58:13+00:00 John Doe Fix authentication bug
c0621052 2024-12-20T18:28:03+00:00 Jane Smith Add user dashboard
b60f0381 2024-12-19T01:09:36+00:00 Bob Wilson Update dependencies
```

### List Pipeline Builds

```bash
# List recent pipeline builds
bitbucket-cli builds -w myworkspace -r frontend-v2

# List all builds
bitbucket-cli builds -w myworkspace -r frontend-v2 --all

# Table format
bitbucket-cli builds -w myworkspace -r frontend-v2 -t
```

**Example Output:**
```
42 2024-12-21T03:56:07.704Z master John Doe SUCCESSFUL
41 2024-12-20T06:19:35.715Z develop Jane Smith FAILED
40 2024-12-19T01:52:33.846Z feature/auth Bob Wilson SUCCESSFUL
```

### Trigger Pipelines

```bash
# Trigger pipeline on a branch
bitbucket-cli trigger -w myworkspace -r frontend-v2 -b master

# Trigger custom pipeline on specific commit
bitbucket-cli trigger -w myworkspace -r frontend-v2 -b master \
  -c bd4ed959e90944d8f661de57d314dd8eacd5e79e \
  -p deploy-production
```

**Example Output:**
```
✅ Pipeline 43 started successfully!
🔗 View progress: https://bitbucket.org/myworkspace/frontend-v2/addon/pipelines/home#!/results/43
```

### Manage Variables

```bash
# List all variables
bitbucket-cli variables -w myworkspace -r frontend-v2

# List in table format
bitbucket-cli variables -w myworkspace -r frontend-v2 -t

# Create a new variable
bitbucket-cli variables -w myworkspace -r frontend-v2 \
  --create -k API_KEY -v "your-api-key-here"

# Create a secured variable
bitbucket-cli variables -w myworkspace -r frontend-v2 \
  --create -k SECRET_TOKEN -v "super-secret-token" --secured

# Delete a variable (use the UUID from list command)
bitbucket-cli variables -w myworkspace -r frontend-v2 \
  --delete "{8cc198d9-44ff-43ea-9473-acd697bcbf31}"
```

**Example Output:**
```
{8cc198d9-44ff-43ea-9473-acd697bcbf31} API_KEY your-api-key-here 🔓
{9f06955b-3ca9-4b93-908f-fe353977ec48} SECRET_TOKEN ******************** 🔒
{18643776-dbe1-4fe6-b01b-6d103242c9ca} ENVIRONMENT production 🔓
```

## 🔧 Advanced Usage

### Using Short Alias

The installation provides a short `bb` alias for convenience:

```bash
bb repos -w myworkspace
bb builds -w myworkspace -r myapp -t
bb trigger -w myworkspace -r myapp -b master
```

### Combining with Other Tools

```bash
# Count repositories
bb repos -w myworkspace | wc -l

# Find specific branch
bb branches -w myworkspace -r myapp | grep feature

# Get latest commit hash
bb commits -w myworkspace -r myapp | head -1 | cut -d' ' -f1

# Monitor pipeline status
watch -n 30 'bb builds -w myworkspace -r myapp | head -5'
```

### Scripting and Automation

```bash
#!/bin/bash
# Deploy script example

WORKSPACE="mycompany"
REPO="production-api"
BRANCH="master"

echo "🚀 Starting deployment for $REPO..."

# Trigger deployment pipeline
RESULT=$(bb trigger -w $WORKSPACE -r $REPO -b $BRANCH -p deploy-production)

if [[ $RESULT == *"started successfully"* ]]; then
    echo "✅ Deployment initiated successfully"
    echo "$RESULT"
else
    echo "❌ Deployment failed to start"
    exit 1
fi
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/mdminhazulhaque/python-bitbucket-cli.git
cd python-bitbucket-cli

# Install the package
make install
```

### Project Structure

```
python-bitbucket-cli/
├── bitbucket/
│   ├── __init__.py
│   ├── bitbucket.py    # Core API client
│   └── main.py         # CLI interface
├── requirements.txt
├── setup.py
├── Makefile
├── LICENSE
└── README.md
```

### API Client Architecture

The `BitBucketClient` class provides a clean, type-safe interface to the Bitbucket REST API:

- **Error Handling**: Custom exceptions with clear error messages
- **Type Safety**: Full type hints for better development experience  
- **Session Management**: Reuses HTTP connections for better performance
- **Pagination**: Automatic handling of paginated API responses
- **Authentication**: Secure app password authentication

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for the CLI interface
- Uses [Requests](https://requests.readthedocs.io/) for HTTP client functionality
- Table formatting powered by [Tabulate](https://github.com/astanin/python-tabulate)
- Inspired by the need for efficient DevOps workflows

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/mdminhazulhaque/python-bitbucket-cli/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/mdminhazulhaque/python-bitbucket-cli/discussions)
- 📧 **Email**: mdminhazulhaque@gmail.com

## 🗺️ Roadmap

- [ ] Pull request operations (create, list, approve, merge)
- [ ] Issue management (create, list, update)
- [ ] Project management (create, list, update)
