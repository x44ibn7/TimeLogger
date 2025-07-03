import os
import sys
import time
from datetime import datetime, timedelta

# Always use the directory of the executable or script for data files
if getattr(sys, 'frozen', False):
    BASEDIR = os.path.dirname(sys.executable)
else:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))

TASKS_FILE = os.path.join(BASEDIR, "tasks.txt")
LOG_FILE = os.path.join(BASEDIR, "logfile.txt")
WORK_HOURS = 8 * 60 * 60  # 8 hours in seconds


def load_tasks():
    with open(TASKS_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]


def parse_time_str(timestr):
    # timestr is like '0:00:12' or '00:00:12'
    parts = timestr.strip().split(':')
    if len(parts) == 3:
        h, m, s = map(int, parts)
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = map(int, parts)
        return m * 60 + s
    else:
        return int(parts[0])


def load_log():
    if not os.path.exists(LOG_FILE):
        return {}
    log = {}
    with open(LOG_FILE, "r") as f:
        date = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Accept header lines with or without '|'
            if (not line.startswith('#')) and (line.count('-') == 2 and len(line) <= 12):
                # Header line: 2025-07-03
                date = line.strip()
                log[date] = {"tasks": {}}
            elif line.startswith('#') and ':' in line:
                # Per-task line: #   TASK: 0:00:12 ...
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    task_part, rest = parts
                    task = task_part.strip()
                    time_str = rest.strip().split(' ', 1)[0]
                    seconds = parse_time_str(time_str)
                    if date and task:
                        log[date]["tasks"][task] = seconds
    return log


def save_log(log):
    with open(LOG_FILE, "w") as f:
        for date in sorted(log.keys()):
            f.write(f"{date}\n")
            total = sum(log[date]["tasks"].values())
            percent = total / WORK_HOURS * 100
            f.write(f"TOTAL: {format_time(total)} ({format_time(total)}/08:00:00) {percent:.1f}%\n")
            for task, seconds in log[date]["tasks"].items():
                tpercent = seconds / WORK_HOURS * 100
                f.write(f"#   {task}: {format_time(seconds)} ({format_time(seconds)}/08:00:00) {tpercent:.1f}%\n")


def save_csv_log(log):
    csv_file = LOG_FILE.replace('.txt', '.csv')
    with open(csv_file, "w") as f:
        f.write("date,task,seconds,percentage\n")
        for date in sorted(log.keys()):
            for task, seconds in log[date]["tasks"].items():
                percent = seconds / WORK_HOURS * 100
                f.write(f"{date},{task},{seconds},{percent:.2f}\n")


def format_time(seconds):
    return str(timedelta(seconds=seconds))


def main():
    tasks = load_tasks()
    log = load_log()
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in log:
        log[today] = {"tasks": {}}
    timers = log[today]["tasks"]
    for task in tasks:
        if task not in timers:
            timers[task] = 0
    session_timers = {task: 0 for task in tasks}
    active_task = None
    paused = False
    last_tick = time.time()
    last_autosave = time.time()
    error_message = ""
    print("Press Ctrl+C to stop tracking and save.")
    try:
        while True:
            # Clear the terminal at the very start of each loop
            os.system('clear' if os.name != 'nt' else 'cls')
            sys.stdout.flush()
            if error_message:
                print(error_message)
                error_message = ""
            now = datetime.now()
            print(f"{today} | {now.strftime('%H:%M:%S')}")
            total = sum(timers[task] + session_timers[task] for task in tasks)
            percent = total / WORK_HOURS * 100
            print(f"\nTotal time: {format_time(total)} / 8:00:00 ({percent:.1f}%)")
            for task in tasks:
                t = timers[task] + session_timers[task]
                tpercent = t / WORK_HOURS * 100
                print(f"  {task}: {format_time(t)} ({tpercent:.1f}%)")
            print(f"\nCurrent task: {active_task if active_task else 'None'} {'[PAUSED]' if paused else ''}")
            print("\nOptions:")
            for i, task in enumerate(tasks):
                print(f"{i+1}. Switch to {task}")
            print(f"P. Pause/Resume current task")
            print(f"Q. Quit and save")
            now_tick = time.time()
            if active_task and not paused:
                session_timers[active_task] += int(now_tick - last_tick)
            last_tick = now_tick
            # Autosave every 5 minutes
            if now_tick - last_autosave >= 300:
                for task in tasks:
                    timers[task] += session_timers[task]
                    session_timers[task] = 0
                save_log(log)
                save_csv_log(log)
                last_autosave = now_tick
            print("\nSelect option (number, P, Q): ", end='', flush=True)
            key = None
            if os.name == 'nt':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
            else:
                import select
                import termios
                import tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setcbreak(fd)
                    rlist, _, _ = select.select([fd], [], [], 1)
                    if rlist:
                        key = sys.stdin.read(1).lower()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            if key:
                if key == 'q':
                    break
                elif key == 'p':
                    paused = not paused
                elif key.isdigit() and 1 <= int(key) <= len(tasks):
                    active_task = tasks[int(key)-1]
                    paused = False
                else:
                    error_message = "Invalid input."
    except KeyboardInterrupt:
        pass
    # On exit, add only the remaining session_timers to timers
    for task in tasks:
        timers[task] += session_timers[task]
        session_timers[task] = 0
    print("\nStopping and saving log...")
    save_log(log)
    save_csv_log(log)
    print("Log saved to logfile.txt and logfile.csv.")

if __name__ == "__main__":
    main()
