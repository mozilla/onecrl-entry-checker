
# Grab a changeset from BMO:
```
curl 'https://bug1343305.bmoattachments.org/attachment.cgi?id=8842097' > expected.txt
```

# configure the yaml
```
cp config.yml.example .config.yml
vim .config.yml
```

# Run
```
python3 kinto-blacklist-entry-checker.py --expect expected.txt
```

# Example Output
```
LDAP account password for user@company:
Password:

Dataset contains 24 added and 29 deleted entries

Deleted:
['0ab1b53f-5695-4802-9a35-4de16961c10f',
 '19b97966-beb9-46cf-a21b-2df51b5562ec',
 '20430047-9c95-40cd-9865-912bf7dffa5b',
 '2b7eba40-729e-4829-b70b-574b6074f336',
 '397417ee-aa00-4da0-9bbe-6498f2afa060',
 '40b9c372-91f6-4ba4-8600-3d36af7a14bd',
 '47e13a94-1bbf-4e08-be63-b74dbf69491c',
 '50edb292-efb2-4ac3-95c1-187686ebffdb',
 '5256dadc-6cdc-4406-b33a-b1052dad1533',
 '5342ffc1-b544-481e-9201-4dfdfaf08c63',
 '534cb5be-6999-4590-a38f-8c7cef1ac4e8',
 '57445c75-0c3b-4a37-ad46-d86a5bba22f2',
 '5c33614b-1d6b-41c1-b483-e9fd39b0f205',
 '669e5b07-084a-4ea9-8e02-14df475366d2',
 '6b6f7eac-f719-4e85-acb6-ae994def3be0',
 '6f21ffef-e1da-4abc-9711-3591c9d205e4',
 '70ef0911-75b3-49ad-8c5f-b191b8cd4ce2',
 '7ef66b53-9caa-4689-846d-939961ffcc97',
 '894a6814-07d5-49ef-b1a0-08028447c361',
 '8d4a85e9-04b1-436f-93a7-eb5053d39d93',
 '8e9a1bed-323b-496c-a1c2-0208ba07576b',
 '91bb20ce-49f0-4900-98ab-8874088b8af5',
 '91be3663-de9b-41f9-89d3-d7c0e43e9d67',
 '9682dffb-15a7-4cbf-a42c-8657a9fb21f9',
 '9a0827b2-8605-4469-af6c-cc3c658282aa',
 'acf9935a-f12f-4dd0-8472-3ba211cb7b89',
 'b817a0bb-19a3-4f40-b5b8-1b6041045308',
 'd81af35e-c9b3-4e8f-a562-6944a86d3a13',
 'dce279fb-0dc6-42d7-91f5-e38222f65e2a']
Expected, but not found in Kinto:
[]
Unexpected, found in Kinto:
[]
```
