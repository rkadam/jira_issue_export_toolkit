'''
Reference: Using Python Jira Client library - https://jira.readthedocs.io/en/master/index.html

Pre Requisitie:
* Python 3
* OAuth token is available to use
* *config* directory in this repo contains
** ".oauthconfig" file.
** "oauth.pem" - location of RSA private key file
** "issue_export.config" file which contains JQL and columns that you need to export for Issues.

➜  ~ cat .oauthconfig
[oauth_token_config]
oauth_token=<oauth token>
oauth_token_secret=<oauth token secret>
consumer_key=<consumer key>
user_private_key_file_name=<private key file path>

[server_info]
jira_base_url=<jira base url>


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
'''

from configparser import SafeConfigParser
from pathlib import Path

from jira import JIRA

def get_oauth(oauth_setup_config):

    key_cert_data = None
    key_cert_file_name = oauth_setup_config.get("oauth_token_config", "user_private_key_file_name")
    key_cert_file_path = Path.cwd() / f"config/{key_cert_file_name}"

    with open (key_cert_file_path, 'r') as key_cert_file:
        key_cert_data = key_cert_file.read()
        
    oauth_dict = {
        'access_token' : oauth_setup_config.get("oauth_token_config", "oauth_token"),
        'access_token_secret': oauth_setup_config.get("oauth_token_config", "oauth_token_secret"),
        'consumer_key': oauth_setup_config.get("oauth_token_config", "consumer_key"),
        'key_cert': key_cert_data
    }

    return oauth_dict

def get_config_details(i_filepath):
    config_parser = SafeConfigParser()
    config_parser.optionxform=str          # Read config file as case insensitive
    config_parser.read(i_filepath)
    return config_parser

def read_issue_field_config(i_fieldpath):
    config_parser = get_config_details(i_fieldpath)
    issue_export_config_dict = {}
    field_config_dict = {}

    for internal_field_name, field_details in config_parser.items("issue_field_config_section"):
        #print(f"name: {internal_field_name}, value: {field_details}")
        
        params = field_details.split(",")
        display_field_name = params[0].strip().lower() if params[0] else ""
        field_type = params[1].strip().lower() if params[1] else ""
        output_type = params[2].strip().lower() if params[2] else ""
        access_key = params[3].strip().lower() if params[3] else ""

        field_config_dict[internal_field_name] = {
            'display_field_name': display_field_name,
            'field_type': field_type,
            'output_type': output_type,
            'access_key': access_key
        }
        
    issue_export_config_dict["field_config_dict"] = field_config_dict

    jql = config_parser.get("jql_section", "jql")
    issue_export_config_dict["jql"] = jql

    return issue_export_config_dict
    
def reterive_issues(jira_session,
                    issue_export_config_dict,
                    max_results_per_page,
                    start_at,
                    total_issue_count):
    jql = issue_export_config_dict["jql"]
    field_config_dict = issue_export_config_dict["field_config_dict"]
    # Get list of fields that we need to fetch
    fields = list(field_config_dict.keys())

    # Get handle to CSV file to which write data.
    # ToDo

    while start_at < total_issue_count:    
        json_result = jira_session.search_issues(jql,
                                     startAt = start_at,
                                     maxResults = max_results_per_page,
                                     fields = fields,
                                     json_result = True)
        total_issue_count = json_result['total']
        start_at = start_at + max_results_per_page

        issue_export_data = []
        for issue in json_result['issues']:
            issue_field_value_list=[]
            issue_field_value_list.append(issue["key"])

            for field in fields:
                field_config = field_config_dict[field]
                if field_config['field_type'] == 'single':
                    if field_config['output_type'] == 'plain':
                        value = issue["fields"][field] if issue["fields"][field] else ""
                    elif field_config['output_type'] == 'json':
                        access_key = field_config['access_key']
                        value = issue["fields"][field][access_key] if issue["fields"][field][access_key] else ""
                elif field_config['field_type'] == 'multi':
                    if field_config['output_type'] == 'json':
                        access_key = field_config['access_key']
                        json_list = issue['fields'][field]
                        value = ",".join([json_item[access_key] for json_item in json_list]) if json_list else ""
                    elif field_config['output_type'] == 'plain':
                        value = ",".join(issue['fields'][field]) if issue['fields'][field] else ""
                elif field_config['field_type'] == 'cascade':
                    access_key = field_config['access_key']
                    # Output should always be in json, so we will ignore "output_type" parameter from config!
                    # Main value
                    value = issue["fields"][field][access_key] if issue["fields"][field] else ""
                    # if we got value in parent dropdown, check if there is any value in child dropdown.
                    if value and ("child" in issue["fields"][field]) :
                        child_value = issue["fields"][field]["child"]["value"]
                        value = value + " -> " + child_value
                
                issue_field_value_list.append(value)        
            print (';'.join(issue_field_value_list))
            issue_export_data.append(';'.join(issue_field_value_list))
        # Write Data to csv file every iteration.
        # To Do csvfile.write

def main():
    max_results_per_page = 50
    start_at = 0
    total_issue_count = max_results_per_page

    # Read oAuth configuration file from config directory in this repo.
    oauth_config_file = Path.cwd() / "config/.oauthconfig"
    oauth_setup_config = get_config_details(oauth_config_file)

    jira_base_url = oauth_setup_config.get("server_info", "jira_base_url")
    oauth_dict = get_oauth(oauth_setup_config)

    # Expecting issue_export.config file to be in same directory as this python script.
    field_config_dict = read_issue_field_config(Path.cwd() / "config/issue_export.config")

    ajira = JIRA(oauth=oauth_dict, server = jira_base_url)
    reterive_issues(ajira, field_config_dict, max_results_per_page, start_at, total_issue_count)

if __name__ == "__main__":
    main()