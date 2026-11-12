<p align="center">
  <img src="assets/banner.svg" alt="mdtoc" width="800">
</p>

**mdtoc** generates and keeps up to date a table of contents for your Markdown files. One Python file, zero dependencies, GitHub-style anchors, and a `--check` mode for CI.

## Features

- GitHub-compatible heading anchors (including duplicate headings)
- Ignores headings inside fenced code blocks
- Configurable heading depth
- Updates the TOC in place between two markers
- `--check` exits with code 1 when the TOC is stale, so you can fail a CI job

## Install

No install needed. Download `mdtoc.py` and run it with Python 3.8+:

```bash
curl -O https://raw.githubusercontent.com/ERROR404DTIR/mdtoc/main/mdtoc.py
python3 mdtoc.py --help
```

## Usage

Add the markers where you want the table of contents:

```markdown
<!-- toc -->
<!-- tocstop -->
```

Then run:

```bash
python3 mdtoc.py README.md            # print the TOC to stdout
python3 mdtoc.py README.md --write    # update the block in place
python3 mdtoc.py README.md --check    # CI: exit 1 if outdated
python3 mdtoc.py docs/*.md -w --min 2 --max 3
```

## Options

| Option | Description |
| --- | --- |
| `--min N` | Shallowest heading level to include (default `2`) |
| `--max N` | Deepest heading level to include (default `4`) |
| `-w`, `--write` | Update files in place |
| `-c`, `--check` | Exit 1 if any TOC is out of date |

## Example CI step

```yaml
- run: python3 mdtoc.py README.md --check
```

## License

MIT
