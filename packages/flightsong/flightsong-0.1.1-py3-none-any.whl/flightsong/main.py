from types import SimpleNamespace
import typer

from flightsong.utils import get_data, get_orders, get_stats, create_csv, console

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main(
    ctx: typer.Context,
    shopify_token: str = typer.Option(None, envvar="SHOPIFY_TOKEN"),
):
    """
    Flightsong toolkit

    Just some handy commands for the shop
    """

    if not shopify_token:
        print(
            "Missing shopify-token; pass --shopify-token or export SHOPIFY_TOKEN in your terminal"
        )
        raise typer.Exit(1)
    ctx.obj = SimpleNamespace(shopify_token=shopify_token)


@app.command(name="stats")
def cmd_stats(ctx: typer.Context):
    data = get_data("orders", ctx.obj.shopify_token)
    stats_data = get_stats(data)
    console.print(stats_data)


@app.command(name="orders")
def cmd_orders(ctx: typer.Context):
    data = get_data("orders", ctx.obj.shopify_token)
    customers_data = get_orders(data)
    console.print(customers_data)


@app.command(name="konto")
def cmd_konto(ctx: typer.Context):
    data = get_data("orders", ctx.obj.shopify_token)
    create_csv(data)


@app.command(name="api")
def cmd_api(ctx: typer.Context):
    data = get_data("orders", ctx.obj.shopify_token)
    console.print_json(data=data)
