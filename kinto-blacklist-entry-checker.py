# Verify Kinto sets with a delta expected list
import json, yaml, requests, getpass, sys
from collections import defaultdict
from optparse import OptionParser
from pprint import pprint

def make_entry(issuer, serial):
  issuer = issuer.rstrip('=\n ')
  serial = serial.rstrip('=\n ')
  return "issuer: {} serial: {}".format(issuer, serial)

def main():
  defaults = defaultdict(str)
  try:
    with open (".config.yml", 'r') as ymlfile:
      defaults.update(yaml.load(ymlfile))
  except:
    pass

  parser = OptionParser()
  parser.add_option("-e", "--expected", dest="expected", metavar="FILE",
                    help="Expected input file", default=defaults['expected'])
  parser.add_option("-u", "--user", dest="user", help="LDAP Account Username",
                    default=defaults['user'])
  parser.add_option("-H", "--host", dest="host", help="Hostname",
                    default=defaults['host'])
  parser.add_option("-E", "--endpoint", dest="endpoint", help="Path at the host",
                    default=defaults['endpoint'])
  parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")
  (options, args) = parser.parse_args()

  if options.expected == "":
    print("You must specify an expected file")
    parser.print_help()
    sys.exit(1)

  if options.host == "":
    print("You must specify a host")
    parser.print_help()
    sys.exit(1)

  if options.endpoint == "":
    print("You must specify an endpoint")
    parser.print_help()
    sys.exit(1)

  if options.user == "":
    print("You must specify a user")
    parser.print_help()
    sys.exit(1)

  expected = set()
  with open(options.expected) as expected_data:
    for line in expected_data.readlines():
      parts=line.strip().split(" ")
      expected.add(make_entry(parts[1], parts[3]))

  print("LDAP account password for {}:".format(options.user))
  auth = (options.user, getpass.getpass())
  payload = {
    "collection_id": "certificates",
    "_sort": "-last_modified",
    "_limit": 9999
  }

  req = requests.get("https://{}{}".format(options.host, options.endpoint),
                     auth=auth, params=payload)
  dataset = req.json()

  if 'data' not in dataset:
    raise Exception("Invalid login, or something else. Details: {}".format(req.content))

  found = set()
  deleted = set()

  for entry in dataset['data']:
    if entry['resource_name'] != "record":
      continue

    entryData = entry['target']['data']

    if 'deleted' in entryData:
      deleted.add(entryData['id'])
    else:
      found.add(make_entry(entryData['issuerName'], entryData['serialNumber']))

  notfound = expected-found
  unexpected = found-expected

  print("")
  print("Dataset contains {} added and {} deleted entries".format(len(found), len(deleted)))
  print("")

  print("Deleted:")
  pprint(sorted(deleted))

  print("Expected, but not found in Kinto:")
  pprint(sorted(notfound))

  print("Unexpected, found in Kinto:")
  pprint(sorted(unexpected))


if __name__ == "__main__":
  main()