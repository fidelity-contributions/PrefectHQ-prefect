import pytest

from prefect import task, flow
from prefect.executors import SyncExecutor, ThreadPoolExecutor, ProcessPoolExecutor


def get_test_flow():
    @task
    def task_a():
        print("Inside task_a.fn")
        return "a"

    @task
    def task_b():
        return "b"

    @flow(version="test")
    def test_flow():
        a = task_a()
        b = task_b()
        return a.result(), b.result()

    return test_flow


@pytest.mark.parametrize(
    "executor",
    [SyncExecutor(), ThreadPoolExecutor(debug=True), ProcessPoolExecutor(debug=True)],
)
def test_flow_run_by_executor(executor):
    test_flow = get_test_flow()
    test_flow.executor = executor

    future = test_flow()
    state = future.result()

    if state.is_failed():
        raise state.data

    assert state.is_completed()
    return_data = state.data
    assert (return_data[0].data, return_data[1].data) == ("a", "b")
