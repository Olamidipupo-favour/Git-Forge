import click
import json
from pathlib import Path
from strategies import GitStrategy
from typing import Optional, Dict, Any



def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"Config file {config_path} not found. Using defaults.", err=True)
        return {}
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON in config file: {e}", err=True)
        raise click.Abort()


@click.command()
@click.option(
    '--config', 
    '-c', 
    default='commit_config.json', 
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    help='Path to configuration file (default: commit_config.json)'
)
@click.option(
    '--repo-path', 
    '-p', 
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help='Override repository path from config'
)
@click.option(
    '--commits', 
    type=int, 
    help='Override number of commits from config'
)
@click.option(
    '--days-spread', 
    type=int, 
    help='Override days spread from config'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be done without actually creating commits'
)
@click.option(
    '--no-cleanup',
    is_flag=True,
    help='Keep temporary files after the process (default: cleanup automatically)'
)
def main(
    config: Path,
    repo_path: Optional[Path],
    commits: Optional[int],
    days_spread: Optional[int],
    dry_run: bool,
    no_cleanup: bool
) -> None:
    """
    GitMod - Generate fake git commits for testing and demonstration purposes.
    
    This tool creates fake commits in a git repository with smart, conventional
    commit messages. Configuration is loaded from commit_config.json by default.
    """
    try:
        # Load configuration
        config_data = load_config(config)
        
        # Apply CLI overrides
        final_repo_path = repo_path or Path(config_data.get('repo_path', '.'))
        final_commits = commits or config_data.get('commits', 10)
        final_days_spread = days_spread or config_data.get('days_spread', 10)
        
        # Validate configuration
        if not final_repo_path.exists():
            click.echo(f"Repository path does not exist: {final_repo_path}", err=True)
            raise click.Abort()
        
        if final_commits <= 0:
            click.echo("Number of commits must be positive", err=True)
            raise click.Abort()
        
        if final_days_spread < 0:
            click.echo("Days spread cannot be negative", err=True)
            raise click.Abort()
        
        if dry_run:
            click.echo(f"Would create {final_commits} commits in {final_repo_path}")
            click.echo(f"Spread over {final_days_spread} days")
            if config_data.get('authors'):
                click.echo(f"Using {len(config_data['authors'])} authors from config")
            if config_data.get('push'):
                click.echo(f"Would push to {config_data.get('remote', 'origin')}/{config_data.get('branch', 'main')}")
            return
        
        # Initialize strategy with config
        strategy = GitStrategy(str(final_repo_path), config_data)

        # Run the strategy
        strategy.run(days_ago=final_days_spread, commits=final_commits, cleanup=not no_cleanup)
        
        click.echo(f"Successfully created {final_commits} commits in {final_repo_path}")
        
        # Handle push if configured
        if config_data.get('push', False):
            try:
                strategy.push_to_remote(
                    remote=config_data.get('remote', 'origin'),
                    branch=config_data.get('branch', 'main')
                )
                click.echo(f"Pushed changes to {config_data.get('remote', 'origin')}/{config_data.get('branch', 'main')}")
            except Exception as e:
                click.echo(f"Failed to push changes: {e}", err=True)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()