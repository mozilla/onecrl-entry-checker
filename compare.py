# Verify Kinto sets to ensure coherency between Stage and Prod, and all affected buckets

import requests, base64, io, itertools, json
from collections import Counter, UserList
from rich import console

console = console.Console()

base_prod = "https://firefox.settings.services.mozilla.com/v1"
base_stage = "https://remote-settings.allizom.org/v1"

bucket_staging = "security-state-staging"
bucket_preview = "security-state-preview"
bucket_publish = "security-state"


def make_entry(**data):
    del data["schema"]
    del data["last_modified"]
    del data["id"]
    return data


def is_equivalent(left, right):
    try:
        verify_equivalent(left, right)
    except:
        return False
    return True


def verify_equivalent(left, right):
    if len(left) != len(right):
        raise Exception(f"{left} and {right} are not equivalent, sizes differ")
    for entry in left:
        if entry not in right:
            raise Exception(
                f"{left} and {right} are not equivalent, mismatch on {entry}"
            )


class Records(UserList):
    def __init__(self, base, bucket, data):
        self.base = base
        self.bucket = bucket
        self.data = [make_entry(**entry) for entry in data]

    def __str__(self):
        name = "stage" if self.base == base_stage else "prod"
        return f"{name}/{self.bucket} ({len(self)})"


def pending_changes(stage, publish):
    """Return the entries that publishing stage would add and delete.

    Entries are compared as multisets, so that deleting one of several
    identical records is counted.
    """

    def counts(records):
        return Counter(json.dumps(entry, sort_keys=True) for entry in records)

    staged, published = counts(stage), counts(publish)
    added = [json.loads(e) for e in (staged - published).elements()]
    deleted = [json.loads(e) for e in (published - staged).elements()]
    return added, deleted


def report_pending(name, stage, publish):
    added, deleted = pending_changes(stage, publish)
    if not added and not deleted:
        console.log(f"No changes are waiting in {name}")
        return
    console.log(
        f"There are {len(added) + len(deleted)} changes waiting in {name}: "
        f"{len(added)} additions and {len(deleted)} deletions."
    )
    for label, entries in (("Adding", added), ("Deleting", deleted)):
        if entries:
            console.log(f"{label} {len(entries)} entries in {name}:")
            for entry in entries:
                console.print(entry)


def get_records(base, bucket):
    url = f"{base}/buckets/{bucket}/collections/onecrl/records"
    rsp = requests.get(url)
    results = rsp.json()
    if "data" in results:
        return Records(base, bucket, results["data"])
    raise Exception(f"Unexpected struct reading from {url}: {results}")


def main():
    stage_stage = get_records(base_stage, bucket_staging)
    stage_preview = get_records(base_stage, bucket_preview)
    stage_publish = get_records(base_stage, bucket_publish)

    console.log(
        f"Stage-Stage: {len(stage_stage)} Stage-Preview: {len(stage_preview)} Stage-Published: {len(stage_publish)}"
    )

    prod_stage = get_records(base_prod, bucket_staging)
    prod_preview = get_records(base_prod, bucket_preview)
    prod_publish = get_records(base_prod, bucket_publish)

    console.log(
        f"Prod-Stage: {len(prod_stage)} Prod-Preview: {len(prod_preview)} Prod-Published: {len(prod_publish)}"
    )

    verify_equivalent(stage_stage, prod_stage)
    verify_equivalent(stage_preview, prod_preview)

    console.log("Verifying stage against preview")
    for left, right in itertools.combinations(
        [stage_stage, stage_preview, prod_stage, prod_preview], 2
    ):
        verify_equivalent(left, right)
        console.log(f"{left} and {right} are equivalent")

    report_pending("staging", stage_stage, stage_publish)
    report_pending("production", prod_stage, prod_publish)

    if is_equivalent(stage_stage, stage_publish) and not is_equivalent(
        prod_stage, prod_publish
    ):
        console.log(
            """Staging is updated, and production changes are waiting, so Firefox can use
Remote Settings DevTools (https://github.com/mozilla-extensions/remote-settings-devtools)
and cert-storage-inspector (https://github.com/mozkeeler/cert-storage-inspector) to test
OneCRL."""
        )


if __name__ == "__main__":
    main()
