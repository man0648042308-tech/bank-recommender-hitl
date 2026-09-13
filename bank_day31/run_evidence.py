"""运行全部验证并将可提交证据保存为UTF-8文本。"""

from __future__ import annotations

import importlib.metadata
import platform
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def capture(title: str, command: list[str], filename: str) -> None:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    body = (
        f"=== {title} ===\n"
        f"$ {' '.join(command)}\n"
        f"{completed.stdout}"
        f"{completed.stderr}"
        f"\nexit_code={completed.returncode}\n"
    )
    (EVIDENCE / filename).write_text(body, encoding="utf-8")
    print(body)
    if completed.returncode != 0:
        raise SystemExit(f"{title}失败，exit_code={completed.returncode}")


def main() -> None:
    EVIDENCE.mkdir(exist_ok=True)
    environment = (
        f"Python={platform.python_version()}\n"
        f"Executable={sys.executable}\n"
        f"Platform={platform.platform()}\n"
        f"langgraph={importlib.metadata.version('langgraph')}\n"
        f"pytest={importlib.metadata.version('pytest')}\n"
        "外部模型调用=无\n"
        "费用=0元\n"
        "密钥读取=无\n"
    )
    (EVIDENCE / "环境版本.txt").write_text(environment, encoding="utf-8")
    print(environment)

    capture(
        "自动测试",
        [sys.executable, "-m", "pytest", "-q"],
        "全量测试结果.txt",
    )
    capture(
        "Day31完整HITL流程",
        [sys.executable, "-m", "bank_day31.full_bank_hitl"],
        "HITL运行结果.txt",
    )
    print("全部验证通过，证据已写入evidence目录。")


if __name__ == "__main__":
    main()

