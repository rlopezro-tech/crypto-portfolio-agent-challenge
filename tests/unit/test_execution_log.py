import json

from app.core.execution_log import ExecutionLogRecorder


def test_execution_log_recorder_writes_jsonl_event(tmp_path) -> None:
    recorder = ExecutionLogRecorder(log_dir=str(tmp_path), enabled=True)

    execution_id = recorder.record(
        route="POST /api/v1/recommendations",
        request={"message": "Invest $1000 in low risk crypto."},
        status="success",
        response={"total_allocated_usd": "1000.00"},
    )

    log_files = list(tmp_path.glob("executions-*.jsonl"))
    assert len(log_files) == 1

    event = json.loads(log_files[0].read_text(encoding="utf-8").strip())
    assert event["execution_id"] == execution_id
    assert event["route"] == "POST /api/v1/recommendations"
    assert event["request"]["message"] == "Invest $1000 in low risk crypto."
    assert event["response"]["total_allocated_usd"] == "1000.00"


def test_execution_log_recorder_redacts_sensitive_fields(tmp_path) -> None:
    recorder = ExecutionLogRecorder(log_dir=str(tmp_path), enabled=True)

    recorder.record(
        route="POST /api/v1/recommendations",
        request={"message": "hello", "api_key": "secret-value"},
        status="error",
        error={"authorization": "Bearer secret-value"},
    )

    log_file = next(tmp_path.glob("executions-*.jsonl"))
    event = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert event["request"]["api_key"] == "[REDACTED]"
    assert event["error"]["authorization"] == "[REDACTED]"
