import os
import sys
import tableauserverclient as TSC

token = os.environ.get('TABLEAU_TOKEN')
if not token:
    print("TABLEAU_TOKEN environment variable needs to be set")
    sys.exit(1)

server_url = os.environ.get('TABLEAU_SERVER_URL')
if not server_url:
    print("TABLEAU_SERVER_URL environment variable needs to be set")
    sys.exit(1)

view_location = os.environ.get('VIEW_FILE_LOCATION')
if not view_location:
    print("VIEW_FILE_LOCATION environment variable needs to be set")
    sys.exit(1)


def list(resource_type):
    # site_id = site to log into, do not specify for default site
    tableau_auth = TSC.PersonalAccessTokenAuth("Slack API Token", token, site_id="")
    server = TSC.Server(server_url, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        endpoint = {
            'workbook': server.workbooks,
            'datasource': server.datasources,
            'view': server.views,
            'job': server.jobs,
            'project': server.projects,
            'webhooks': server.webhooks,
        }.get(resource_type)

        values = []
        for resource in TSC.Pager(endpoint.get):
            values.append(resource.name)
        return values


def generate_report(view_name):
    # site_id = site to log into, do not specify for default site
    tableau_auth = TSC.PersonalAccessTokenAuth("Slack API Token", token, site_id="")
    server = TSC.Server(server_url, use_server_version=True)
    # The new endpoint was introduced in Version 2.5
    server.version = "2.5"

    with server.auth.sign_in(tableau_auth):
        # Query for the view that we want an image of
        req_option = TSC.RequestOptions()
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                         TSC.RequestOptions.Operator.Equals, view_name))
        all_views, pagination_item = server.views.get(req_option)
        if not all_views:
            raise LookupError("View with the specified name was not found.")
        view_item = all_views[0]

        max_age = 1
        if not max_age:
            max_age = 1

        image_req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High,
                                                   maxage=max_age)
        server.views.populate_image(view_item, image_req_option)

        with open("{0}/view.png".format(view_location), "wb") as image_file:
            image_file.write(view_item.image)
