import click
import pathlib
from loguru import logger

from dataicer import ice, deice, register_handlers, DirectoryHandler

from . import (
    load_summary_df,
    get_ecl_deck,
    get_summary_keys,
    get_ecl_property_keys,
    get_restart_reports,
    EclDeck,
    __version__,
)


ELASTIC_INIT = ["PORV", "PORO", "NTG", "SATNUM"]
ELASTIC_RST = ["PRESSURE", "SWAT", "SGAS", "RS"]


@click.group()
@click.version_option(__version__)
def main():
    pass


@main.command()
@click.argument("file", nargs=1, type=click.STRING)
@click.argument("curves", nargs=-1, type=click.STRING)
@click.option("-k", "--keys", help="Print keys in file.", is_flag=True, default=False)
@click.option("-csv", help="Export to csv file.", nargs=1)
@click.option("-hdf", help="Export to hdf file.", nargs=1)
def summary(file, curves, keys, csv, hdf):
    """Export the summary data as a table."""
    deck = get_ecl_deck(file)

    has_curves = get_summary_keys(deck["SUM"][0])

    if keys:
        print(has_curves)
        raise SystemExit

    sumdf = load_summary_df(deck["SUM"][0], curves=curves)

    if csv:
        sumdf.to_csv(csv)

    if hdf:
        sumdf.to_hdf(hdf)

    if not csv and not hdf:
        print(sumdf)


@main.command()
@click.argument("file", nargs=1, type=click.STRING)
def report(file):
    """[summary]"""
    deck = get_ecl_deck(file)

    click.secho("Parent Directory:", fg="green")
    click.secho(deck["DATA"][0].parent)

    for dt, locs in deck.items():
        click.secho(f"{dt} FILES:", fg="green")
        click.secho([l.name for l in locs])

    has_curves = get_summary_keys(deck["SUM"][0])

    click.secho("\nSummary Curves:", fg="blue")
    click.secho(has_curves)

    has_init_keys = get_ecl_property_keys(deck["INIT"][0])

    click.secho("\nINIT Keys:", fg="blue")
    click.secho(has_init_keys)

    has_rst_keys = get_ecl_property_keys(deck["RST"][0])

    click.secho("\nRST Keys:", fg="blue")
    click.secho(has_rst_keys)

    reports = get_restart_reports(deck["RST"][0])

    click.secho("\nRST Reports:", fg="blue")
    click.secho(reports)


@main.command()
@click.argument("file", nargs=1, type=click.STRING)
@click.option(
    "-d",
    "--export-dir",
    help="export directory if not supplied output location will be the model directory",
    default=None,
)
@click.option(
    "-ts",
    "--time-steps",
    help="choose report time steps for output e.g. '-ts=0,10'; to get "
    "report numbers use 'eclx reports <model>` and select "
    "the numbers from the 'report' column.",
    default=None,
    type=click.STRING,
)
@click.option(
    "-e",
    "--elastic",
    is_flag=True,
    default=False,
    help="Load and output only KW necessary for sim2seis and sim2imp",
)
@click.option(
    "-ki",
    "--keys_init",
    help="INIT Keys for export as comma separated list.",
    default=None,
    type=click.STRING,
)
@click.option(
    "-kr",
    "--keys_rst",
    help="RESTART Keys for export as comma separated list.",
    default=None,
    type=click.STRING,
)
@click.option(
    "--flip_hand",
    is_flag=True,
    default=False,
    help="Flip the handedness of the simulation grid. This is "
    "equivalent to reversing the cell numbering in the J "
    "direction.",
)
@click.option(
    "-V", "--verbose", is_flag=True, default=False, help="Enable additional output"
)
def simx(
    file,
    export_dir,
    time_steps,
    elastic,
    keys_init,
    keys_rst,
    flip_hand,
    csv,
    csv_delim,
    verbose,
):
    """Export the grid and simulation results as"""
    deck = get_ecl_deck(file)

    if verbose:
        click.secho("Parent Directory:", fg="green")
        try:
            click.secho(deck["DATA"][0].parent)
        except IndexError:
            click.secho("DATA file does not exist", fg="red")
            raise SystemExit

        for dt, locs in deck.items():
            click.secho(f"{dt} FILES:", fg="green")
            click.secho([l.name for l in locs])

    file = pathlib.Path(file)
    if export_dir is None:
        export_dir = file.parent / file.stem
    else:
        export_dir = pathlib.Path(export_dir)

    assert export_dir.parent.exists()

    sim = EclDeck(silent=~verbose)
    try:
        sim.set_grid(deck["GRID"][0])
        sim.set_init(deck["INIT"][0])
        sim.set_rst(deck["RST"][0])
    except IndexError as e:
        click.secho("Could not find input files, check with '-V'", err=True, fg="red")
        raise SystemExit

    if time_steps is None:
        time_steps_str = map(str, sim.reports)
        time_steps = sim.reports
    else:
        time_steps_str = time_steps.split(",")
        time_steps = map(int, time_steps_str)
        # check timesteps in sim.reports

    if keys_init is not None:
        keys_init = list(keys_init.split(","))
        # check all keys_init in keys

    if elastic and keys_init is not None:
        keys_init += ELASTIC_INIT
    elif elastic:
        keys_init = ELASTIC_INIT
    else:
        keys_init = get_ecl_property_keys(deck["INIT"][0])

    if keys_rst is not None:
        keys_rst = list(keys_rst.split(","))
        # check all keys_rst in keys

    if elastic and keys_rst is not None:
        keys_rst += ELASTIC_RST
    elif elastic:
        keys_rst = ELASTIC_RST
    else:
        keys_rst = get_ecl_property_keys(deck["RST"][0])

    if verbose:
        click.secho("Loading Summary:", fg="blue")
        click.secho("Loading time steps: " + ", ".join(time_steps_str))
        click.secho(keys_init)
        click.secho(keys_rst)

    sim.load_grid()
    sim.load_init(keys=keys_init)
    sim.load_rst(reports=list(time_steps), keys=keys_rst)

    if not csv:
        dh = DirectoryHandler(export_dir, mode="w")
        register_handlers(dh, numpy="txt", xarray="nc", pandas="h5")

        ice(dh, eclxsim=sim)
