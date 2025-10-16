# Contributing to LLM Code Deployment System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

1. **Report Bugs** - Submit detailed bug reports
2. **Suggest Features** - Propose new features or enhancements
3. **Write Code** - Submit pull requests
4. **Improve Documentation** - Fix typos, add examples, clarify instructions
5. **Create Templates** - Add new task templates
6. **Write Tests** - Improve test coverage

## 🐛 Reporting Bugs

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to recreate the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, relevant configurations
- **Logs**: Any error messages or relevant logs

## 💡 Suggesting Features

Feature requests should include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches you considered
- **Additional Context**: Any other relevant information

## 🔧 Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/myaiprojectto.git
   cd myaiprojectto
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Set up pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Write docstrings for all functions/classes
- Maximum line length: 100 characters

### Code Quality
```bash
# Format code
make format

# Lint code
make lint

# Run tests
make test
```

### Example Function
```python
def process_task(task: Task, email: str) -> Dict[str, Any]:
    """
    Process a task for a student.
    
    Args:
        task: The task to process
        email: Student email address
    
    Returns:
        Dictionary containing processing results
    
    Raises:
        ValueError: If task is invalid
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python test_system.py

# Run specific test
python -c "from test_system import test_imports; test_imports()"
```

### Writing Tests
- Add tests for new features
- Ensure existing tests pass
- Aim for high coverage

## 📋 Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Add docstrings to new code
   - Update CHANGELOG.md

2. **Test Your Changes**
   ```bash
   make test
   ```

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   
   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test updates
   - `chore:` - Build/tooling changes

4. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Provide clear description
   - Reference any related issues
   - Include screenshots if relevant

## 🎓 Creating Task Templates

To add a new task template:

1. **Create JSON file** in `templates/tasks/`
   ```json
   {
     "id": "your-task-id",
     "brief": "Task description with ${seed}",
     "attachments": [],
     "checks": [
       "Check 1",
       "js: document.querySelector('#element')"
     ],
     "round2": [
       {
         "brief": "Revision task",
         "checks": []
       }
     ]
   }
   ```

2. **Test the template**
   ```python
   from templates.task_loader import task_loader
   template = task_loader.get_template_by_id('your-task-id')
   task = task_loader.generate_task(template, 'test@example.com', 1)
   print(task)
   ```

3. **Document the template**
   - Add description to README.md
   - Include example usage
   - List evaluation criteria

## 🏗️ Architecture Guidelines

### Adding New Features

1. **API Endpoints**: Add to appropriate file in `api/`
2. **Database Models**: Update `database/models.py`
3. **Utilities**: Add to `utils/`
4. **Scripts**: Add to `scripts/`

### Database Changes

1. Update models in `database/models.py`
2. Create migration if using Alembic
3. Update documentation

### API Changes

1. Update Pydantic models
2. Add appropriate error handling
3. Update API documentation
4. Add tests

## 📚 Documentation Guidelines

- Use clear, concise language
- Include code examples
- Add screenshots where helpful
- Keep documentation up-to-date
- Use proper Markdown formatting

## 🔍 Code Review Process

Pull requests will be reviewed for:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it well-written and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Style**: Does it follow project conventions?

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create a GitHub Issue
- **Chat**: Join our community (if available)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🙏
