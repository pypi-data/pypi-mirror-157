from collections import OrderedDict
from datetime import datetime
import csv
from typing import Dict, List

import requests
import typer
from rich import pretty
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

custom_theme = Theme({"info": "dim cyan", "warning": "magenta", "error": "bold red"})
console = Console(theme=custom_theme)

pretty.install()


def get_data(service: str, shopify_token: str):
    headers = {"X-Shopify-Access-Token": shopify_token}
    api_url = "https://flightsong.myshopify.com/admin/api/2021-07/{}.json"
    try:
        res = requests.get(api_url.format(service), headers=headers)
        data = res.json()[service]
        return data
    except Exception as e:
        typer.secho("Got an error when getting data from the Shopify API", err=True)
        raise typer.Exit(1) from e


def has_kennitala(item):
    try:
        return (
            item["note_attributes"][0]["value"].isdigit()
            and item["note_attributes"][0]["name"] == "kennitala"
        )
    except Exception:
        return False


def get_claims_data(data: List[Dict]):
    data = [
        {
            "kennitala": item["note_attributes"][0]["value"],
            "amount": item["current_subtotal_price"],
        }
        for item in data
        if has_kennitala(item)
    ]
    return data


def get_stats(data: Dict):
    stats = {
        "orders": str(len(data)),
        "taxes": str(sum(int(item["current_total_tax"]) for item in data)),
        "income": str(sum(int(item["current_subtotal_price"]) for item in data)),
        "kennitala": f"{len(get_claims_data(data))}/{len(data)}",
    }
    table = Table(*stats.keys(), title="Flightsong quickstats")
    table.add_row(*stats.values())

    return table


def get_orders(data: Dict):
    customers = [
        OrderedDict(
            {
                "name": item["customer"]["default_address"]["name"],
                "email": item["customer"]["email"],
                "phone": item["customer"]["phone"],
                "order": item["customer"]["last_order_name"],
                "address": item["customer"]["default_address"]["address1"],
                "city": item["customer"]["default_address"]["city"],
                "zip": item["customer"]["default_address"]["zip"],
                "amount": item["customer"]["total_spent"],
            }
        )
        for item in data
    ]
    col_headers = customers[0].keys()
    table = Table(*col_headers, title="All orders")

    for customer in customers:
        table.add_row(*customer.values())

    return table


def create_csv(data: Dict):
    csv_filename = f"konto-claims-{datetime.now().timestamp()}.csv"
    claims_data = get_claims_data(data)
    console.print(f"Writing the following claims data to {csv_filename}", style="info")
    console.print(claims_data)
    with open(
        csv_filename,
        "w",
        encoding="UTF8",
        newline="",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=["kennitala", "amount"])
        writer.writeheader()
        writer.writerows(claims_data)
