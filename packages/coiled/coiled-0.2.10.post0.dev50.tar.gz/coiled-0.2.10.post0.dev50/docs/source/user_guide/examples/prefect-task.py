import coiled
import dask.dataframe as dd
import prefect
from dask.distributed import Client
from prefect import Flow, task


@task
def load_data():
    """Load some data"""
    return dd.read_parquet(
        "s3://nyc-tlc/trip data/yellow_tripdata_2019-*.parquet",
        columns=["passenger_count", "tip_amount"],
        storage_options={"anon": True},
        filters=[[("passenger_count", ">", 2)]],
    )


@task
def summarize(df):
    """Compute a summary table"""
    return (
        df.groupby("passenger_count").tip_amount.agg(["min", "max", "mean"]).compute()
    )


@task
def log_summary(df):
    """Log summary result"""
    logger = prefect.context.get("logger")
    logger.info(df)


with Flow(name="taxi-tips") as flow:
    with coiled.Cluster(
        "prefect-example", n_workers=5, software="prefect-example"
    ) as cluster:
        # These tasks rely on a Coiled cluster to run,
        # so you can create them inside the context manager
        client = Client(cluster)
        df = load_data()
        summary = summarize(df)
    # This task doesn't rely on the Coiled cluster to run
    # so it can be outside the context manager
    log_summary(summary)

# run the flow
flow.run()

# To use with Prefect Cloud or Prefect Server:
# Register the flow under your project
# flow.register(project_name="<project-name>")
