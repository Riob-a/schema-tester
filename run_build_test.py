import logging
import pandas as pd
import glob
import os
import argparse
from datetime import datetime
from collections import defaultdict
from build_global_schemas import build_global_schemas


# ---- logging setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


def safe_input(message: str) -> str:
    """
    Wrapper around input() that allows global escape keywords.
    """
    value = input(message).strip().lower()

    if value in {"exit", "quit", "q"}:
        print("\n⚠ Execution manually aborted by user.")
        raise SystemExit(0)

    return value


def main():
    # ---- argument parsing ----
    parser = argparse.ArgumentParser(description="Dry run schema deployment")

    parser.add_argument(
        "--mode",
        choices=["manual", "auto"],
        default="auto",
        help="Choose manual (single file) or auto (all .xlsx files in folder)"
    )

    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to Excel file (required if mode is set to manual)"
    )

    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution in auto mode)"
    )

    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Actually write output Excel file (disables dry run)"
    )

    parser.add_argument(
        "--prompt-deploy",
        action="store_true",
        help="Prompt the user after dry run to generate Excel files"
    )

    parser.add_argument(
        "--escape",
        action="store_true",
        help="Immediately stop execution before deployment logic"
    )

    parser.add_argument(
        "--dry-only",
        action="store_true",
        help="Run dry run only and skip deployment"
    )

    args = parser.parse_args()

    # ---- Global escape ----
    if args.escape:
        print("⚠ Escape flag detected. Stopping execution.")
        return

    # ---- Interactive confirmation for auto mode ----
    if args.mode == "auto" and not args.no_confirm:
        print("Auto mode will process all .xlsx files in the current folder.")

        confirm = safe_input(
            "Do you want to continue? (y/n) "
            "[type exit, quit, or q to stop]: "
        )

        if confirm != "y":
            print("Switching to manual mode...")
            args.mode = "manual"

    # ---- Ask for file path if manual and not provided ----
    if args.mode == "manual" and not args.file:
        last_dir = os.getcwd()

        while True:
            file_input = safe_input(
                f"Enter path to Excel file for manual mode [{last_dir}] "
                "[type exit, quit, or q to stop]: "
            )

            if not file_input:
                print("Please provide a valid Excel file path.")
                continue

            file_input = os.path.expanduser(file_input)

            if not os.path.isabs(file_input):
                file_input = os.path.join(last_dir, file_input)

            if os.path.isfile(file_input):
                args.file = file_input
                last_dir = os.path.dirname(file_input)
                break
            else:
                print(f"File not found: {file_input}. Please enter a valid path.")

    # ---- Prepare Excel files ----
    if args.mode == "manual":
        if not args.file:
            raise ValueError("Manual mode requires --file argument.")
        if not os.path.isfile(args.file):
            raise FileNotFoundError(f"File not found: {args.file}")
        excel_files = [args.file]
    else:
        excel_files = [f for f in glob.glob("*.xlsx") if not f.startswith("~$")]
        if not excel_files:
            raise FileNotFoundError("No Excel file found in directory for auto mode.")

    # ---- Dry run variables ----
    grouped_deployed = defaultdict(list)
    total_rows = 0

    # ---- Process files ----
    for file_path in excel_files:
        print(f"\nProcessing: {file_path}")

        df = pd.read_excel(file_path)
        total_rows += len(df)
        
        output_file = "global_deployed_schemas.xlsx"
        deployed = build_global_schemas(df, file_path=file_path, dry_run=True)

        conservancy = os.path.splitext(file_path)[0].replace("schemas-", "")
        grouped_deployed[conservancy].extend(deployed)

    # ---- Global summary ----
    print("\n==============================")
    print("GLOBAL DRY RUN SUMMARY")
    print("==============================")

    total_deployed = sum(len(v) for v in grouped_deployed.values())

    print(f"Total schemas processed: {total_rows}")
    print(f"Total schemas deployable: {total_deployed}")
    print("------------------------------")
    
    # ---- Grouped Results ----
    for conservancy in sorted(grouped_deployed.keys()):
        schemas = grouped_deployed[conservancy]

        if not schemas:
            continue

        print(f"\n--- {conservancy.upper()} ---")
        print(f"Deployed: {len(schemas)}")
        print("---------------------------")
        
        # Optional: sort schemas alphabetically by event_value
        schemas_sorted = sorted(schemas, key=lambda x: x["event_value"])

        for schema in schemas_sorted:
            print(f"{schema['event_value']} | {schema['schema_id']}")

    # ---- Dry-only exit ----
    if args.dry_only:
        print("\nDry run complete. Skipping Excel generation (--dry-only).")
        return

    # ---- Prompt user to generate Excel files ----
    if grouped_deployed:
        user_input = input(
            "\nDo you want to generate Excel files for all deployable schemas? (y/n): "
        )

        if user_input == "y":

            output_dir = "deploy_output"
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for conservancy, schemas in grouped_deployed.items():

                if not schemas:
                    continue

                df_out = pd.DataFrame(schemas)

                output_path = os.path.join(
                    output_dir,
                    f"{conservancy}_deployed_schemas_{timestamp}.xlsx"
                )

                df_out.to_excel(output_path, index=False)

                print(f"Generated: {output_path}")
        else:
            print("\n⚠ Excel generation skipped.")
    else:
        print("\n⚠ No deployable schemas — nothing to write.")


# ---- Graceful Ctrl+C handling ----
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Execution cancelled by user (Ctrl+C).")
        raise SystemExit(0)
