import pathlib

import click
import toml as toml_

from ._site import Site

from netlink.logging import logger
logger.set_level(logger.WARNING)


@click.command()
@click.option('-u', '--url', help='Sharepoint URL')
@click.option('-i', '--id', help='Client ID')
@click.option('-s', '--secret', help='Client Secret')
@click.option('-t', '--toml', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),  help="TOML file with 'url', 'id', and 'secret'")
@click.option('-f', '--fields', is_flag=True, help='include fields')
@click.option('--hidden', is_flag=True, help='include hidden lists')
@click.argument('name', nargs=-1)
def print_list_info(name, url, id, secret, toml, fields, hidden):
    """Print information about SharePoint List(s)

    If NAME is not provided, all lists are returned.

    """
    if toml is not None:
        with toml.open('r', encoding='utf-8-sig') as f:
            d = toml_.load(f)
        url, id, secret = d['url'], d['id'], d['secret']
    if url is None or id is None or secret is None:
        raise click.UsageError("Essential options missing. Either provide 'url', 'id', and 'secret', or a "
                               "respective 'toml'-file.")
    site = Site(url=url, client_id=id, client_secret=secret)
    for i in site.get_lists(hidden=hidden):
        if name:
            if i.title not in name:
                continue
        print(i.title)
        if fields:
            for j in site.get_list_columns(name=i.title, hidden=hidden):
                print(
                    f"    {j.title:25}  {j.type_as_string:10}  {j.internal_name}{'Id' if j.type_as_string in ('User', 'Lookup') else ''}")
            print()
