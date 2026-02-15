# EarthRanger Global Schema Deployment Review Tool

This project builds a global EarthRanger deployment list from one or
more conservancy schema Excel files.

It consists of two main files:

-   `build_global_schemas.py` --- Core schema filtering logic.
-   `run_build.py` --- CLI runner (handles file selection, dry runs,
    grouping, and Excel output)

------------------------------------------------------------------------

## Project Structure

    project/
    │
    ├── build_global_schemas.py   # Core schema builder logic
    ├── run_build.py              # CLI runner
    ├── schemas-borana.xlsx       # Example input file
    ├── schemas-foo.xlsx          # Another conservancy
    └── deploy_output/            # Generated Excel files (auto-created)

------------------------------------------------------------------------

## How the System Works

### build_global_schemas.py (Core Logic Engine)

**Purpose:**

Builds a filtered list of deployable schemas based on:

-   `event_is_active == True`
-   Skips False
-   Skips Blank
-   Skips `flag = system`
-   Requires valid `event_category_id`

------------------------------------------------------------------------

## Key Functions

### `parse_bool(value)`

  Excel Value    Result
  -------------- --------
  TRUE, yes, 1   True
  FALSE, no, 0   False
  Blank          None

------------------------------------------------------------------------

### `build_global_schemas(df, file_path, dry_run=True)`

Processes a single Excel file and:

-   Reads schema rows
-   Applies filtering rules
-   Returns a list of deployable schema dictionaries
-   Logs:
    -   Total rows
    -   Deployed count
    -   False count
    -   Blank count
    -   System flagged count

It does not write Excel files --- that logic is handled in
`run_build.py` to prevent duplicate outputs.

------------------------------------------------------------------------

## run_build.py (Command Line Interface)

This is the main script you run.

It:

-   Handles CLI arguments.
-   Supports manual or automatic mode.
-   Runs dry run summaries.
-   Groups results by conservancy.
-   Optionally generates Excel output files.
<!-- -   Provides colored terminal output (via `colorama`) -->

------------------------------------------------------------------------

## Installation

``` bash
pip install pandas, openpyxl, colorama
```

------------------------------------------------------------------------

## How To Run

``` bash
python run_build.py
```

------------------------------------------------------------------------

## Modes

### Auto Mode (Default)

Processes all `.xlsx` files in the current directory.

``` bash
python run_build.py
```

### Manual Mode (Single File)

``` bash
python run_build.py --mode manual --file schemas-borana.xlsx
```

------------------------------------------------------------------------

## Safety and Control Flags

### Dry Run Only (No Excel output)

``` bash
python run_build.py --dry-only
```

### Skip Confirmation in Auto Mode

``` bash
python run_build.py --no-confirm
```

### Immediate Escape

``` bash
python run_build.py --escape
```

------------------------------------------------------------------------

## What Happens During Execution

1.  File is read into pandas.
2.  `build_global_schemas()` is called.
3.  Deployable schemas are grouped by conservancy name.
4.  A global summary is printed.

------------------------------------------------------------------------

## Excel Output Generation

If confirmed:

-   A folder `deploy_output/` is created.
-   Each conservancy gets its own Excel file.

File format example:

    borana_deployed_schemas_YYYYMMDD_HHMMSS.xlsx

Each file contains:

| event_value \| schema_title \| api_version \| icon_id \| source_server
  \| schema_id \| flag \|

------------------------------------------------------------------------

## Safe Exit Options

At any interactive prompt you may type:

    exit
    quit
    q

Or press:

    Ctrl + C

------------------------------------------------------------------------

## Deployment Flow Summary

    Excel file(s)
          ↓
    pandas DataFrame
          ↓
    build_global_schemas()
          ↓
    Filtered deployable schemas
          ↓
    Grouped by conservancy
          ↓
    Dry run summary
          ↓
    (Optional) Excel generation

------------------------------------------------------------------------

## Design Philosophy

This tool is built to:

-   Prevent accidental deployments
-   Separate logic from execution
-   Make dry runs mandatory before writing
-   Provide full transparency in what gets skipped and why
-   Scale to multiple conservancies

------------------------------------------------------------------------

## Recommended Workflow

1.  Place all `schemas-*.xlsx` files in the folder

2.  Run:

    ``` bash
    python run_build.py
    ```

3.  Review the dry run summary carefully

4.  Confirm Excel generation

5.  Use generated files for review / deployment
