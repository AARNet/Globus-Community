# Globus Community Code Samples

## Examples
The examples folder contains code examples for various useful tasks using Globus.
All example code is provided on an as-is basis and are provided strictly on a "use at your own risk" basis. The examples are intended not as complete solutions, but rather as an indicator of how to approach particular tasks.

### Bandwidth Throttling
This is an example of [how to throttle bandwidth outbound from a Globus server under Ubuntu 22.04](./examples/bandwidth_throttling/README.md).

### Folder Watcher
This is an example of [how to set up a folder watcher script to automate Globus transfers when new files appear](./examples/folder_watcher/README.md). This is potentially useful where the Globus synch option is not appropriate: for example, when transferred files need to be removed from the destination collection as part of a workflow and we do not wish to re-transfer them.
