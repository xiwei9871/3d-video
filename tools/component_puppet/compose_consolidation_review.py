"""Compose neutral and action before/after comparison sheets with FFmpeg."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ACTIONS = [
    "snake_head_tilt",
    "snake_head_shake",
    "snake_body_sway",
    "snake_bounce",
    "snake_tail_wag",
    "snake_tongue_flick",
]


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--review-dir", required=True, type=Path)
    p.add_argument("--ffmpeg", default="ffmpeg")
    return p.parse_args()


def compose(ffmpeg, inputs, output, columns, rows, cell=384):
    output.parent.mkdir(parents=True, exist_ok=True)
    filter_parts = []
    for index in range(len(inputs)):
        filter_parts.append(f"[{index}:v]scale={cell}:{cell},setsar=1[v{index}]")
    layouts = []
    for index in range(len(inputs)):
        x = (index % columns) * cell
        y = (index // columns) * cell
        layouts.append(f"{x}_{y}")
    filter_parts.append(
        "".join(f"[v{index}]" for index in range(len(inputs)))
        + f"xstack=inputs={len(inputs)}:layout={'|'.join(layouts)}:fill=black[out]"
    )
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "warning", "-y"]
    for path in inputs:
        cmd.extend(["-i", str(path)])
    cmd.extend(["-filter_complex", ";".join(filter_parts), "-map", "[out]", "-frames:v", "1", "-update", "1", str(output)])
    subprocess.run(cmd, check=True)


def main():
    parsed = args()
    review = parsed.review_dir
    compose(
        parsed.ffmpeg,
        [review / "original_neutral.png", review / "consolidated_neutral.png"],
        review / "original_vs_consolidated_neutral.png",
        2,
        1,
        512,
    )
    action_inputs = []
    for action in ACTIONS:
        action_inputs.extend([review / f"original_{action}.png", review / f"consolidated_{action}.png"])
    compose(
        parsed.ffmpeg,
        action_inputs,
        review / "original_vs_consolidated_actions.png",
        2,
        len(ACTIONS),
        384,
    )
    print({"neutral": str(review / "original_vs_consolidated_neutral.png"), "actions": str(review / "original_vs_consolidated_actions.png")})


if __name__ == "__main__":
    main()
