# AARNet Public Globus Test Collections

The following collections have been made available by AARNet to help Australian users test their Globus endpoints against high-performance endpoints on AARNet infrastructure.
The collections are published from servers with 100GB/s network interfaces and fast RAID0 NVME storage for parallel writes. These servers are connected directly to the AARNet network.
The full list of AARNet Globus collections can be viewed in the Globus web app [here](https://app.globus.org/collections?entityType=GCSv5_guest_collection&q=AARNet&scope=all).

Please note that we do not advise uploading sensitive data to any AARNet test collections, as they are for test and demonstration use only and are not certified for privacy.

## Public, Anonymously-readable Test Collections

These fixed collections are intended to demonstrate anonymous download or transfer by all users with or without a Globus account.

The ```standard_test_files``` directory contains a suite of test files copied from CERN that will be useful for testing transfer performance with different sizes and numbers of files.

The ```RWTEST``` directory contains the files in the Public, Anonymously-readable Test Collections writeable for AARNet Demonstrators.

Note that the contents of these collections will be visible to ALL users, and not directly writeable by anyone, including by AARNet Demonstrators.

- [AARNet Melbourne Read-only Test Collection #1](https://app.globus.org/file-manager?origin_id=af7fa138-6565-4a6e-a863-2292a34fa1eb&origin_path=%2F&two_pane=false)
- [AARNet Melbourne Read-only Test Collection #2](https://app.globus.org/file-manager?origin_id=ea66df1d-7642-4e90-99ae-87a11e4c0678&origin_path=%2F&two_pane=false)
- [AARNet Sydney Read-only Test Collection](https://app.globus.org/file-manager?origin_id=481dde3c-15cc-4521-befa-68a37a2346f8&origin_path=%2F&two_pane=false)

## Public, Anonymously-readable Test Collections writeable for AARNet Demonstrators

These collections are intended for AARNet demonstrators to show how files can be uploaded securely by permitted groups and users, and made available for anonymous download or transfer by all users with or without a Globus account.

Note that the contents of these collections will be readable by ALL users, but only writeable by the AARNet Demonstrators group. Contents of these collections may change or be deleted without warning.

- [AARNet Melbourne Read-write Test Collection #1](https://app.globus.org/file-manager?origin_id=cd03197a-3ac5-4152-adbc-2dd7cf719a6f&origin_path=%2F&two_pane=false)
- [AARNet Melbourne Read-write Test Collection #2](https://app.globus.org/file-manager?origin_id=006f4bd3-24f7-42c7-9f2a-151f28845338&origin_path=%2F&two_pane=false)
- [AARNet Sydney Read-write Test Collection](https://app.globus.org/file-manager?origin_id=acacff14-5b44-4fe1-8ab2-a9836146d9b9&origin_path=%2F&two_pane=false)

## Public, Read-Only Test Collections readable and writeable only for AARNet Demonstrators

These collections are intended for AARNet demonstrators to show how files can be uploaded securely by permitted groups and users, and made available for download or transfer only by permitted users and groups.

Note that the contents of these collections will NOT be readable or writeable by users outside the AARNet Demonstrators group.

- [AARNet Melbourne Restricted Demonstration Collection #1](https://app.globus.org/file-manager?origin_id=d0795ba5-46a4-4672-9414-57a58d94c1da&origin_path=%2F&two_pane=false)
- [AARNet Melbourne Restricted Demonstration Collection #2](https://app.globus.org/file-manager?origin_id=4f61ba54-3a64-4ace-9b18-487317acbb0b&origin_path=%2F&two_pane=false)
- [AARNet Sydney Restricted Demonstration Collection](https://app.globus.org/file-manager?origin_id=8360af02-46f3-4371-9920-92209d19fac8&origin_path=%2F&two_pane=false)

## Custom Collections for write testing - available on request

For obvious security reasons, AARNet must restrict the users able to upload to our Globus test collections. AARnet can, however, create custom writeable collections for specific users to test uploads from their own endpoints as required. Please contact your AARNet representative if you need to do this.

## Third-Party Globus Collections (Non-AARNet)
There are some publicly-accessible third-party Globus collections which contain test data or live datasets that may be of interest to users. It is important to realise that some of these collections are intended for archival purposes and are not optimised for high transfer speeds.
- [ESnet CERN DTN (Anonymous read-only testing)](https://app.globus.org/file-manager?destination_id=531643be-e83e-4ebc-a0d1-d459b48432e7&destination_path=%2Ftest3%2F&origin_id=722751ce-1264-43b8-9160-a9272f746d78&two_pane=true)
- [EMBL-EBI Public Data](https://app.globus.org/file-manager?origin_id=47772002-3e5b-4fd3-b97c-18cee38d6df2&origin_path=%2Fbiostudies%2F)
