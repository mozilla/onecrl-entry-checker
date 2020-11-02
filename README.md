# Requirements

You'll need read access to the `prod` bucket and read/write access to the `staging` bucket on a suitable copy of Kinto.

Install deps with `pip install -r requirements.txt`

# Usage

`python3 compare.py`

```
[09:33:43] Stage-Stage: 1243 Stage-Preview: 1243 Stage-Published: 1240                 compare.py:72
[09:33:45] Prod-Stage: 1243 Prod-Preview: 1243 Prod-Published: 1240                    compare.py:78
           Verifying stage against preview                                             compare.py:84
           stage/security-state-staging (1243) and stage/security-state-preview (1243) compare.py:87
           are equivalent
           stage/security-state-staging (1243) and prod/security-state-staging (1243)  compare.py:87
           are equivalent
           stage/security-state-staging (1243) and prod/security-state-preview (1243)  compare.py:87
           are equivalent
           stage/security-state-preview (1243) and prod/security-state-staging (1243)  compare.py:87
           are equivalent
           stage/security-state-preview (1243) and prod/security-state-preview (1243)  compare.py:87
           are equivalent
           prod/security-state-staging (1243) and prod/security-state-preview (1243)   compare.py:87
           are equivalent
           There are 3 changes waiting:                                                compare.py:92
                                           Added entries
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                       ┃                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ MF0xCzAJBgNVBAYTAkpQMSUwIwYDVQQKExxTRUNPTSBUcnVzdCBTeXN0ZW1zIENPLixM… │ Irmw1g==                 │
│ MGAxCzAJBgNVBAYTAk5MMR4wHAYDVQQKDBVTdGFhdCBkZXIgTmVkZXJsYW5kZW4xMTAv… │ akWWZTytiy58nyLOsqpnaQ== │
│ MFAxJDAiBgNVBAsTG0dsb2JhbFNpZ24gRUNDIFJvb3QgQ0EgLSBSNTETMBEGA1UEChMK… │ Ae5fInnr9AhpWVIjkw==     │
└───────────────────────────────────────────────────────────────────────┴──────────────────────────┘
```