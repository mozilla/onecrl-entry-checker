# Requirements

You'll need read access to the `prod` bucket and read/write access to the `staging` bucket on a suitable copy of Kinto.

Install deps with `pip install -r requirements.txt`

# Usage

`python3 compare.py`

```
[09:45:22] Stage-Stage: 1243 Stage-Preview: 1243 Stage-Published: 1240                 compare.py:59
[09:45:24] Prod-Stage: 1243 Prod-Preview: 1243 Prod-Published: 1240                    compare.py:65
           Verifying stage against preview                                             compare.py:71
           stage/security-state-staging (1243) and stage/security-state-preview (1243) compare.py:74
           are equivalent
           stage/security-state-staging (1243) and prod/security-state-staging (1243)  compare.py:74
           are equivalent
           stage/security-state-staging (1243) and prod/security-state-preview (1243)  compare.py:74
           are equivalent
[09:45:25] stage/security-state-preview (1243) and prod/security-state-staging (1243)  compare.py:74
           are equivalent
           stage/security-state-preview (1243) and prod/security-state-preview (1243)  compare.py:74
           are equivalent
           prod/security-state-staging (1243) and prod/security-state-preview (1243)   compare.py:74
           are equivalent
           There are 3 changes waiting. Adding:                                        compare.py:79
{
    'details': {
        'bug': 'https://bugzilla.mozilla.org/show_bug.cgi?id=1674587',
        'who': '',
        'why': '',
        'name': '',
        'created': ''
    },
    'enabled': False,
    'issuerName':
'MF0xCzAJBgNVBAYTAkpQMSUwIwYDVQQKExxTRUNPTSBUcnVzdCBTeXN0ZW1zIENPLixMVEQuMScwJQYDVQQLEx5TZWN1cml0eSB
    'serialNumber': 'Irmw1g=='
}
{
    'details': {
        'bug': 'https://bugzilla.mozilla.org/show_bug.cgi?id=1674587',
        'who': '',
        'why': '',
        'name': '',
        'created': ''
    },
    'enabled': False,
    'issuerName':
'MGAxCzAJBgNVBAYTAk5MMR4wHAYDVQQKDBVTdGFhdCBkZXIgTmVkZXJsYW5kZW4xMTAvBgNVBAMMKFN0YWF0IGRlciBOZWRlcmx
    'serialNumber': 'akWWZTytiy58nyLOsqpnaQ=='
}
{
    'details': {
        'bug': 'https://bugzilla.mozilla.org/show_bug.cgi?id=1674587',
        'who': '',
        'why': '',
        'name': '',
        'created': ''
    },
    'enabled': False,
    'issuerName':
'MFAxJDAiBgNVBAsTG0dsb2JhbFNpZ24gRUNDIFJvb3QgQ0EgLSBSNTETMBEGA1UEChMKR2xvYmFsU2lnbjETMBEGA1UEAxMKR2x
    'serialNumber': 'Ae5fInnr9AhpWVIjkw=='
}
```