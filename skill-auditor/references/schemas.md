# JSON Schemas

This document defines the JSON schemas used by skill-auditor.

---

## evals.json

Defines the evals for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "skill-auditor",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": [],
      "expectations": [
        "The audit report includes all 12 sections",
        "The skill detected encoding issues"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable statements

---

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The audit report includes all 12 sections",
      "passed": true,
      "evidence": "Found in transcript: 'Section 1: Basic Structure... Section 12: Output Quality'"
    },
    {
      "text": "The audit detected encoding issues",
      "passed": false,
      "evidence": "No encoding issues were reported in the output"
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 1,
    "total": 2,
    "pass_rate": 0.5
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Bash": 3
    },
    "total_tool_calls": 8,
    "total_steps": 4,
    "errors_encountered": 0,
    "output_chars": 5250,
    "transcript_chars": 1800
  },
  "timing": {
    "executor_duration_seconds": 45.0,
    "grader_duration_seconds": 12.0,
    "total_duration_seconds": 57.0
  },
  "claims": [
    {
      "claim": "The target skill has proper encoding",
      "type": "quality",
      "verified": true,
      "evidence": "Encoding check passed for all Python files"
    }
  ],
  "eval_feedback": {
    "suggestions": [],
    "overall": "Assertions are appropriate for the audit task"
  }
}
```

**Fields:**
- `expectations[]`: Graded expectations with evidence
- `summary`: Aggregate pass/fail counts
- `execution_metrics`: Tool usage and output size
- `timing`: Wall clock timing
- `claims`: Extracted and verified claims from the output
- `eval_feedback`: Improvement suggestions for the evals

---

## benchmark.json

Output from benchmark mode. Located at `<benchmark-dir>/benchmark.json`.

```json
{
  "metadata": {
    "skill_name": "skill-auditor",
    "skill_path": "/path/to/skill-auditor",
    "executor_model": "<model-name>",
    "analyzer_model": "<model-name>",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Basic Audit",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": []
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": []
}
```

**Important:** The viewer reads these field names exactly. Using `config` instead of `configuration`, or putting `pass_rate` at the top level of a run instead of nested under `result`, will cause the viewer to show empty/zero values.

---

## eval_metadata.json

Metadata for a single eval run. Located at `<eval-dir>/eval_metadata.json`.

```json
{
  "eval_id": 1,
  "eval_name": "basic-audit",
  "prompt": "Audit the skill-installer skill to check if it meets all compliance standards",
  "assertions": [
    {
      "text": "The audit report includes all 12 sections",
      "type": "contains"
    },
    {
      "text": "The audit detected encoding issues",
      "type": "contains"
    }
  ]
}
```

---

## timing.json

Wall clock timing for a run. Located at `<run-dir>/timing.json`.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## feedback.json

User feedback from the eval viewer. Located at `<workspace>/feedback.json`.

```json
{
  "reviews": [
    {
      "run_id": "eval-0-with_skill",
      "feedback": "The audit report is comprehensive but missing some security checks",
      "timestamp": "2026-01-15T10:35:00Z"
    },
    {
      "run_id": "eval-1-with_skill",
      "feedback": "",
      "timestamp": "2026-01-15T10:36:00Z"
    }
  ],
  "status": "complete"
}
```

**Fields:**
- `reviews[]`: List of feedback entries
  - `run_id`: Identifier for the run (e.g., "eval-0-with_skill")
  - `feedback`: User's feedback text (empty string means no issues)
  - `timestamp`: ISO timestamp of when feedback was saved
- `status`: "in_progress" or "complete"
