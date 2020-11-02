# Verify Kinto sets to ensure coherency between Stage and Prod, and all affected buckets

import requests, base64, io, itertools
from collections import UserList
from rich import console, table

console = console.Console()

base_prod="https://settings.prod.mozaws.net/v1"
base_stage="https://settings.stage.mozaws.net/v1"

bucket_staging="security-state-staging"
bucket_preview="security-state-preview"
bucket_publish="security-state"

def canonicalize(s):
  return s.strip("\n ")

def make_entry(**data):
  if "issuerName" in data and "serialNumber" in data:
    data["issuer"] = data["issuerName"]
    data["serial"] = data["serialNumber"]
  if "issuer" in data and "serial" in data:
    return {
      "issuer": canonicalize(data['issuer']),
      "serial": canonicalize(data['serial'])
    }
  if "pubKeyHash" in data and "subject" in data:
    return {
      "pubKeyHash": canonicalize(data['pubKeyHash']),
      "subject": canonicalize(data['subject'])
    }
  raise Exception(f"Unexpected entry components {data}")

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
      raise Exception(f"{left} and {right} are not equivalent, mismatch on {entry}")

class Records(UserList):
  def __init__(self, base, bucket, data):
    self.base = base
    self.bucket = bucket
    self.data = [ make_entry(**entry) for entry in data ]

  def __str__(self):
    name = "stage" if "stage" in self.base else "prod"
    return f"{name}/{self.bucket} ({len(self)})"

def get_records(base, bucket):
  url = f"{base}/buckets/{bucket}/collections/onecrl/records"
  rsp = requests.get(url)
  results = rsp.json()
  if 'data' in results:
    return Records(base, bucket, results['data'])
  raise Exception(f"Unexpected struct reading from {url}: {results}")

def main():
  stage_stage = get_records(base_stage, bucket_staging)
  stage_preview = get_records(base_stage, bucket_preview)
  stage_publish = get_records(base_stage, bucket_publish)

  console.log(f"Stage-Stage: {len(stage_stage)} Stage-Preview: {len(stage_preview)} Stage-Published: {len(stage_publish)}")

  prod_stage = get_records(base_prod, bucket_staging)
  prod_preview = get_records(base_prod, bucket_preview)
  prod_publish = get_records(base_prod, bucket_publish)

  console.log(f"Prod-Stage: {len(prod_stage)} Prod-Preview: {len(prod_preview)} Prod-Published: {len(prod_publish)}")

  verify_equivalent(stage_stage, prod_stage)
  verify_equivalent(stage_preview, prod_preview)
  verify_equivalent(stage_publish, prod_publish)

  console.log("Verifying stage against preview")
  for left, right in itertools.combinations([stage_stage, stage_preview, prod_stage, prod_preview], 2):
    verify_equivalent(left, right)
    console.log(f"{left} and {right} are equivalent")

  if is_equivalent(stage_stage, stage_publish):
    console.log("No changes are waiting")
  else:
    console.log(f"There are {len(stage_stage)-len(stage_publish)} changes waiting:")

    datatable = table.Table(title="Added entries")
    for entry in stage_stage:
      if entry not in stage_publish:
        if "issuer" in entry:
          datatable.add_row(entry["issuer"], entry["serial"])
        elif "pubKeyHash" in entry:
          datatable.add_row(entry["pubKeyHash"], entry["subject"])
        else:
          raise Exception("Unexpected entry", entry)
    console.print(datatable)



if __name__ == "__main__":
  main()
