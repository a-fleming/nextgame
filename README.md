# nextgame

`nextgame` is a local-first Python CLI for organizing a board game collection, logging plays, and helping answer the question: what should we play tonight?

I built it because I host board game nights with friends pretty often, and I got tired of trying to remember which games support the number of people coming, fit within the time we have, and match the kind of game night we want. I wanted something simple that could narrow the list down quickly. It also felt like the kind of tool that could be useful in a board game shop or cafe, where someone might need to recommend games based on player count, time, or general preferences.

## What it does

You can store games with details like supported player counts, estimated play time, weight, and tags. Tags in `nextgame` are simple descriptors for mechanics, themes, or categories, such as `cooperative`, `deck builder`, `party game`, or `hidden roles`.

You can get recommendations based on player count, with optional time, weight, and tag preferences to narrow the results further.

You can also log play sessions for games you have played, and that history is factored into the recommendation scoring so recently played or frequently played games do not always rise to the top.

There is also a demo mode with seeded data if you want to try the CLI without building a library from scratch.

## Tech stack and project design

The stack is intentionally small and straightforward:

- Python 3.12
- `argparse` for the CLI
- SQLite via the standard library `sqlite3` module
- SQL stored in `.sql` files under `src/nextgame/db/sql/`
- thin Python query wrappers under `src/nextgame/db/queries/`
- migrations applied automatically when the database is opened
- pytest for tests
- setuptools entrypoint so the CLI can be installed as `nextgame`

There are no runtime third-party dependencies right now. Most of the project is built on the standard library.

## Project structure

```text
nextgame/
├── pyproject.toml          # package metadata, CLI entrypoint, dev dependencies
├── src/nextgame/
│   ├── cli.py             # top-level argparse setup
│   ├── config.py          # default paths and env-based settings
│   ├── runtime_setup.py   # logging setup
│   ├── validation.py      # shared argument validation helpers
│   ├── commands/          # command handlers
│   ├── parsers/           # parser/subcommand definitions
│   ├── db/
│   │   ├── connection.py  # sqlite connection and PRAGMA setup
│   │   ├── migrations.py  # schema migration runner
│   │   ├── queries/       # Python wrappers around SQL queries
│   │   └── sql/           # raw SQL for schema and queries
│   └── data/
│       └── demo_seed.json # sample data for demo mode
└── tests/
    └── test_validation.py # validation-focused pytest coverage
```

## Installation

First, clone the repository and move into the project directory:

```bash
git clone https://github.com/a-fleming/nextgame.git
cd nextgame
```

You can run this project with either `uv` or plain `pip`.

### Option 1 (recommended): using `uv`

```bash
uv sync --dev
source .venv/bin/activate
nextgame --help
```

