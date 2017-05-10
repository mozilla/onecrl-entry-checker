# Verify Kinto sets with a delta expected list
import json, yaml, requests, getpass, sys
from collections import defaultdict
from optparse import OptionParser
from pprint import pprint

def make_entry(issuer, serial):
  issuer = issuer.rstrip('\n ')
  serial = serial.rstrip('\n ')
  return "issuer: {} serial: {}".format(issuer, serial)

def find_id(dataset, ident):
  for entry in dataset['data']:
    if entry['id'] == ident:
      return entry
  return None

def main():
  defaults = defaultdict(str)
  try:
    with open (".config.yml", 'r') as ymlfile:
      dataset = yaml.load(ymlfile)
      defaults.update(dataset)
  except FileNotFoundError:
    print("No .config.yml; continuing without defaults.")

  parser = OptionParser()
  parser.add_option("-e", "--expected", dest="expected", metavar="FILE",
                    help="Expected input file", default=defaults['expected'])
  parser.add_option("-u", "--user", dest="user", help="LDAP Account Username",
                    default=defaults['user'])
  parser.add_option("-H", "--host", dest="host", help="Hostname",
                    default=defaults['host'])
  parser.add_option("-S", "--staging-endpoint", dest="stagingendpoint", help="Path at the host for staging",
                    default=defaults['stagingendpoint'])
  parser.add_option("-P", "--prod-endpoint", dest="prodendpoint", help="Path at the host for production",
                    default=defaults['prodendpoint'])
  parser.add_option("-l", "--livelist", dest="livelist", help="Live blocklist",
                    default=defaults['livelist'])
  parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")
  parser.add_option("-d", "--debug",
                    action="store_true", dest="debug", default=False,
                    help="Start debugger after run")
  (options, args) = parser.parse_args()

  if options.expected == "":
    print("You must specify an expected file")
    parser.print_help()
    sys.exit(1)

  if options.host == "":
    print("You must specify a host")
    parser.print_help()
    sys.exit(1)

  if options.stagingendpoint == "":
    print("You must specify a staging endpoint")
    parser.print_help()
    sys.exit(1)

  if options.user == "":
    print("You must specify a user")
    parser.print_help()
    sys.exit(1)

  if options.livelist == "":
    print("You must specify a livelist")
    parser.print_help()
    sys.exit(1)

  expected = set()
  with open(options.expected) as expected_data:
    for line in expected_data.readlines():
      parts=line.strip().split(" ")
      expected.add(make_entry(parts[1], parts[3]))

  liveentries = set()
  liveids = set()
  livereq = requests.get(options.livelist)
  livelist_dataset = livereq.json()
  if 'data' not in livelist_dataset:
    raise Exception("Invalid livelist, or something else. Details: {}".format(livereq.content))

  for entryData in livelist_dataset['data']:
    liveentries.add(make_entry(entryData['issuerName'], entryData['serialNumber']))
    liveids.add(entryData['id'])

  print("LDAP account password for {}:".format(options.user))
  auth = (options.user, getpass.getpass())
  payload = {
    "_sort": "-last_modified",
    "_limit": 9999
  }

  found = set()
  update_url = "https://{}{}".format(options.host, options.stagingendpoint)

  updatereq = requests.get(update_url, auth=auth, params=payload)
  update_dataset = updatereq.json()
  if 'data' not in update_dataset:
    raise Exception("Invalid login, or something else. Details: {}".format(updatereq.content))

  for entryData in update_dataset['data']:
    found.add(make_entry(entryData['issuerName'], entryData['serialNumber']))

  prod_url = "https://{}{}".format(options.host, options.prodendpoint)

  prod = set()
  prodreq = requests.get(prod_url, auth=auth, params=payload)
  prod_dataset = prodreq.json()
  if 'data' not in prod_dataset:
    raise Exception("Invalid login, or something else. Details: {}".format(prodreq.content))
  for entryData in prod_dataset['data']:
    prod.add(make_entry(entryData['issuerName'], entryData['serialNumber']))

  if liveentries | expected == found:
    print("The Kinto dataset found at {} equals the union of the expected file and the live list.".format(update_url))
    # return

  deleted = prod-found
  notfound = expected-found
  missing = liveentries-(found-expected)

  print("")
  print("Dataset contains {} added entries".format(len(found)))
  print("")

  print("Expected, but not found in Kinto:")
  pprint(sorted(notfound))

  print("Found live, but missing in Kinto:")
  pprint(sorted(missing))

  if len(deleted) > 0 and deleted == missing:
    print("The missing entries {} are all deleted.".format(len(deleted)))

    for deletedEntry in deleted:
      found = False
      for entryData in prod_dataset['data']:
        if deletedEntry == make_entry(entryData['issuerName'], entryData['serialNumber']):
          found = True
          print("Deleted ID: {} Serial: {}".format(entryData['id'], entryData['serialNumber']))
          break
      if not found:
        raise("Missing entry?")

  if options.debug:
    print("Variables available:")
    print("  prod - located in Kinto production")
    print("  expected - from the file on disk")
    print("  found - located in Kinto changeset")
    print("  liveentries - located in the live CDN list")
    import pdb; pdb.set_trace()

if __name__ == "__main__":
  main()