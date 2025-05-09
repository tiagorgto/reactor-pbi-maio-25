from utils import *
import os
import argparse
import glob

current_file = __file__
current_folder = os.path.dirname(current_file)
src_folder = os.path.join(current_folder, "..", "src")

capacity_name = None
workspace_name = 'ReactorPBI'
admin_upns = [None]

semanticmodel_parameters = None
server = None
database = None

# Authentication
auth_login()

# Ensure workspace exists
workspace_id = create_workspace(workspace_name=workspace_name, upns=admin_upns)

# Deploy semantic model
semanticmodel_id = deploy_item(
    "src/Sample.SemanticModel",
    workspace_name=workspace_name,
    find_and_replace={
        (
            r"expressions.tmdl",
            r'(expression\s+SqlServerInstance\s*=\s*)".*?"',
        ): rf'\1"{server}"',
        (
            r"expressions.tmdl",
            r'(expression\s+SqlServerDatabase\s*=\s*)".*?"',
        ): rf'\1"{database}"',
    },
)

# Deploy reports
for report_path in glob.glob("src/*.Report"):
    deploy_item(
        report_path,
        workspace_name=workspace_name,
        find_and_replace={
            ("definition.pbir", r"\{[\s\S]*\}"): json.dumps(
                {
                    "version": "4.0",
                    "datasetReference": {
                        "byConnection": {
                            "connectionString": None,
                            "pbiServiceModelId": None,
                            "pbiModelVirtualServerName": "sobe_wowvirtualserver",
                            "pbiModelDatabaseName": semanticmodel_id,
                            "name": "EntityDataSource",
                            "connectionType": "pbiServiceXmlaStyleLive",
                        }
                    },
                }
            )
        },
    )

#Logoff
auth_logout()