### Option 2: using `venv` + `pip`

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
nextgame --help
```

If you want to run it straight from source before installing the entrypoint:

```bash
PYTHONPATH=src python -m nextgame --help
```

## Local database and config

By default, `nextgame` stores data under your home directory:

- database: `~/.nextgame/nextgame.db`
- log file: `~/.nextgame/nextgame.log`

You can override the database path with:

- `--db-path`
- `NEXTGAME_DB_PATH`

You can override the log path with:

- `NEXTGAME_LOG_PATH`

## Quickstart

Create a database:

```bash
nextgame init
```

Add some tags:

```bash
nextgame tag add cooperative "engine builder" "party game"
```

Add a couple of games:

```bash
nextgame game add "Terraforming Mars" --players 1-5 --time 120 --weight 3.2 --tags cooperative "engine builder"
nextgame game add Codenames --players 2-8 --time 15 --weight 1.3 --tags "party game"
```

List your library:

```bash
nextgame game list --with-tags
```

Log a play session:

```bash
nextgame log add "Terraforming Mars" --date 2026-04-08 --players 4 --time 135
```

Ask for a recommendation:

```bash
nextgame recommend 4 --time 60-150 --max-weight 3.5 --include-tags "engine builder"
```

## Major commands

### `nextgame init`

Initialize the database and apply any unapplied migrations.

```bash
nextgame init
nextgame init --db-path ./test.db
```

### `nextgame game`

Manage the game library.

```bash
nextgame game add Catan --players 3-4 --time 60 --tags trading economic --weight 2.3
nextgame game list
nextgame game list --with-tags
nextgame game search --players 4 --include-tags cooperative
nextgame game tag add Catan trading
nextgame game tag remove Catan trading
nextgame game delete --name Catan
```

### `nextgame tag`

Manage reusable tags.

```bash
nextgame tag add cooperative "deck builder" "party game"
nextgame tag list
nextgame tag delete cooperative
nextgame tag delete "party game" --force
```

### `nextgame log`

Track what actually gets played.

```bash
nextgame log add Pandemic --date 2026-04-08 --players 4 --time 55
nextgame log list
nextgame log delete 3 4
```

### `nextgame recommend`

Recommend games for a specific player count using soft preferences.

```bash
nextgame recommend 4
nextgame recommend 4 --time 45-90
nextgame recommend 5 --include-tags deduction cooperative
nextgame recommend 4 --exclude-tags "take that"
nextgame recommend 3 --time 45-90 --min-weight 2.0 --max-weight 3.5 --include-tags cooperative
```

### `nextgame demo`

Load a demo database with seeded games, tags, and session history.

```bash
nextgame demo start
nextgame demo stop
```

## Recommendation logic

The recommendation command uses one hard rule and a few softer signals.

- Player count is the hard filter. If a game does not support the requested number of players, it is out.
- Time, weight, included tags, and excluded tags all affect ranking as soft preferences.
- Recently played games are penalized.
- Games with more logged sessions are also penalized a bit so the same titles do not always float to the top.

That makes `recommend` different from `game search`.

- `game search` is for filtering
- `recommend` is for ranking likely good options for a game night

## Migrations and query layer

Schema setup is handled with SQL migration files under `src/nextgame/db/sql/schema/`.

Right now the project includes:

- `001_init.sql`

SQL lives in `.sql` files, and small Python wrappers load and execute those queries. There are also a couple of helpers for dynamic `IN (...)` and optional `WHERE` clause construction, which keeps the search and lookup code flexible without pulling in an ORM.

## Testing

The project uses pytest.

Current tests focus on validation and option-conflict rules, including:

- date parsing and leap year behavior
- numeric validation
- player/time range validation
- tag normalization
- include/exclude conflict checks
- min/max weight conflict checks


If you are using the recommended `uv` setup, run:

```bash
uv run pytest
```

If you are using `venv` + `pip`, run pytest through the active Python environment:

```bash
python -m pytest
```

## Lessons learned

A few things this project pushed me to get better at:

- Designing a CLI that still feels understandable as the number of commands, flags, and argument combinations grows
- Deciding what should be validated by the parsers, what belongs in the command logic, and what should be enforced by the database
- Using SQLite more like a real application datastore, including migrations, foreign keys, transactions, and organizing SQL in separate files that still integrate cleanly with the Python query layer
- Building recommendation logic around practical tradeoffs, like what should be a hard filter, what should affect scoring, and how to handle incomplete data
- Using tests to catch edge cases and confirm that validation logic behaves the way I intended

## Future improvements

Some directions I would like to explore next:

- BoardGameGeek API integration
- importing game data from external catalogs
- recommendations for games to buy that are not already owned
- CSV or JSON import/export for games, sessions, and tags
- a `--details` mode for recommendation scoring
- richer play stats and reporting
- a lightweight UI or web version built on top of the same local database

## Closing

`nextgame` started as a tool for my own board game nights, but it turned into a solid little project to build out properly. It stays pretty manageable in scope, but it still gave me room to work on packaging, CLI design, validation, migrations, SQL organization, testing, and recommendation logic.
