import logging
from typing import List, Dict, Optional
import pandas as pd
import os

logger = logging.getLogger(__name__)


def parse_bool(value) -> Optional[bool]:
    """
    Convert a value to True/False/None:
    - True, 'true', 'yes', '1' → True
    - False, 'false', 'no', '0' → False
    - Blank / anything else → None
    """
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val_lower = value.strip().lower()
        if val_lower in {"true", "yes", "1"}:
            return True
        elif val_lower in {"false", "no", "0"}:
            return False
    return None


def write_global_schemas(
    schemas: List[Dict],
    output_path: str,
    *,
    confirm: bool = False,
) -> None:
    """
    Writes global schemas to disk.

    Protected by an explicit confirmation flag
    to prevent accidental overwrites.
    """
    if not confirm:
        raise RuntimeError(
            "Refusing to write global schemas without confirm=True "
            "(dry run protection)."
        )

    df = pd.DataFrame(schemas)
    df.to_excel(output_path, index=False)

    logger.info(
        "Wrote %d schemas to %s",
        len(schemas),
        output_path,
    )


def build_global_schemas(
    df,
    *,
    file_path: str,
    dry_run: bool = True,
    output_path: Optional[str] = None,
) -> List[Dict]:
    
    """
    Build a global EarthRanger schema list using Borana-first precedence.

    Rules:
    - Only active schemas (event_is_active=True) are considered
    - False or blank event_is_active → skipped
    - System-flagged schemas are excluded from propagation
    - Borana schema ID always wins
    """
    source_server = os.path.splitext(os.path.basename(file_path))[0]

    deployed: List[Dict] = []

    false_count = 0
    blank_count = 0
    system_count = 0

    for _, row in df.iterrows():
        event_value = row.get("event_value", "")
        schema_title = row.get("schema_title", "")
        api_version = row.get("api_version", "")
        icon_id = row.get("icon_id", "")

        is_active = parse_bool(row.get("event_is_active", ""))
        flag = str(row.get("flag", "")).strip().lower()

        # ---- Skip inactive or blank ----
        if is_active is not True:
            # status = "FALSE" if is_active is False else "BLANK"
            if is_active is not True:
               if is_active is False:
                   false_count += 1
                   status = "FALSE"
               else:
                   blank_count += 1
                   status = "BLANK"

            logger.info(f"[SKIP - {status}] {event_value} → not active")
            continue

        # ---- Skip system-flagged schemas ----
        if flag == "system":
            system_count += 1
            logger.info(f"[SKIP - SYSTEM] {event_value} → system-flagged")
            continue

        # ---- Borana-first resolution ----
        schema_id = (row.get("event_category_id") or "").strip()
        
        if not schema_id:
            logger.warning(f"[SKIP] {event_value} → no schema ID")
            continue

        deployed.append(
            {
                "event_value": event_value,
                "schema_title": schema_title,
                "api_version": api_version,
                "icon_id": icon_id,
                "source_server": source_server,
                "schema_id": schema_id,
                "flag": flag,
            }
        )

    # ---- DRY RUN / WRITE CONTROL ----
    if dry_run:
        deployed_count = len(deployed)
        total_count = len(df)
        skipped_total = total_count - deployed_count
        
        logger.info(
            "DRY RUN enabled — \n"
            "-----------------------------\n"
            "TOTALS\n"
            "-----------------------------\n"
            f"Total schemas: {total_count}\n"
            f"Deployed: {deployed_count}\n"
            f"False: {false_count}\n"
            f"Blank: {blank_count}\n"
            f"System flagged: {system_count}"
        )
        return deployed

# ----LOGIC MOVED TO run_build TO PREVENT DUPLICATES OF GENERATED EXCEL FILES----
    # if output_path is None:
    #     raise ValueError("output_path must be provided when dry_run=False")

    # write_global_schemas(
    #     deployed,
    #     output_path,
    #     confirm=True,
    # )

    return deployed
