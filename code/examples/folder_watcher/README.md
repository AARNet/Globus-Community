# Automate Globus transfers with a folder watcher

If the folder sync functionality built into Globus does not fit your workflow, you can set up a watcher script that triggers a file transfer whenever new files are added to the folder.

## Limitations

The inotifywait command used in this example may not work with NFS-mounted volumes. If your servers use NFS, you might need a different solution.

## Prerequisites

- The UUIDs of both the source and destination collections.
- Packages installed on the sending server:
  - The Globus Command Line Interface (CLI) package.
  - The inotify-tools package is installed (for the inotifywait folder watching command).
- Account permissions:
  - Administrator privileges on the sending server.
  - Globus permissions to read files from the source directory on the sending endpoint and write files to the destination directory on the receiving endpoint (requires Globus login operation).

## Procedure to enable the folder watcher

**Note: these instructions are intended as a demonstration only, and specific to a server running Ubuntu 22.04. If you are running a different Ubuntu distribution or operating system, you may need to adjust the script.**

Copy the ```globus_folder_watcher.sh``` script in this directory to your machine, replacing the placeholders in the script below with your own values:

- ```\<SOURCE>```: The UUID for the sending server.
- ```\<DESTINATION>```: The UUID for the destination server.
- ```\<SEND-DIR>```: The root directory for the source collection.
- ```\<SOURCE-DIR>```: The source directory to be watched, in the source collection.
- ```\<DEST-DIR>```: The destination directory to which source directory files will be sent, in the destination collection.

We recommend this script be run in the background for production use, but this will demonstrate the output to stdout.

```
# Set permissions for the watcher script:
chmod 750 globus_folder_watcher.sh

# Log in to Globus
globus-connect-server login localhost
```

Globus will respond with an authentication link:

```
Please authenticate with Globus here:

------------------------------------

https://auth.globus.org/v2/oauth2/authorize?client_id=7e9acd72-a8f3-496d-ab96-cf823b11d70b&redirect_uri=https%3A%2F%2Fauth.globus.org%2Fv2%2Fweb%2Fauth-code&scope=openid+profile+email+urn%3Aglobus%3Aauth%3Ascope%3Aauth.globus.org%3Aview_identity_set+urn%3Aglobus%3Aauth%3Ascope%3Aauth.globus.org%3Amanage_projects+urn%3Aglobus%3Aauth%3Ascope%3Ab04bec41-a6aa-4aae-8405-d0cc85ea222f%3Amanage_collections&state=_default&response_type=code&access_type=offline&prompt=login

------------------------------------
```

Copy the link shown and paste it into your browser. Complete your login in your browser.

Copy the authorisation code and paste it into the command line:

```
Enter the resulting Authorization Code here: alFoFZko5gioVatdKSDhAlICsIr5lz

You have successfully logged into GCS endpoint a04bec41-b6aa-5aae-7405-e0cc85ea222e at 3820e9.0ec8.data.globus.org!
```

Note: that the above authentication method is for demonstration only. The resulting login session will persist for 11 days by default.

Run the folder watcher script:

```
./globus_folder_watcher.sh
```
If the script loads correctly, output similar to this will be displayed:
```
Watching /dest-directory/
Setting up watches.  Beware: since -r was given, this may take a while!
Watches established.
The file 'globustest1.txt' appeared in directory '/ dest-directory /' via 'CLOSE_WRITE,CLOSE' at Sun Jul  7 11:10:21 PM UTC 2024
File path in collection is '/dest-directory/globustest1.txt'
globus transfer XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:/dest-directory/globustest1.txt YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY:/dest-directory/globustest1.txt
Message: The transfer has been accepted and a task has been created and queued for execution
Task ID: ZZZZZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZZZZZZZZ1
The file 'globustest1.txt' appeared in directory '/send-directory/' via 'CLOSE_WRITE,CLOSE' at Sun Jul  7 11:50:11 PM UTC 2024
File path in collection is '/globustest1.txt'
globus transfer XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX:/globustest1.txt YYYYYYYY-YYYY-YYYY-YYYY-YYYYYYYYYYYY:/dest-directory/globustest1.txt
Message: The transfer has been accepted and a task has been created and queued for execution
Task ID: ZZZZZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZZZZZZZZ2
```
The script will run indefinitely until terminated with Ctrl-C.

Note that the script can also be launched to run in the background with a command like the following:
```
./globus_folder_watcher.sh &
```
