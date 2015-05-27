### GET rest/db/browse

---
loc: /rest/db/browse
category: Database
method: GET
---

Returns the directory tree of the global model. 
Directories are always JSON objects (map/dictionary), and files are always arrays of modification time and size.
The first integer is the files modification time, and the second integer is the file size.

The call takes one mandatory `folder` parameter and two optional parameters.
Optional parameter `levels` defines how deep within the tree we want to dwell down (0 based, defaults to unlimited depth)
Optional parameter `prefix` defines a prefix within the tree where to start building the structure.

```bash
$ curl -s http://localhost:8384/rest/db/browse?folder=default | json_pp
{
   "directory": {
      "file": ["2015-04-20T22:20:45+09:00", 130940928],
      "subdirectory": {
         "another file": ["2015-04-20T22:20:45+09:00", 130940928]
      }
   },
   "rootfile": ["2015-04-20T22:20:45+09:00", 130940928] 
}

$ curl -s http://localhost:8384/rest/db/browse?folder=default&levels=0 | json_pp
{
   "directory": {},
   "rootfile": ["2015-04-20T22:20:45+09:00", 130940928] 
}

$ curl -s http://localhost:8384/rest/db/browse?folder=default&levels=1 | json_pp
{
   "directory": {
      "file": ["2015-04-20T22:20:45+09:00", 130940928],
      "subdirectory": {}
   },
   "rootfile": ["2015-04-20T22:20:45+09:00", 130940928]
}

$ curl -s http://localhost:8384/rest/db/browse?folder=default&prefix=directory/subdirectory | json_pp
{
   "another file": ["2015-04-20T22:20:45+09:00", 130940928]
}

$ curl -s http://localhost:8384/rest/db/browse?folder=default&prefix=directory&levels=0 | json_pp
{
   "file": ["2015-04-20T22:20:45+09:00", 130940928],
   "subdirectory": {}
}
```### GET rest/db/completion

---
loc: /rest/db/completion
category: Database
method: GET
---

Returns the completion percentage (0 to 100) for a given device and folder.Takes `device` and `folder` parameters.

```json
{
  "completion": 0
}
```### GET rest/db/file

---
loc: /rest/db/file
category: Database
method: GET
---

Returns most data available about a given file, including version and availability.

```json
{
  "availability": [
    "I6KAH76-66SLLLB-5PFXSOA-UFJCDZC-YAOMLEK-CP2GB32-BV5RQST-3PSROAU"
  ],
  "global": {
    "flags": "0644",
    "localVersion": 3,
    "modified": "2015-04-20T22:20:45+09:00",
    "name": "util.go",
    "numBlocks": 1,
    "size": 9642,
    "version": [
      "5407294127585413568:1"
    ]
  },
  "local": {
    "flags": "0644",
    "localVersion": 4,
    "modified": "2015-04-20T22:20:45+09:00",
    "name": "util.go",
    "numBlocks": 1,
    "size": 9642,
    "version": [
      "5407294127585413568:1"
    ]
  }
}
```### GET rest/db/ignores

---
loc: /rest/db/ignores
category: Database
method: GET
---

Takes one parameter, `folder`, and returns the content of the `.stignore` as the `ignore` field. A second field, `patterns`, provides a compiled version of all included ignore patterns in the form of regular expressions. Excluded items in the `patterns` field have a nonstandard `(?exclude)` marker in front of the regular expression.

```json
{
  "ignore": [
    "/Backups"
  ],
  "patterns": [
    "(?i)^Backups$",
    "(?i)^Backups/.*$"
  ]
}
```### POST rest/db/ignores

---
loc: /rest/db/ignores
category: Database
method: POST
---

Expects a format similar to the output of `GET` call, but only containing the `ignore` field (`patterns` field should be omitted). It takes one parameter, `folder`, and either updates the content of the `.stignore` echoing it back as a response, or returns an error.### GET rest/db/need

---
loc: /rest/db/need
category: Database
method: GET
---

Takes one parameter, `folder`, and returns lists of files which are needed by this device in order for it to become in sync. 

```bash
{
  # Files currently being downloaded
  "progress": [
    {
      "flags": "0755",
      "localVersion": 6,
      "modified": "2015-04-20T23:06:12+09:00",
      "name": "ls",
      "size": 34640,
      "version": [
        "5157751870738175669:1"
      ]
    }
  ],
  # Files queued to be downloaded next (as per array order)
  "queued": [
      ...   
  ],
  # Files to be downloaded after all queued files will be downloaded. 
  # This happens when we start downloading files, and new files get added while we are downloading.
  "rest": [
      ...
  ]
}
```### POST rest/db/prio

---
loc: /rest/db/prio
category: Database
method: POST
---

Moves the file to the top of the download queue.

```bash
curl -X POST http://127.0.0.1:8384/rest/db/prio?folder=default&file=foo/bar
```

