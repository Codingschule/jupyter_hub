import os, json, time, subprocess, shlex
from pathlib import Path
from watchfiles import watch
import yaml

COURSE_DIR = Path(os.environ["COURSE_DIR"])
WATCH_DIR  = Path(os.environ["RUNNER_WATCH_DIR"])
CONFIG     = Path(os.environ["RUNNER_CONFIG"])
OUTDIR     = Path(os.environ["RUNNER_OUTDIR"])
OUTDIR.mkdir(parents=True, exist_ok=True)
STATUS_JSON = OUTDIR / 'status.json'

def load_cfg():
    if CONFIG.exists():
        with open(CONFIG, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

def run_step(step, idx):
    name = step.get('name', f'step-{idx}')
    cmd  = step.get('run')
    shell= step.get('shell', False)
    cont = step.get('continue_on_error', False)
    if not cmd: 
        return {'name': name, 'skipped': True, 'ok': True}
    logfile = OUTDIR / f'{idx:02d}_{name}.log'
    t0 = time.time()
    ok = True
    try:
        with open(logfile, 'wb') as lf:
            proc = subprocess.run(
                cmd if shell else shlex.split(cmd),
                cwd=WATCH_DIR, stdout=lf, stderr=subprocess.STDOUT,
                shell=shell, check=False, text=False
            )
        ok = (proc.returncode == 0)
    except Exception as e:
        ok = False
        with open(logfile, 'ab') as lf:
            lf.write(f'\n[runner] Exception: {e}\n'.encode('utf-8'))
    return {'name': name, 'cmd': cmd, 'ok': ok, 'continue_on_error': cont, 'log': str(logfile), 'secs': round(time.time()-t0,3)}

def execute_pipeline():
    steps = load_cfg().get('steps', [])
    results = []
    for i, step in enumerate(steps, 1):
        res = run_step(step, i)
        results.append(res)
        if not res['ok'] and not res['continue_on_error']:
            break
    STATUS_JSON.write_text(json.dumps({'results': results, 'ts': time.time()}, ensure_ascii=False, indent=2), encoding='utf-8')

def first_run(): execute_pipeline()
def watch_loop():
    for _ in watch(WATCH_DIR, stop_event=None):
        execute_pipeline()

if __name__ == '__main__':
    first_run()
    watch_loop()
