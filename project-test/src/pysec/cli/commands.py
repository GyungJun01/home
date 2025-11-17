"""
CLI commands for pysec scanner
TAG-REQ-SEC-002: CLI interface
TAG-REQ-SEC-005: Scan execution
TAG-REQ-SEC-007: Invalid path handling
TAG-REQ-SEC-008: Bandit execution failure handling
TAG-REQ-SEC-009: Progress display
TAG-REQ-SEC-010: JSON output option
TAG-REQ-SEC-011: Severity filtering option
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from pysec.reporter.json_reporter import JsonReporter
from pysec.reporter.text_reporter import TextReporter
from pysec.scanner.bandit_engine import BanditScanner

app = typer.Typer(
    name="pysec",
    help="Python Security Scanner MVP - SAST with Bandit",
    add_completion=True,
)

console = Console()


@app.command()
def scan(
    target_path: Annotated[
        Path,
        typer.Argument(
            help="Target path to scan (directory or file)",
            exists=True,
            file_okay=True,
            dir_okay=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format (text or json)",
        ),
    ] = "text",
    severity: Annotated[
        str,
        typer.Option(
            "--severity",
            "-s",
            help="Filter by severity level (ALL, HIGH, MEDIUM, LOW)",
        ),
    ] = "ALL",
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output file path (default: stdout)",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging",
        ),
    ] = False,
) -> None:
    """
    Scan Python project for security vulnerabilities using Bandit SAST.

    TAG-REQ-SEC-002: CLI interface
    TAG-REQ-SEC-005: Scan execution event
    TAG-REQ-SEC-007: Invalid path handling
    TAG-REQ-SEC-008: Bandit execution failure handling
    TAG-REQ-SEC-009: Progress display
    TAG-REQ-SEC-010: JSON output option
    TAG-REQ-SEC-011: Severity filtering option
    """
    # TAG-REQ-SEC-005: Scan execution event
    # TAG-REQ-SEC-009: Progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("🔍 Starting security scan...", total=None)

        # Step 1: Initialize scanner (TAG-REQ-SEC-001)
        scanner = BanditScanner()

        if verbose:
            console.print(f"[dim]Scanning: {target_path}[/dim]")
            console.print(f"[dim]Format: {format}, Severity filter: {severity}[/dim]")

        # Step 2: Execute Bandit scan (TAG-REQ-SEC-001, TAG-REQ-SEC-008)
        try:
            progress.update(task, description="⚙️  Running Bandit scanner...")
            result = scanner.scan(target_path)

            if verbose:
                console.print(f"[dim]Bandit exit code: {result.exit_code}[/dim]")

        except RuntimeError as e:
            # TAG-REQ-SEC-008: Bandit execution failure handling
            console.print(f"[red]❌ Scan failed: {e}[/red]")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  1. Ensure Bandit is installed: pip install bandit")
            console.print("  2. Check if target path is readable")
            console.print("  3. Try running with --verbose flag")
            raise typer.Exit(code=2) from e

        # Step 3: Parse results (TAG-REQ-SEC-006)
        progress.update(task, description="📋 Parsing results...")

        try:
            issues = scanner.parse_results(result.stdout)
        except ValueError as e:
            console.print(f"[red]❌ Failed to parse Bandit output: {e}[/red]")
            if verbose:
                console.print(f"[dim]Raw output: {result.stdout[:500]}[/dim]")
            raise typer.Exit(code=2) from e

        # Step 4: Apply severity filter (TAG-REQ-SEC-011)
        if severity != "ALL":
            issues = [i for i in issues if i.severity == severity.upper()]

            if verbose:
                console.print(f"[dim]Filtered to {len(issues)} {severity} issues[/dim]")

        # Step 5: Generate report (TAG-REQ-SEC-003, TAG-REQ-SEC-010)
        progress.update(task, description="📄 Generating report...")

        report_output: str
        if format.lower() == "json":
            json_reporter = JsonReporter()
            report_output = json_reporter.format(issues, str(target_path))
        else:
            text_reporter = TextReporter()
            report_output = text_reporter.format(issues)

    # Step 6: Output report
    if output:
        # Save to file
        try:
            output.write_text(report_output, encoding="utf-8")
            console.print(f"[green]✅ Report saved to: {output}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to write output file: {e}[/red]")
            raise typer.Exit(code=2) from e
    else:
        # Print to stdout
        console.print(report_output)

    # Step 7: Exit with appropriate code
    # Exit code 1 if issues found (standard for security tools)
    # Exit code 0 if no issues found
    if issues:
        raise typer.Exit(code=1)
    else:
        console.print("\n[green]✅ No security issues detected![/green]")
        raise typer.Exit(code=0)


def main() -> None:
    """Main entry point for CLI"""
    app()


if __name__ == "__main__":
    main()
