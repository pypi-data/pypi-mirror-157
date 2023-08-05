"""This module provides the CLI."""
# cli-module/cli.py
import json
from typing import List, Optional
from polygon import rest_connect

import typer

app = typer.Typer()


@app.command()
def list():
    """Example :\n
               Run "polygon container list" to get the list of container's in the account """
    typer.echo(f"list")
    #call the endpoint to get list of clod containers
    #rest-connect with the json
    containerList=rest_connect.containerList()
    print(json.dumps(containerList, indent=3))


@app.command()
def add(cloudstoragename:str = typer.Option("None","--cloudstoragename","--n"),
    cloudtype: str = typer.Option("None","--cloudtype",),
    authentication: str = typer.Option("None","--authentication",),
    containername: str = typer.Option("None","--containername",),
    bucketname: str = typer.Option("None","--bucketname",),
    accontname: str = typer.Option("None","--accontname",),
    accesskey: str = typer.Option("None","--accesskey",),
    secretid: str = typer.Option("None","--secretid",),
    sastoken: str = typer.Option("None","--sastoken",),
    manifestjson: str = typer.Option("None","--manifestjson",),
    region: str = typer.Option("None","--region",),
) -> None:
    """Example :\n
            --To add AWS s3 with account athentication : polygon container add --cloudstoragename="<name for cloud storage (users choice)>"  --cloudtype="aws_s3"  --authentication="account_authentication" --bucketname="<aws s3 bucket name>"  --accesskey="<aws accont secret key>" --secretid="<aws account secret ID>" --region="<region which the bucket belongs to>"\n
            --To add AWS s3 with annonymous access : polygon container add --cloudstoragename="<name for cloud storage (users choice)>"  --cloudtype="aws_s3"  --authentication="annonymous_access" --bucketname="<aws s3 bucket name with public access>" --manifestjson="manifest.json" --region="<aws region which the bucket belongs to>"\n
            --To add azure container with account athentication : polygon container add --cloudstoragename="<name for cloud storage (users choice)>"  --cloudtype="azure_container"  --authentication="account_authentication" --containername="<azure container name>" --accontname="<account name>" --sastoken="<azure SAS token with list, read access>"\n
            --To add azure container with annonymous access : polygon container add --cloudstoragename="<name for cloud storage (users choice)>"  --cloudtype="azure_container"  --authentication="annonymous_access" --containername="<azure container name with annonymous access of read list>" --accontname="<account name>"

                """
    if (cloudtype == "aws_s3" and authentication == "account_authentication"):
        if (bucketname == "None" or accesskey == "None" or secretid == "None" or region == "None"):
            print("Please provide proper cloud details'")
        else:
            dataseDetails=rest_connect.createContainer(cloudstoragename,cloudtype,authentication,containername,bucketname,
                                                   accontname,accesskey,secretid,sastoken,manifestjson,region)
            print(dataseDetails)
    if (cloudtype == "aws_s3" and authentication == "annonymous_access"):
        if (bucketname == "None" or manifestjson == "None" or region == "None"):
            print("Please provide proper cloud details'")
        else:
            dataseDetails = rest_connect.createContainer(cloudstoragename, cloudtype, authentication, containername,
                                                       bucketname,
                                                       accontname, accesskey, secretid, sastoken, manifestjson, region)
            print(dataseDetails)
    if (cloudtype == "azure_container" and authentication == "account_authentication"):
        if (containername == "None" or accontname == "None" or sastoken == "None"):
            print("Please provide proper cloud details'")
        else:
            dataseDetails = rest_connect.createContainer(cloudstoragename, cloudtype, authentication, containername,
                                                       bucketname,
                                                       accontname, accesskey, secretid, sastoken, manifestjson, region)
            print(dataseDetails)
    if (cloudtype == "azure_container" and authentication == "annonymous_access"):
        if (containername == "None" or accontname == "None"):
            print("Please provide proper cloud details'")
        else:
            dataseDetails = rest_connect.createContainer(cloudstoragename, cloudtype, authentication, containername,
                                                       bucketname,
                                                       accontname, accesskey, secretid, sastoken, manifestjson, region)
            print(dataseDetails)

@app.command()
def details(cloudstoragename:str = typer.Option("None","--cloudstoragename",),
    cloudstorageid: str = typer.Option("None","--cloudstorageid",),
) -> None:
    """Example :\n
           --With container id : polygon container details --cloudstorageid="<container id to get the details>"\n
           --With container name : polygon container details --cloudstoragename="<container name to get the details>"
               """
    datasetDetails = rest_connect.container_details(cloudstoragename, cloudstorageid)
    print(datasetDetails)


@app.command()
def delete(name:str = typer.Option("None","--name","--n"),
    id: str = typer.Option("None","--id",),
) -> None:
    """Example :\n
            --With container id : polygon container delete --id="<container id to be delete>"\n
            --With container name : polygon container delete --name="<container name to be delete>"
                """
    datasetDetails = rest_connect.delete_container(name, id)
    print(datasetDetails)


if __name__ == "__main__":
    app()
