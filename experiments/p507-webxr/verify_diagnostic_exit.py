"""Real diagnostic CLI negative regression; original frozen inputs remain read-only."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact-dir', type=Path, required=True)
    ap.add_argument('--blender-dir', type=Path, required=True)
    ap.add_argument('--three-report', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    original = json.loads(args.three_report.read_text(encoding='utf-8'))
    results = []
    for mode in ('matching', 'manual-mismatch', 'box3-mismatch'):
        three = json.loads(json.dumps(original))
        if mode == 'manual-mismatch':
            three['union_bounds_gltf'][0] += .01
        if mode == 'box3-mismatch':
            three['box3_vs_manual_max_delta_m'] = .01
        injected = args.output_dir / (mode + '-three.json')
        output = args.output_dir / (mode + '-diagnostic.json')
        injected.write_text(json.dumps(three), encoding='utf-8')
        proc = subprocess.run([sys.executable, str(HERE/'diagnose_tv_bounds.py'),
            '--artifact-dir', str(args.artifact_dir), '--blender-dir', str(args.blender_dir),
            '--three-report', str(injected), '--output', str(output), '--require-original-version'],
            capture_output=True, text=True)
        assert output.is_file(), (mode, proc.returncode, proc.stdout, proc.stderr)
        report = json.loads(output.read_text(encoding='utf-8'))
        expected = 'ROOT_CAUSE_CONFIRMED' if mode == 'matching' else 'ROOT_CAUSE_UNRESOLVED'
        assert report['conclusion'] == expected, (mode, report['conclusion'], proc.stderr)
        assert proc.returncode == (0 if mode == 'matching' else 1), (mode, proc.returncode)
        results.append({'case':mode, 'conclusion':report['conclusion'], 'exit_code':proc.returncode,
                        'head':report['experiment_head'], 'dirty':report['work_tree_dirty']})
    summary = {'result':'PASS', 'cases':results}
    (args.output_dir/'exit-regression-report.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