Response contains the same output as `GET /rest/db/need`### POST rest/db/scan

---
loc: /rest/db/scan
category: Database
method: POST
---

Request immediate rescan of a folder, or a specific path within a folder. Takes the mandatory parameter `folder` (folder ID) and the optional parameter `sub` (path relative to the folder root). If `sub` is omitted or empty, the entire folder is scanned for changes, otherwise only the given path (and children, in case it's a directory) is scanned.

Requesting scan of a path that no longer exists, but previously did, is valid and will result in syncthing noticing the deletion of the path in question.

Returns status 200 and no content upon success, or status 500 and a plain text error if an error occurred during scanning.

```bash
curl -X POST http://127.0.0.1:8384/rest/db/scan?folder=default&sub=foo/bar
```### GET rest/db/status

---
loc: /rest/db/status
category: Database
method: GET
---

Returns information about the current status of a folder.

Parameters: `folder`, the ID of a folder.

```bash
{
  # latest version according to cluster:
  "globalBytes": 13173473780,
  "globalDeleted": 1847,
  "globalFiles": 42106,
  # what we have locally:
  "localBytes": 13173473780,
  "localDeleted": 1847,
  "localFiles": 42106,
  # which part of what we have locally is the latest cluster verision:
  "inSyncBytes": 13173473780,
  "inSyncFiles": 42106,
  # which part of what we have locally should be fetched from the cluster:
  "needBytes": 0,
  "needFiles": 0,
  # various other metadata
  "ignorePatterns": true,
  "invalid": "",
  "state": "idle",
  "stateChanged": "2015-03-16T21:47:28.750853241+01:00",
  "version": 71989
}
```### GET rest/stats/device

---
loc: /rest/stats/device
category: Statistics
method: GET
---

Returns general statistics about devices.
Currently, only contains the time the device was last seen.

```bash
$ curl -s http://localhost:8384/rest/stats/device | json
{
  "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2": {
    "lastSeen" : "2015-04-18T11:21:31.3256277+01:00"
  }
}
```### GET rest/stats/folder

---
loc: /rest/stats/folder
category: Statistics
method: GET
---

Returns general statistics about folders.
Currently, only contains the last synced file.

```bash
$ curl -s http://localhost:8384/rest/stats/folder | json
{
  "folderid" : {
    "lastFile" : {
      "filename" : "file/name",
        "at" : "2015-04-16T22:04:18.3066971+01:00"
      }
  }
}
```### GET rest/svc/deviceid

---
loc: /rest/svc/deviceid
category: Services
method: GET
---

Verifies and formats a device ID. Accepts all currently valid formats (52 or 56 characters with or without separators, upper or lower case, with trivial substitutions). Takes one parameter, `id`, and returns either a valid device ID in modern format, or an error.

```bash
$ curl -s http://localhost:8384/rest/svc/deviceid?id=1234 | json
{
  "error": "device ID invalid: incorrect length"
}

$ curl -s http://localhost:8384/rest/svc/deviceid?id=p56ioi7m--zjnu2iq-gdr-eydm-2mgtmgl3bxnpq6w5btbbz4tjxzwicq | json
{
  "id": "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2"
}
```### GET rest/svc/lang

---
loc: /rest/svc/lang
category: Services
method: GET
---

Returns a list of canonicalized localization codes, as picked up from the `Accept-Language` header sent by the browser.

```json
["sv_sv","sv","en_us","en"]
```### GET rest/svc/report

---
loc: /rest/svc/report
category: Services
method: GET
---

Returns the data sent in the anonymous usage report.

```json
{
  "folderMaxFiles": 42106,
  "folderMaxMiB": 12563,
  "longVersion": "syncthing v0.10.27+5-g36c93b7 (go1.4 darwin-amd64 default) jb@syno 2015-03-16 20:43:34 UTC",
  "memorySize": 16384,
  "memoryUsageMiB": 41,
  "numDevices": 10,
  "numFolders": 4,
  "platform": "darwin-amd64",
  "sha256Perf": 122.38,
  "totFiles": 45180,
  "totMiB": 18151,
  "uniqueID": "6vulmdGw",
  "version": "v0.10.27+5-g36c93b7"
}
```### GET rest/system/config

---
loc: /rest/system/config
category: System
method: GET
---

Returns the current configuration.

```bash
{
 # etc
}
```### GET rest/system/config/insync

---
loc: /rest/system/config/insync
category: System
method: GET
---

Returns whether the config is in sync, i.e. whether the running configuration is the same as that on disk.

```json
{
  "configInSync": true
}
```### POST rest/system/config

---
loc: /rest/system/config
category: System
method: POST
---

Post the full contents of the configuration, in the same format as returned by the corresponding GET request. The configuration will be saved to disk and the configInSync flag set to false. Restart syncthing to activate.### GET rest/system/connections

---
loc: /rest/system/connections
category: System
method: GET
---

Returns the list of current connections and some metadata associated with the connection/peer.

```json
{
  "connections": {
    "SMAHWLH-AP74FAB-QWLDYGV-Q65ASPL-GAAR2TB-KEF5FLB-DRLZCPN-DJBFZAG": {
      "address": "172.21.20.78:22000",
      "at": "2015-03-16T21:51:38.672758819+01:00",
      "clientVersion": "v0.10.27",
      "inBytesTotal": 415980,
      "outBytesTotal": 396300
    }
  },
  "total": {
    "address": "",
    "at": "2015-03-16T21:51:38.672868814+01:00",
    "clientVersion": "",
    "inBytesTotal": 415980,
    "outBytesTotal": 396300
  }
}
```### GET rest/system/discovery

---
loc: /rest/system/discovery
category: System
method: GET
---

Returns the contents of the local discovery cache.

```json
{
  "LGFPDIT7SKNNJVJZA4FC7QNCRKCE753K72BW5QD2FOZ7FRFEP57Q": [
    "192.162.129.11:22000"
  ]
}
```### POST rest/system/discovery/hint

---
loc: /rest/system/discovery/hint
category: System
method: POST
---

Post with the query parameters `device` and `addr` to add entries to the discovery cache.

```bash
curl -X POST http://127.0.0.1:8384/rest/system/discovery/hint?device=LGFPDIT7SKNNJVJZA4FC7QNCRKCE753K72BW5QD2FOZ7FRFEP57Q\&addr=192.162.129.11:22000
# Or with the X-API-Key header:
curl -X POST --header "X-API-Key: TcE28kVPdtJ8COws1JdM0b2nodj77WeQ" http://127.0.0.1:8384/rest/system/discovery/hint?device=LGFPDIT7SKNNJVJZA4FC7QNCRKCE753K72BW5QD2FOZ7FRFEP57Q\&addr=192.162.129.11:22000
```### POST rest/system/error/clear

---
loc: /rest/system/error/clear
category: System
method: POST
---

Post with empty to body to remove all recent errors.### GET rest/system/error

---
loc: /rest/system/error
category: System
method: GET
---

Returns the list of recent errors.

```json
{
  "errors": [
    {
      "time": "2014-09-18T12:59:26.549953186+02:00",
      "error": "This is an error string"
    }
  ]
}
```### POST rest/system/error

---
loc: /rest/system/error
category: System
method: POST
---

Post with an error message in the body (plain text) to register a new error. The new error will be displayed on any active GUI clients.### GET rest/system/ping

---
loc: /rest/system/ping
category: System
method: GET
---

Returns a `{"ping": "pong"}` object.

```json
{
  "ping": "pong"
}
```### POST rest/system/ping

---
loc: /rest/system/ping
category: System
method: POST
---

Returns a `{"ping": "pong"}` object.### POST rest/system/reset

---
loc: /rest/system/reset
category: System
method: POST
---

Post with empty body to immediately *reset* syncthing. This means renaming all folder directories to temporary, unique names, wiping all indexes and restarting. This should probably not be used during normal operations...### POST rest/system/restart

---
loc: /rest/system/restart
category: System
method: POST
---

Post with empty body to immediately restart syncthing.### POST rest/system/shutdown

---
loc: /rest/system/shutdown
category: System
method: POST
---

Post with empty body to cause syncthing to exit and not restart.### GET rest/system/status

---
loc: /rest/system/status
category: System
method: GET
---

Returns information about current system status and resource usage.

```json
{
  "alloc": 30618136,
  "cpuPercent": 0.006944836512046966,
  "extAnnounceOK": {
    "udp4://announce.syncthing.net:22026": true,
    "udp6://announce-v6.syncthing.net:22026": true
  },
  "goroutines": 49,
  "myID": "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2",
  "pathSeparator": "/",
  "sys": 42092792,
  "tilde": "/Users/jb"
}
```### GET rest/system/upgrade

---
loc: /rest/system/upgrade
category: System
method: GET
---

Checks for a possible upgrade and returns an object describing the newest version and upgrade possibility.

```json
{
  "latest": "v0.10.27",
  "newer": false,
  "running": "v0.10.27+5-g36c93b7"
}
```### POST rest/system/upgrade

---
loc: /rest/system/upgrade
category: System
method: POST
---

Perform an upgrade to the newest released version and restart. Does nothing if there is no newer version than currently running.### GET rest/system/version

---
loc: /rest/system/version
category: System
method: GET
---

Returns the current syncthing version information.

```json
{
  "arch": "amd64",
  "longVersion": "syncthing v0.10.27+3-gea8c3de (go1.4 darwin-amd64 default) jb@syno 2015-03-16 11:01:29 UTC",
  "os": "darwin",
  "version": "v0.10.27+3-gea8c3de"
}
```