# Jira Issue Export Toolkit

## Pre Requisitie:
* Python 3
* [Python Jira Client library](https://jira.readthedocs.io/en/master/index.html)
  * Install all necessary libraries using requirements.txt
  ```
  pip install requirements.txt
  ```
* OAuth token is available to use.
  * Don't have it, [Read here on how to generate Jira OAuth Token](https://raju.guide/index.php/2018/08/19/oauth-with-jira/)
* *config* directory in this repo contains
  * ".oauthconfig" file.
  * "oauth.pem" - location of RSA private key file
  * "issue_export.config" file which contains JQL and columns that you need to export for Issues.

* Below are sample .oauthconfig and issue_export.config files that you should put in config directory.
```
➜  ~ cat .oauthconfig
[oauth_token_config]
oauth_token=<oauth token>
oauth_token_secret=<oauth token secret>
consumer_key=<consumer key>
user_private_key_file_name=<private key file path>

[server_info]
jira_base_url=<jira base url>
```

```
➜  ~ cat issue_export.config
[issue_field_config]
# <jira_internal_field_name>=<display_field_name>,<field_type>,<output_type>,<access_key>
# <jira_internal_field_name>=<display_field_name>,<single/multi>,<plain/plainarray/json/cascade>,<blank/json_key if applicable>
summary=Issue Summary,single,plain,
priority=Priority,single,json,name
# Components - Multi select, json type
components=Component/s,multi,json,name
# Labels - Multi value, plain Array
labels=Labels,multi,plain,
# xyz - Multi Select List
customfield_13=xyz,multi,json,value
# abc - Checkboxes, multi, json, value  
customfield_11=abc,multi,json,value
# lmn - Date, single, plain
customfield_23=lmn,single,plain,
# si - Cascade Field
customfield_40=Si,cascade,json,value

[jql_section]
jql=issuekey in (DUM-1,DUM-32)
```

## How to Run
* Make sure you have issue_export.config file is ready with JQL for all issues that you want to export.
* .oauthconfig file contains your oAuth token info.
```
(py3env) ➜  issue_export_toolkit git:(master) ✗ python JiraExport.py
DUM-1;Recurring Issue;Chao -> Dam
DUM-2;Testing Economy Blah;
```
* If you want to get csv file, redirect output to file.
```
(py3env) ➜  issue_export_toolkit git:(master) ✗ python JiraExport.py > issues.csv

(py3env) ➜  issue_export_toolkit git:(master) ✗ cat issues.csv
DUM-1;Recurring Issue;Chao -> Dam
DUM-2;Testing Economy Blah;
```

Enjoy :+1: