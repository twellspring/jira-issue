jira-issue
================

This script allows users to quickly create Jira issues from the command line.  The script is python3 based and uses the [jira-python](https://github.com/pycontribs/jira). The goal is to minimize the effor needed to put in simple Jira issues.

If prerequisites are not automatically installed, run:  `sudo pip3 install jira python-editor`

Configuration
=====
The configuration is stored in ~/.jira_config.  This file uses `ini` format with a DEFAULT section for items like the Jira credentials and custom sections that can be used to create templates that can be easily called.  Here are the common fields for the configuration file:

username, token, server = Data needed to connect to github.  Go to https://id.atlassian.com/manage/api-tokens to create a token.<br>

assignee = github assignee ID<br>
board = Board name to add this issue to ( or use board_id ).<br>
board_id = Scrum board to add this issue to ( or use board).<br>
issue = issue key to process ( leave blank to create a new issue).<br>
key = the key for the project that issues will be created in.<br>
type = Issue type to create.<br>
labels = labels to assign.  Labels can be in comma or space separated format.  Labels can not contain spaces or commas.<br>
close = Close the issue?<br>
work = Time Spent string for the amount of work done (Examples: 30m, 1h ).<br>

**Custom Fields**<br>
Custom fields can be mapped to an alias name for more readable configuration.  The following examples maps customfile_11135 to the alias `squad` and then assigns it the value of `Alpha`.

    customfield_11135 = {"alias":"squad","type":"list"}
    squad = Alpha

Custom Field     Notes<br>
* Custom fields can only be configured in the DEFAULT section. 
* An alias can be specified in any section
* A custom field can be configured but not used ( i.e. an the alias field not specified).  In this case, the custom field will not be set
* By default custom fields are of type text.  Currently the only other option is a list. Use comma or space separation between list items

Usage
=====
These examples are based on the jira_config.example file.  The title field does not need to be quoted.  This means that if you update an existing ticket that the title field has to be sent, but will be ignored.

Create an *Ops Request* and close it with 1.5 hours worked <br>
```jira-issue -u opsc -w 1.5h More evidence needed for soc2```

Create a *Support* request with the tag ProdSupport and 30 minutes worked <br>
```jira-issue -u ps -w 30m Investigate deploy failure on core-api-prod-1a```

Update the issue DC-1788 with hours <br>
``` jira-issue -w 30m -i DC-1788 x ```

Update the issue DC-1788 with hours and close <br>
``` jira-issue -w 30m -c -i DC-1788 x ```








