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

    def _generate_commit_message(self, changes: Dict[str, any], commit_type: str) -> str:
        """Generate a conventional commit message based on changes."""
        all_files = changes['added'] + changes['modified'] + changes['deleted']
        if changes['renamed']:
            all_files.extend([old for old, new in changes['renamed']])
        
        if not all_files:
            return f"{commit_type}: update repository"
        
        # Categorize files
        categories = self._categorize_files(all_files)
        
        # Generate message based on file types and changes
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

    def _create_commit(self, days_ago: int = 0) -> None:
        """Create a commit with smart message generation."""
        authors = self._get_authors()
        author = random.choice(authors)
        
        # Analyze changes
        changes = self._analyze_changes()
        commit_type = self._generate_commit_type(changes)
        message = self._generate_commit_message(changes, commit_type)
        
        # Generate commit timestamp
        commit_time = datetime.now() - timedelta(
            days=days_ago, 
            hours=random.randint(0, 23), 
            minutes=random.randint(0, 59)
        )
        commit_date = commit_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Stage changes
        try:
            self.repo.git.add(A=True)
        except Exception:
            # If no changes to add, create a dummy file
            dummy_file = f"temp_{random.randint(1000, 9999)}.txt"
            with open(dummy_file, 'w') as f:
                f.write(f"Temporary file created at {datetime.now()}")
            self.repo.git.add(dummy_file)
        
        # Set environment for commit
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_date
        env["GIT_COMMITTER_DATE"] = commit_date
        
        # Create commit
        self.repo.index.commit(
            message,
            author=author,
            committer=author,
            env=env
        )
        
        print(f"Committed: {message} by {author.name} <{author.email}> at {commit_date}")

    def push_to_remote(self, remote: str = "origin", branch: str = "main") -> None:
        """Push changes to remote repository."""
        try:
            self.repo.git.push(remote, branch)
        except Exception as e:
            raise Exception(f"Failed to push to {remote}/{branch}: {e}")

    def run(self, days_ago: int = 0, commits: int = 10) -> None:
        """Run the git strategy to create commits."""
        for i in range(commits):
            self._create_commit(days_ago=days_ago)

