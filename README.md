jira-issue
================

This script allows users to quickly create Jira issues from the command line.  The script is python3 based and uses the [jira-python](https://github.com/pycontribs/jira). The goal is to minimize the effor needed to put in simple Jira issues.

Configuration
=====
The configuration is stored in ~/.jira_config.  This file uses `ini` format with a DEFAULT section for items like the Jira credentials and custom sections that can be used to create templates that can be easily called.  Here are the common fields for the configuration file:

username, token|password, server = Data needed to connect to github.

assignee = github assignee ID
board = Board name to add this issue to ( or use board_id )
board_id = Scrum board to add this issue to ( or use board)
issue = issue key to process ( leave blank to create a new issue)
key = the key for the project that issues will be created in
type = Issue type to create
labels = labels to assign.  Labels can be in comma or space separated format.
close = Close the issue?
work = Time Spent string for the amount of work done (Examples: 30m, 1h ) 

**Custom Fields**
Custom fields can be mapped to an alias name for more readable configuration.  The following examples maps customfile_11135 to the alias `squad` and then assigns it the value of `Alpha`:

customfield_11135 = {"alias":"squad","type":"list"}
squad = Alpha


Usage
=====
These examples are based on the jira_config.example file.  The title field does not need to be quoted.  This means that if you update an existing ticket that the title field has to be sent, but will be ignored.

Create an `Ops Request` and close it with 1.5 hours worked 
```jira-issue -u opsc -w 1.5h More evidence needed for soc2```

Create a Support request with the tag ProdSupport and 30 minutes worked
```jira-issue -u ps -w 30m Investigate deploy failure on core-api-prod-1a```

Update the story DC-1788 with hours and close
``` jira-issue -w 30m -c -i DC-1788 x ```








