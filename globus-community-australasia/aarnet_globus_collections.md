---
title: AARNet Public Globus Test Collections
---

The following collections have been made available by AARNet to help Australian users test their Globus endpoints against high-performance endpoints on AARNet infrastructure.
The collections are published from servers with 100GB/s network interfaces and fast RAID0 NVME storage for parallel writes. These servers are connected directly to the AARNet network.
The full list of AARNet Globus collections can be viewed in the Globus web app [here](https://app.globus.org/collections?entityType=GCSv5_guest_collection&q=AARNet&scope=all).

Please note that we do not advise uploading sensitive data to any AARNet test collections, as they are for test and demonstration use only and are not certified for privacy.

## Public, Anonymously-readable Test Collections

These fixed collections are intended to demonstrate anonymous download or transfer by all users with or without a Globus account.

The ```standard_test_files``` directory contains a suite of test files copied from CERN that will be useful for testing transfer performance with different sizes and numbers of files.

The ```RWTEST``` directory contains the files in the Public, Anonymously-readable Test Collections writeable for AARNet Demonstrators.

Note that the contents of these collections will be visible to ALL users, and not directly writeable by anyone, including by AARNet Demonstrators.

- [AARNet Globus Endpoint NSW (ARTM) POSIX Gateway Public RO Guest Collection](https://app.globus.org/file-manager?origin_id=9e472d3a-ac18-42d0-bac8-3c9220801fbe&two_pane=true)
- [AARNet Globus Endpoint NSW (ETCA) POSIX Gateway Public RO Guest Collection](https://app.globus.org/file-manager?origin_id=ba7a1bc4-dacd-47a7-bc92-87d0a5768305&two_pane=true)
- [AARNet Globus Endpoint NSW (MCQM) POSIX Gateway Public RO Guest Collection](https://app.globus.org/file-manager?origin_id=12b88024-167c-4869-ab40-69bbf07ce3c5&two_pane=true)

## Public, Anonymously-readable Test Collections writeable for AARNet Demonstrators

These collections are intended for AARNet demonstrators to show how files can be uploaded securely by permitted groups and users, and made available for anonymous download or transfer by all users with or without a Globus account.

Note that the contents of these collections will be readable by ALL users, but only writeable by the AARNet Demonstrators group. Contents of these collections may change or be deleted without warning.

- [AARNet Globus Endpoint NSW (ARTM) POSIX Gateway Public RW Guest Collection](https://app.globus.org/file-manager?origin_id=8991e6d2-a5e3-41ca-a90f-33e7aa0da9d2&two_pane=true)
- [AARNet Globus Endpoint NSW (ETCA) POSIX Gateway Public RW Guest Collection](https://app.globus.org/file-manager?origin_id=afc72bc4-1196-4499-8ec6-959b4d108c96&two_pane=true)
- [AARNet Globus Endpoint NSW (MCQM) POSIX Gateway Public RW Guest Collection](https://app.globus.org/file-manager?origin_id=f9156b88-b2a5-4680-8f91-00b47ce22d5a&two_pane=true)

## Custom Collections for write testing - available on request

For obvious security reasons, AARNet must restrict the users able to upload to our Globus test collections. AARnet can, however, create custom writeable collections for specific users to test uploads from their own endpoints as required. Please contact your AARNet representative if you need to do this.

## Third-Party Globus Collections (Non-AARNet)
There are some publicly-accessible third-party Globus collections which contain test data or live datasets that may be of interest to users. It is important to realise that some of these collections are intended for archival purposes and are not optimised for high transfer speeds.
- [ESnet CERN DTN (Anonymous read-only testing)](https://app.globus.org/file-manager?destination_id=531643be-e83e-4ebc-a0d1-d459b48432e7&destination_path=%2Ftest3%2F&origin_id=722751ce-1264-43b8-9160-a9272f746d78&two_pane=true)
- [EMBL-EBI Public Data](https://app.globus.org/file-manager?origin_id=47772002-3e5b-4fd3-b97c-18cee38d6df2&origin_path=%2Fbiostudies%2F)
