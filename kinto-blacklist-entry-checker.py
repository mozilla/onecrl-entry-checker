# Verify Kinto sets with a delta expected list
import json, yaml, requests, sys, base64, io, codecs
from xml.etree import ElementTree
from collections import defaultdict
from optparse import OptionParser
from pprint import pprint
from colorama import init, Fore

def make_entry(issuer, serial):
  issuer = issuer.rstrip('\n')
  serial = serial.rstrip('\n')
  return "issuer: {} serial: {}".format(issuer, serial)

def find_id(dataset, ident):
  for entry in dataset['data']:
    if entry['id'] == ident:
      return entry
  return None

def gIfR(condition):
  return Fore.GREEN + "[GOOD] "  if condition else Fore.RED + "[BAD] "

def main():
  init()

  defaults = defaultdict(str)
  try:
    with open (".config.yml", 'r') as ymlfile:
      dataset = yaml.load(ymlfile, Loader=yaml.BaseLoader)
      defaults.update(dataset)
  except FileNotFoundError:
    print("No .config.yml; continuing without defaults.")

  parser = OptionParser()
  parser.add_option("-e", "--expected", dest="expected", metavar="FILE",
                    help="Expected input file", default=defaults['expected'])
  parser.add_option("-b", "--bug", dest="bugnum", help="Bug #")
  parser.add_option("-H", "--host", dest="host", help="Hostname",
                    default=defaults['host'])
  parser.add_option("-S", "--staging-endpoint", dest="stagingendpoint", help="Path at the host for staging",
                    default=defaults['stagingendpoint'])
  parser.add_option("-P", "--prod-endpoint", dest="prodendpoint", help="Path at the host for production",
                    default=defaults['prodendpoint'])
  parser.add_option("-l", "--livelist", dest="livelist", help="Live blocklist",
                    default=defaults['livelist'])
  parser.add_option("-q", "--quiet",
                    action="store_true", dest="verbose", default=False,
                    help="be more verbose to stdout")
  parser.add_option("-d", "--debug",
                    action="store_true", dest="debug", default=False,
                    help="Start debugger after run")
  (options, args) = parser.parse_args()

  if options.expected == "" and options.bugnum is None:
    print("You must specify an expected file or a bug number")
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

  if options.livelist == "":
    print("You must specify a livelist")
    parser.print_help()
    sys.exit(1)

  if "-writer" not in options.host:
    print("Your host needs to be the one with -writer in its name")
    sys.exit(1)

  expected = set()
  expected_source = None

  if options.expected != "":
    expected_source = open(options.expected)
  else:
    bug_page = requests.get("https://bugzilla.mozilla.org/show_bug.cgi?ctype=xml&id={}".format(options.bugnum))
    bug = ElementTree.fromstring(bug_page.content)[0]
    for attachment in bug.findall("attachment"):
      if attachment.attrib['isobsolete'] == '0' and "BugData.txt" in attachment.find("filename").text:
        print("Downloading attachment ID {} found, dated {}".format(attachment.find("attachid").text,
                                                        attachment.find("date").text))
        utfData = codecs.decode(base64.b64decode(attachment.find("data").text))
        expected_source = io.StringIO(utfData)

  print("Intermediates to be revoked")

  with expected_source as expected_data:
    for line in expected_data.readlines():
      parts=line.strip().split(" ")
      issuer = parts[1]
      serial = parts[3]
      expected.add(make_entry(issuer, serial))

      if options.verbose:
        print("Issuer: {} Serial: {}".format(str(base64.b64decode(issuer)), base64.b16encode(base64.b64decode(serial))))

  liveentries = set()
  liveids = set()
  livereq = requests.get(options.livelist)
  livelist_dataset = livereq.json()
  if 'data' not in livelist_dataset:
    raise Exception("Invalid livelist, or something else. Details: {}".format(livereq.content))

  for entryData in livelist_dataset['data']:
    liveentries.add(make_entry(entryData['issuerName'], entryData['serialNumber']))
    liveids.add(entryData['id'])

  payload = {
    "_sort": "-last_modified",
    "_limit": 9999
  }

  found = set()
  while not found:
    print(f"We're going to need a bearer token to log into {options.host}.")
    print(f"Please log in to https://{options.host}/v1/admin/ and use devtools to find the Authorization header.")
    print("Example: Authorization: Bearer ZZkZZZxNZZZZ_0ZZZZ4ZZZZZNcZZZZ")

    token = input("> ")
    if token.startswith("Authorization: Bearer"):
      token = token.split("Bearer")[1].strip()

    headers = {"Authorization": "Bearer {}".format(token)}

    update_url = "https://{}{}".format(options.host, options.stagingendpoint)

    updatereq = requests.get(update_url, params=payload, headers=headers)
    update_dataset = updatereq.json()
    if 'data' not in update_dataset:
      print("Invalid login, or something else. URL: {} Details: {}".format(update_url, updatereq.content))
      continue

    for entryData in update_dataset['data']:
      found.add(make_entry(entryData['issuerName'], entryData['serialNumber']))

    print("Worked, downloaded {} entries from the staging list.".format(len(found)))

  prod_url = "https://{}{}".format(options.host, options.prodendpoint)

  prod = set()
  prodreq = requests.get(prod_url, params=payload)
  prod_dataset = prodreq.json()
  if 'data' not in prod_dataset:
    raise Exception("Invalid login, or something else. Details: {}".format(prodreq.content))
  for entryData in prod_dataset['data']:
    prod.add(make_entry(entryData['issuerName'], entryData['serialNumber']))

  deleted = prod-found
  notfound = expected-found
  missing = liveentries-(found|expected)

  print("")
  if options.expected != "":
    print("Evaluating expected file = '{}'".format(options.expected))
  else:
    print("Downloading intermediates to be revoked from bug # {}".format(options.bugnum))
  print("")
  print("Results:")
  print("Pending Kinto Dataset (Found): {}".format(len(found)))
  print("Added Entries (Expected): {}".format(len(expected)))
  print("{c}Expected But Not Pending (Not Found): {}".format(len(notfound), c=gIfR(len(notfound)==0)) + Fore.RESET)
  print("Deleted: {}".format(len(deleted)))
  print("{c}Entries In Production But Lost Without Being Deleted (Missing): {}".format(len(missing), c=gIfR(len(missing)==0)) + Fore.RESET)
  print("")

  if expected == found-prod:
    print(Fore.GREEN + "[GOOD] The Expected file matches the change between the staged Kinto and production." + Fore.RESET)
  else:
    print(Fore.RED + "[BAD] The Expected file doesn't match; there are {} differences seen, but '{}' is {} entries long".format(len(found-prod), options.expected, len(expected)) + Fore.RESET)

  if liveentries | expected == found:
    print(Fore.GREEN + "[GOOD] The Kinto dataset found at production equals the union of the expected file and the live list." + Fore.RESET)
  else:
    print(Fore.RED + "[BAD] The Kinto dataset is not equal to the union of the live list and the expected file. Differences follow." + Fore.RESET)
    for entry in found - (liveentries | expected):
      print(Fore.RED + " * {}".format(entry) + Fore.RESET)


  if len(notfound) > 0:
    print(Fore.RED + "[BAD] Expected, but not found in Kinto:" + Fore.RESET)
    pprint(sorted(notfound))
  else:
    print("Nothing not found.")

  if len(deleted) > 0:
    if deleted == missing:
      for deletedEntry in deleted:
        seen = False
        for entryData in prod_dataset['data']:
          if deletedEntry == make_entry(entryData['issuerName'], entryData['serialNumber']):
            seen = True
            print("Deleted ID: {} Serial: {}".format(entryData['id'], entryData['serialNumber']))
            break
        if not seen:
          print(Fore.RED + "[BAD] Deleted Entry: {}".format(deletedEntry) + Fore.RESET)
          raise("Missing entry?")

      print(Fore.GREEN + "[GOOD] The missing entries {} are all deleted.".format(len(deleted)) + Fore.RESET)
    else:
      print(Fore.RED + "[BAD] Found live, but missing in Kinto:" + Fore.RESET)
      pprint(sorted(missing))
  else:
    print("Nothing deleted.")

  if options.debug:
    print("Variables available:")
    print("  prod - located in Kinto production")
    print("  expected - from the file on disk")
    print("  found - located in Kinto changeset")
    print("  liveentries - located in the live CDN list")
    import pdb; pdb.set_trace()

if __name__ == "__main__":
  main()

