from faker import Faker
from git import Repo, Actor
import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import difflib


class GitStrategy:
    def __init__(self, repo_path: str, config: Optional[Dict[str, Any]] = None):
        self.repo = Repo(repo_path)
        self.fake = Faker()
        self.config = config or {}
        
        # Conventional commit types and their common patterns
        self.commit_types = {
            'feat': ['add', 'create', 'implement', 'introduce', 'new'],
            'fix': ['fix', 'resolve', 'correct', 'repair', 'patch'],
            'docs': ['document', 'update readme', 'add docs', 'improve docs'],
            'style': ['format', 'style', 'indent', 'whitespace', 'lint'],
            'refactor': ['refactor', 'restructure', 'reorganize', 'cleanup'],
            'test': ['test', 'spec', 'coverage', 'unit test', 'integration'],
            'chore': ['chore', 'maintenance', 'deps', 'config', 'setup'],
            'perf': ['optimize', 'performance', 'speed', 'efficiency'],
            'ci': ['ci', 'pipeline', 'workflow', 'github actions'],
            'build': ['build', 'compile', 'dist', 'release']
        }
        
        # File type patterns for better message generation
        self.file_patterns = {
            'python': ['.py'],
            'javascript': ['.js', '.ts', '.jsx', '.tsx'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'],
            'docs': ['.md', '.txt', '.rst'],
            'data': ['.csv', '.xml', '.sql', '.db']
        }

    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension from path."""
        return Path(file_path).suffix.lower()

    def _categorize_files(self, files: List[str]) -> Dict[str, List[str]]:
        """Categorize files by type."""
        categories = {cat: [] for cat in self.file_patterns.keys()}
        categories['other'] = []
        
        for file_path in files:
            ext = self._get_file_extension(file_path)
            categorized = False
            
            for category, extensions in self.file_patterns.items():
                if ext in extensions:
                    categories[category].append(file_path)
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(file_path)
        
        return categories

    def _analyze_changes(self) -> Dict[str, any]:
        """Analyze the current changes in the repository."""
        try:
            # Get staged changes
            diff = self.repo.git.diff('--cached', '--name-status')
            if not diff.strip():
                # Get unstaged changes
                diff = self.repo.git.diff('--name-status')
            
            if not diff.strip():
                # If no changes, create a dummy file
                return self._create_dummy_changes()
            
            changes = {
                'added': [],
                'modified': [],
                'deleted': [],
                'renamed': []
            }
            
            for line in diff.strip().split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    status, file_path = parts[0], parts[1]
                    
                    if status == 'A':
                        changes['added'].append(file_path)
                    elif status == 'M':
                        changes['modified'].append(file_path)
                    elif status == 'D':
                        changes['deleted'].append(file_path)
                    elif status == 'R' and len(parts) >= 3:
                        changes['renamed'].append((file_path, parts[2]))
            
            return changes
            
        except Exception:
            return self._create_dummy_changes()

    def _create_dummy_changes(self) -> Dict[str, any]:
        """Create dummy changes when no real changes exist."""
        dummy_files = [
            'src/main.py',
            'tests/test_main.py',
            'README.md',
            'requirements.txt',
            'config/settings.json'
        ]
        
        return {
            'added': [random.choice(dummy_files)],
            'modified': [],
            'deleted': [],
            'renamed': []
        }

    def _generate_commit_type(self, changes: Dict[str, any]) -> str:
        """Determine commit type based on changes."""
        if changes['added']:
            # Check if it's documentation
            docs_files = [f for f in changes['added'] if self._get_file_extension(f) in ['.md', '.txt', '.rst']]
            if docs_files and len(docs_files) == len(changes['added']):
                return 'docs'
            return 'feat'
        
        if changes['deleted']:
            return 'refactor'
        
        if changes['modified']:
            # Check for specific patterns
            modified_files = changes['modified']
            for file_path in modified_files:
                ext = self._get_file_extension(file_path)
                if ext in ['.py', '.js', '.ts']:
                    return 'fix'
                elif ext in ['.md', '.txt']:
                    return 'docs'
                elif ext in ['.json', '.yaml', '.yml']:
                    return 'config'
            
            return 'fix'
        
        return 'chore'

    def _analyze_repository_structure(self) -> Dict[str, any]:
        """Analyze the existing repository structure to understand the project."""
        structure = {
            'file_types': {},
            'directories': [],
            'has_tests': False,
            'has_docs': False,
            'has_config': False,
            'main_language': None,
            'project_type': 'unknown',
            'commit_history': [],
            'development_phase': 'initial'
        }
        
        try:
            # Get all files in the repository
            all_files = []
            for root, dirs, files in os.walk(self.repo.working_dir):
                # Skip .git directory
                if '.git' in root:
                    continue
                    
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), self.repo.working_dir)
                    all_files.append(file_path)
            
            # Analyze file types
            for file_path in all_files:
                ext = self._get_file_extension(file_path)
                if ext:
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
            
            # Determine main language
            lang_counts = {
                'python': structure['file_types'].get('.py', 0),
                'javascript': structure['file_types'].get('.js', 0) + structure['file_types'].get('.ts', 0),
                'java': structure['file_types'].get('.java', 0),
                'cpp': structure['file_types'].get('.cpp', 0) + structure['file_types'].get('.c', 0),
                'go': structure['file_types'].get('.go', 0),
                'rust': structure['file_types'].get('.rs', 0)
            }
            
            if lang_counts:
                structure['main_language'] = max(lang_counts, key=lang_counts.get)
            
            # Check for common project patterns
            structure['has_tests'] = any('test' in f.lower() or 'spec' in f.lower() for f in all_files)
            structure['has_docs'] = any(f.endswith(('.md', '.txt', '.rst')) for f in all_files)
            structure['has_config'] = any(f.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')) for f in all_files)
            
            # Determine project type
            if structure['main_language'] == 'python':
                if any('requirements' in f.lower() or 'setup.py' in f for f in all_files):
                    structure['project_type'] = 'python_app'
                elif any('django' in f.lower() or 'flask' in f.lower() for f in all_files):
                    structure['project_type'] = 'web_app'
            elif structure['main_language'] == 'javascript':
                if any('package.json' in f for f in all_files):
                    structure['project_type'] = 'node_app'
                elif any('react' in f.lower() or 'vue' in f.lower() for f in all_files):
                    structure['project_type'] = 'frontend_app'
            
            # Analyze commit history to understand development phase
            structure.update(self._analyze_commit_history())
            
        except Exception:
            pass
        
        return structure

    def _analyze_commit_history(self) -> Dict[str, any]:
        """Analyze existing commit history to understand project development phase."""
        analysis = {
            'commit_history': [],
            'development_phase': 'initial',
            'feature_areas': set(),
            'recent_focus': 'setup'
        }
        
        try:
            # Get recent commits (last 20)
            commits = list(self.repo.iter_commits('HEAD', max_count=20))
            
            for commit in commits:
                analysis['commit_history'].append({
                    'message': commit.message.strip(),
                    'date': commit.committed_datetime,
                    'files': list(commit.stats.files.keys()) if commit.stats.files else []
                })
            
            # Analyze commit patterns to determine development phase
            messages = [c['message'] for c in analysis['commit_history']]
            
            # Count different types of commits
            feat_count = sum(1 for msg in messages if msg.startswith('feat:'))
            fix_count = sum(1 for msg in messages if msg.startswith('fix:'))
            docs_count = sum(1 for msg in messages if msg.startswith('docs:'))
            test_count = sum(1 for msg in messages if msg.startswith('test:'))
            perf_count = sum(1 for msg in messages if msg.startswith('perf:'))
            refactor_count = sum(1 for msg in messages if msg.startswith('refactor:'))
            
            # Determine development phase based on commit patterns
            total_commits = len(messages)
            if total_commits < 5:
                analysis['development_phase'] = 'initial'
            elif feat_count > fix_count * 2:
                analysis['development_phase'] = 'feature_development'
            elif fix_count > feat_count:
                analysis['development_phase'] = 'bug_fixing'
            elif docs_count > total_commits * 0.3:
                analysis['development_phase'] = 'documentation'
            elif test_count > total_commits * 0.2:
                analysis['development_phase'] = 'testing'
            elif perf_count > 0 or refactor_count > 0:
                analysis['development_phase'] = 'optimization'
            else:
                analysis['development_phase'] = 'maintenance'
            
            # Analyze recent focus areas
            recent_messages = messages[:5] if messages else []
            if any('api' in msg.lower() for msg in recent_messages):
                analysis['recent_focus'] = 'api'
            elif any('test' in msg.lower() for msg in recent_messages):
                analysis['recent_focus'] = 'testing'
            elif any('doc' in msg.lower() for msg in recent_messages):
                analysis['recent_focus'] = 'documentation'
            elif any('fix' in msg.lower() for msg in recent_messages):
                analysis['recent_focus'] = 'bug_fixes'
            elif any('perf' in msg.lower() for msg in recent_messages):
                analysis['recent_focus'] = 'performance'
            
            # Extract feature areas from commit messages
            for msg in messages:
                if 'api' in msg.lower():
                    analysis['feature_areas'].add('api')
                if 'auth' in msg.lower():
                    analysis['feature_areas'].add('authentication')
                if 'db' in msg.lower() or 'database' in msg.lower():
                    analysis['feature_areas'].add('database')
                if 'ui' in msg.lower() or 'frontend' in msg.lower():
                    analysis['feature_areas'].add('frontend')
                if 'test' in msg.lower():
                    analysis['feature_areas'].add('testing')
                if 'doc' in msg.lower():
                    analysis['feature_areas'].add('documentation')
            
        except Exception:
            pass
        
        return analysis

    def _generate_contextual_commit_message(self, changes: Dict[str, any], commit_type: str) -> str:
        """Generate a contextual commit message based on repository structure and changes."""
        structure = self._analyze_repository_structure()
        all_files = changes['added'] + changes['modified'] + changes['deleted']
        
        if not all_files:
            return f"{commit_type}: update repository"
        
        # Categorize files
        categories = self._categorize_files(all_files)
        
        # Generate contextual messages based on project type and changes
        if structure['project_type'] == 'python_app':
            return self._generate_python_commit_message(changes, commit_type, categories)
        elif structure['project_type'] == 'web_app':
            return self._generate_web_commit_message(changes, commit_type, categories)
        elif structure['project_type'] == 'node_app':
            return self._generate_node_commit_message(changes, commit_type, categories)
        elif structure['project_type'] == 'frontend_app':
            return self._generate_frontend_commit_message(changes, commit_type, categories)
        else:
            return self._generate_generic_commit_message(changes, commit_type, categories)

    def _generate_python_commit_message(self, changes: Dict[str, any], commit_type: str, categories: Dict[str, List[str]]) -> str:
        """Generate Python-specific commit messages."""
        if changes['added']:
            if categories['python']:
                if any('test' in f.lower() for f in categories['python']):
                    return f"{commit_type}: add test{'s' if len(categories['python']) > 1 else ''}"
                elif any('model' in f.lower() or 'class' in f.lower() for f in categories['python']):
                    return f"{commit_type}: add model{'s' if len(categories['python']) > 1 else ''}"
                else:
                    return f"{commit_type}: add Python module{'s' if len(categories['python']) > 1 else ''}"
            elif categories['docs']:
                return f"{commit_type}: add documentation"
            elif categories['config']:
                return f"{commit_type}: add configuration"
        
        elif changes['modified']:
            if categories['python']:
                if any('test' in f.lower() for f in categories['python']):
                    return f"{commit_type}: update test{'s' if len(categories['python']) > 1 else ''}"
                else:
                    return f"{commit_type}: update Python code"
            elif categories['docs']:
                return f"{commit_type}: update documentation"
            elif categories['config']:
                return f"{commit_type}: update configuration"
        
        return f"{commit_type}: update Python project"

    def _generate_web_commit_message(self, changes: Dict[str, any], commit_type: str, categories: Dict[str, List[str]]) -> str:
        """Generate web application commit messages."""
        if changes['added']:
            if categories['python']:
                return f"{commit_type}: add view{'s' if len(categories['python']) > 1 else ''}"
            elif categories['html']:
                return f"{commit_type}: add template{'s' if len(categories['html']) > 1 else ''}"
            elif categories['css']:
                return f"{commit_type}: add style{'s' if len(categories['css']) > 1 else ''}"
        
        elif changes['modified']:
            if categories['python']:
                return f"{commit_type}: update view{'s' if len(categories['python']) > 1 else ''}"
            elif categories['html']:
                return f"{commit_type}: update template{'s' if len(categories['html']) > 1 else ''}"
            elif categories['css']:
                return f"{commit_type}: update style{'s' if len(categories['css']) > 1 else ''}"
        
        return f"{commit_type}: update web application"

    def _generate_node_commit_message(self, changes: Dict[str, any], commit_type: str, categories: Dict[str, List[str]]) -> str:
        """Generate Node.js application commit messages."""
        if changes['added']:
            if categories['javascript']:
                return f"{commit_type}: add JavaScript module{'s' if len(categories['javascript']) > 1 else ''}"
            elif categories['config']:
                return f"{commit_type}: add package configuration"
        
        elif changes['modified']:
            if categories['javascript']:
                return f"{commit_type}: update JavaScript code"
            elif categories['config']:
                return f"{commit_type}: update package configuration"
        
        return f"{commit_type}: update Node.js application"

    def _generate_frontend_commit_message(self, changes: Dict[str, any], commit_type: str, categories: Dict[str, List[str]]) -> str:
        """Generate frontend application commit messages."""
        if changes['added']:
            if categories['javascript']:
                return f"{commit_type}: add component{'s' if len(categories['javascript']) > 1 else ''}"
            elif categories['css']:
                return f"{commit_type}: add style{'s' if len(categories['css']) > 1 else ''}"
            elif categories['html']:
                return f"{commit_type}: add page{'s' if len(categories['html']) > 1 else ''}"
        
        elif changes['modified']:
            if categories['javascript']:
                return f"{commit_type}: update component{'s' if len(categories['javascript']) > 1 else ''}"
            elif categories['css']:
                return f"{commit_type}: update style{'s' if len(categories['css']) > 1 else ''}"
            elif categories['html']:
                return f"{commit_type}: update page{'s' if len(categories['html']) > 1 else ''}"
        
        return f"{commit_type}: update frontend application"

    def _generate_generic_commit_message(self, changes: Dict[str, any], commit_type: str, categories: Dict[str, List[str]]) -> str:
        """Generate generic commit messages."""
        if changes['added']:
            if categories['python']:
                return f"{commit_type}: add Python module{'s' if len(categories['python']) > 1 else ''}"
            elif categories['javascript']:
                return f"{commit_type}: add JavaScript component{'s' if len(categories['javascript']) > 1 else ''}"
            elif categories['docs']:
                return f"{commit_type}: add documentation"
            elif categories['config']:
                return f"{commit_type}: add configuration file{'s' if len(categories['config']) > 1 else ''}"
            else:
                return f"{commit_type}: add new file{'s' if len(changes['added']) > 1 else ''}"
        
        elif changes['modified']:
            if categories['python']:
                return f"{commit_type}: update Python code"
            elif categories['javascript']:
                return f"{commit_type}: update JavaScript code"
            elif categories['docs']:
                return f"{commit_type}: update documentation"
            elif categories['config']:
                return f"{commit_type}: update configuration"
            else:
                return f"{commit_type}: update file{'s' if len(changes['modified']) > 1 else ''}"
        
        elif changes['deleted']:
            return f"{commit_type}: remove unused file{'s' if len(changes['deleted']) > 1 else ''}"
        
        elif changes['renamed']:
            return f"{commit_type}: rename file{'s' if len(changes['renamed']) > 1 else ''}"
        
        return f"{commit_type}: update repository"

    def _generate_commit_message(self, changes: Dict[str, any], commit_type: str) -> str:
        """Generate a contextual commit message based on repository structure and changes."""
        return self._generate_contextual_commit_message(changes, commit_type)

    def _get_authors(self) -> List[Actor]:
        """Get list of authors from config or environment variable."""
        # First try to get authors from config
        if self.config and 'authors' in self.config:
            authors = []
            for author_data in self.config['authors']:
                if isinstance(author_data, dict) and 'name' in author_data and 'email' in author_data:
                    authors.append(Actor(author_data['name'], author_data['email']))
            if authors:
                return authors
        
        # Fallback to environment variable
        try:
            authors_str = os.environ.get('GIT_AUTHORS', '')
            if not authors_str:
                # Default authors if not set
                return [
                    Actor("John Doe", "john.doe@example.com"),
                    Actor("Jane Smith", "jane.smith@example.com"),
                    Actor("Developer", "dev@example.com")
                ]
            
            authors = []
            for author_pair in authors_str.split(','):
                if ':' in author_pair:
                    name, email = author_pair.strip().split(':', 1)
                    authors.append(Actor(name.strip(), email.strip()))
            
            return authors if authors else [Actor("Developer", "dev@example.com")]
            
        except Exception:
            return [Actor("Developer", "dev@example.com")]

    def _generate_realistic_commit_message(self, changes: Dict[str, any], commit_type: str, commit_index: int) -> str:
        """Generate realistic commit messages that vary based on commit index and project context."""
        structure = self._analyze_repository_structure()
        
        # Define realistic commit patterns based on project timeline and history
        commit_patterns = {
            'initial_setup': [
                "feat: initialize project structure",
                "feat: set up basic project configuration",
                "feat: create initial project skeleton",
                "feat: add project foundation",
                "feat: bootstrap project setup"
            ],
            'core_features': [
                "feat: implement core functionality",
                "feat: add main application logic",
                "feat: create primary business logic",
                "feat: implement key features",
                "feat: add essential functionality"
            ],
            'api_development': [
                "feat: add REST API endpoints",
                "feat: implement API routes",
                "feat: create API controllers",
                "feat: add API middleware",
                "feat: implement API authentication"
            ],
            'database': [
                "feat: add database models",
                "feat: implement data persistence",
                "feat: create database schema",
                "feat: add ORM configuration",
                "feat: implement data access layer"
            ],
            'frontend': [
                "feat: add user interface components",
                "feat: implement frontend views",
                "feat: create responsive design",
                "feat: add client-side functionality",
                "feat: implement user interactions"
            ],
            'testing': [
                "test: add unit tests",
                "test: implement integration tests",
                "test: add test coverage",
                "test: create test suite",
                "test: add automated tests"
            ],
            'documentation': [
                "docs: add API documentation",
                "docs: update README with usage examples",
                "docs: add code comments",
                "docs: create user guide",
                "docs: add deployment instructions"
            ],
            'configuration': [
                "config: update environment settings",
                "config: add deployment configuration",
                "config: update build settings",
                "config: add CI/CD configuration",
                "config: update package dependencies"
            ],
            'bug_fixes': [
                "fix: resolve authentication issue",
                "fix: correct data validation error",
                "fix: fix API response format",
                "fix: resolve database connection issue",
                "fix: correct frontend rendering bug"
            ],
            'performance': [
                "perf: optimize database queries",
                "perf: improve API response time",
                "perf: optimize frontend performance",
                "perf: reduce memory usage",
                "perf: improve loading speed"
            ],
            'refactoring': [
                "refactor: improve code structure",
                "refactor: extract common utilities",
                "refactor: reorganize project layout",
                "refactor: simplify complex logic",
                "refactor: improve code readability"
            ],
            'security': [
                "security: add input validation",
                "security: implement proper authentication",
                "security: fix security vulnerabilities",
                "security: add data encryption",
                "security: improve access controls"
            ]
        }
        
        # Determine commit category based on development phase and recent focus
        development_phase = structure.get('development_phase', 'initial')
        recent_focus = structure.get('recent_focus', 'setup')
        feature_areas = structure.get('feature_areas', set())
        
        # Smart category selection based on project history
        if development_phase == 'initial' or commit_index < 3:
            category = 'initial_setup'
        elif development_phase == 'feature_development':
            if 'api' in feature_areas and recent_focus == 'api':
                category = 'api_development'
            elif 'database' in feature_areas:
                category = 'database'
            elif 'frontend' in feature_areas:
                category = 'frontend'
            else:
                category = 'core_features'
        elif development_phase == 'bug_fixing':
            category = 'bug_fixes'
        elif development_phase == 'documentation':
            category = 'documentation'
        elif development_phase == 'testing':
            category = 'testing'
        elif development_phase == 'optimization':
            category = random.choice(['performance', 'refactoring'])
        else:
            # Fallback based on commit index
            if commit_index < 8:
                category = 'core_features'
            elif commit_index < 12:
                category = random.choice(['api_development', 'database', 'frontend'])
            elif commit_index < 15:
                category = random.choice(['testing', 'documentation', 'configuration'])
            else:
                category = random.choice(['bug_fixes', 'performance', 'refactoring', 'security'])
        
        # Get appropriate messages for the category
        messages = commit_patterns.get(category, commit_patterns['core_features'])
        
        # Add project-specific context based on existing patterns
        if structure['project_type'] == 'python_app':
            messages.extend([
                "feat: add Python package structure",
                "feat: implement Python modules",
                "feat: add Python dependencies"
            ])
        elif structure['project_type'] == 'web_app':
            messages.extend([
                "feat: add web framework setup",
                "feat: implement web routes",
                "feat: add web templates"
            ])
        elif structure['project_type'] == 'node_app':
            messages.extend([
                "feat: add Node.js package setup",
                "feat: implement Express routes",
                "feat: add npm dependencies"
            ])
        
        # Add context-specific messages based on recent commits
        if recent_focus == 'api':
            messages.extend([
                "feat: extend API functionality",
                "feat: add new API endpoint",
                "feat: improve API response handling"
            ])
        elif recent_focus == 'testing':
            messages.extend([
                "test: add more test coverage",
                "test: improve test reliability",
                "test: add edge case tests"
            ])
        elif recent_focus == 'documentation':
            messages.extend([
                "docs: improve existing documentation",
                "docs: add missing documentation",
                "docs: update API documentation"
            ])
        
        return random.choice(messages)

    def _create_realistic_file_content(self, file_path: str, commit_index: int) -> str:
        """Create realistic file content based on file type and commit context."""
        ext = self._get_file_extension(file_path)
        
        if ext == '.py':
            return self._generate_python_content(file_path, commit_index)
        elif ext in ['.js', '.ts']:
            return self._generate_javascript_content(file_path, commit_index)
        elif ext == '.md':
            return self._generate_markdown_content(file_path, commit_index)
        elif ext in ['.json', '.yaml', '.yml']:
            return self._generate_config_content(file_path, commit_index)
        else:
            return f"# {file_path}\n\nContent added in commit {commit_index}\nGenerated at {datetime.now()}\n"

    def _generate_python_content(self, file_path: str, commit_index: int) -> str:
        """Generate realistic Python file content."""
        if 'test' in file_path.lower():
            return f'''import unittest
from unittest.mock import Mock, patch

class Test{file_path.split('/')[-1].replace('.py', '').title().replace('_', '')}(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        self.assertTrue(True)
    
    def test_edge_cases(self):
        """Test edge cases."""
        self.assertIsNotNone(None)

if __name__ == '__main__':
    unittest.main()
'''
        elif 'model' in file_path.lower():
            return f'''class {file_path.split('/')[-1].replace('.py', '').title().replace('_', '')}:
    """Model class for {file_path.split('/')[-1].replace('.py', '')}."""
    
    def __init__(self):
        self.id = None
        self.created_at = None
        self.updated_at = None
    
    def save(self):
        """Save the model."""
        pass
    
    def delete(self):
        """Delete the model."""
        pass
'''
        else:
            return f'''"""
{file_path.split('/')[-1].replace('.py', '').title().replace('_', '')} module.

This module provides functionality for {file_path.split('/')[-1].replace('.py', '').lower().replace('_', ' ')}.
"""

def main():
    """Main function."""
    print("Hello from {file_path}")

if __name__ == "__main__":
    main()
'''

    def _generate_javascript_content(self, file_path: str, commit_index: int) -> str:
        """Generate realistic JavaScript file content."""
        filename = file_path.split('/')[-1].replace('.js', '').replace('.ts', '')
        if 'test' in file_path.lower():
            return f'''const {{ expect }} = require('chai');

describe('{filename}', () => {{
    it('should work correctly', () => {{
        expect(true).to.be.true;
    }});
    
    it('should handle edge cases', () => {{
        expect(null).to.be.null;
    }});
}});
'''
        else:
            # Use string formatting to avoid f-string issues with curly braces
            display_name = filename.replace('_', ' ').upper()
            description = filename.replace('_', ' ').lower()
            return f'''/**
 * {display_name}
 * 
 * This module provides functionality for {description}.
 */

function main() {{
    console.log('Hello from {file_path}');
}}

module.exports = {{ main }};
'''

    def _generate_markdown_content(self, file_path: str, commit_index: int) -> str:
        """Generate realistic Markdown content."""
        if 'readme' in file_path.lower():
            return f'''# {file_path.split('/')[-1].replace('.md', '').title().replace('_', ' ')}

This is the README file for the project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
npm install
```

## Usage

```javascript
const app = require('./app');
app.start();
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct.

## License

This project is licensed under the MIT License.
'''
        else:
            return f'''# {file_path.split('/')[-1].replace('.md', '').title().replace('_', ' ')}

This document provides information about {file_path.split('/')[-1].replace('.md', '').lower().replace('_', ' ')}.

## Overview

This section contains important information about the project.

## Details

- Point 1
- Point 2
- Point 3

Generated in commit {commit_index}.
'''

    def _generate_config_content(self, file_path: str, commit_index: int) -> str:
        """Generate realistic configuration file content."""
        if 'package.json' in file_path:
            return '''{
  "name": "my-project",
  "version": "1.0.0",
  "description": "A sample project",
  "main": "index.js",
  "scripts": {
    "test": "jest",
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.17.1"
  },
  "devDependencies": {
    "jest": "^27.0.0"
  }
}'''
        else:
            return f'''# Configuration file for {file_path}
# Generated in commit {commit_index}

setting1 = value1
setting2 = value2
setting3 = value3
'''

    def _create_commit(self, days_ago: int = 0, commit_index: int = 0) -> None:
        """Create a commit with realistic message generation."""
        authors = self._get_authors()
        author = random.choice(authors)
        
        # Generate commit timestamp
        commit_time = datetime.now() - timedelta(
            days=days_ago, 
            hours=random.randint(0, 23), 
            minutes=random.randint(0, 59)
        )
        commit_date = commit_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Always create a new file for each commit to ensure we have changes
        file_name = self._generate_realistic_filename(commit_index)
        dummy_path = Path(self.repo.working_dir) / file_name
        
        # Ensure the file doesn't already exist
        counter = 1
        while dummy_path.exists():
            name, ext = os.path.splitext(file_name)
            file_name = f"{name}_v{counter}{ext}"
            dummy_path = Path(self.repo.working_dir) / file_name
            counter += 1
        
        # Create realistic content
        content = self._create_realistic_file_content(file_name, commit_index)
        with open(dummy_path, 'w') as f:
            f.write(content)
        
        # Stage the file
        self.repo.git.add(file_name)
        changes = {'added': [file_name], 'modified': [], 'deleted': [], 'renamed': []}
        
        # Generate realistic commit message
        commit_type = self._generate_commit_type(changes)
        message = self._generate_realistic_commit_message(changes, commit_type, commit_index)
        
        # Set environment for commit
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_date
        env["GIT_COMMITTER_DATE"] = commit_date
        
        # Create commit using git command to properly handle environment variables
        self.repo.git.commit(
            '-m', message,
            '--author', f'{author.name} <{author.email}>',
            env=env
        )
        
        print(f"Committed: {message} by {author.name} <{author.email}> at {commit_date}")

    def _generate_realistic_filename(self, commit_index: int) -> str:
        """Generate realistic filenames based on commit context."""
        if commit_index < 3:
            # Initial setup files
            files = ['setup.py', 'requirements.txt', 'README.md', 'config.py', 'main.py']
        elif commit_index < 8:
            # Core functionality files
            files = ['app.py', 'models.py', 'utils.py', 'helpers.py', 'core.py']
        elif commit_index < 12:
            # API and database files
            files = ['api.py', 'routes.py', 'database.py', 'schema.py', 'controllers.py']
        elif commit_index < 15:
            # Testing and documentation
            files = ['test_app.py', 'test_models.py', 'docs.md', 'CHANGELOG.md', 'CONTRIBUTING.md']
        else:
            # Bug fixes and improvements
            files = ['fix_auth.py', 'optimize_db.py', 'security.py', 'middleware.py', 'validation.py']
        
        base_file = random.choice(files)
        
        # Always make filename unique by adding commit index and timestamp
        name, ext = os.path.splitext(base_file)
        timestamp = datetime.now().strftime("%H%M%S")
        return f"{name}_{commit_index}_{timestamp}{ext}"

    def push_to_remote(self, remote: str = "origin", branch: str = "main") -> None:
        """Push changes to remote repository."""
        try:
            self.repo.git.push(remote, branch)
        except Exception as e:
            raise Exception(f"Failed to push to {remote}/{branch}: {e}")

    def _cleanup_temp_files(self) -> None:
        """Remove all temporary files created during the forging process."""
        try:
            # Get all files in the repository
            all_files = []
            for root, dirs, files in os.walk(self.repo.working_dir):
                # Skip .git directory
                if '.git' in root:
                    continue
                    
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), self.repo.working_dir)
                    all_files.append(file_path)
            
            # Find temporary files created by this tool
            temp_files = []
            for file_path in all_files:
                # Check if it's a temporary file created by our tool
                if any(pattern in file_path for pattern in [
                    '_0_', '_1_', '_2_', '_3_', '_4_', '_5_', '_6_', '_7_', '_8_', '_9_',
                    '_10_', '_11_', '_12_', '_13_', '_14_', '_15_', '_16_', '_17_', '_18_', '_19_',
                    '_v1', '_v2', '_v3', '_v4', '_v5'
                ]):
                    temp_files.append(file_path)
            
            # Remove temporary files
            for temp_file in temp_files:
                try:
                    file_path = Path(self.repo.working_dir) / temp_file
                    if file_path.exists():
                        file_path.unlink()
                        print(f"Cleaned up: {temp_file}")
                except Exception as e:
                    print(f"Failed to remove {temp_file}: {e}")
            
            if temp_files:
                print(f"Cleaned up {len(temp_files)} temporary files")
            else:
                print("No temporary files found to clean up")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def run(self, days_ago: int = 0, commits: int = 10, cleanup: bool = True) -> None:
        """Run the git strategy to create commits."""
        try:
            for i in range(commits):
                self._create_commit(days_ago=days_ago, commit_index=i)
        finally:
            # Clean up temporary files after the process
            if cleanup:
                self._cleanup_temp_files()

