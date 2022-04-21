import prefect
from prefect import Flow, task
from prefect.storage import Docker
from prefect.engine.results import AzureResult

@task
def get_word() -> str:
    return "World"

@task
def say_word(the_word: str) -> None:
    prefect.context.logger.info(the_word)

storage = Docker()
result = AzureResult("results")
with Flow("azure_result_flow", storage=storage, result=result) as flow:
    word = get_word()
    say_word(word)
