# TimeLogger

A simple, cross-platform terminal time tracking app for Windows and macOS.

## Features
- Track time spent on tasks loaded from `tasks.txt`
- Switch between tasks instantly with a single keypress
- Pause/resume tracking
- Live updating terminal UI
- Autosaves every 5 minutes to prevent data loss
- Logs daily totals and per-task times to `logfile.txt` (human readable)
- Exports to `logfile.csv` for easy import into Excel
- No dependencies except Python 3 (for building/running)

## Usage
1. Place your `tasks.txt` (one task per line) in the same folder as the executable or script.
2. Run the app:
   - As a script: `python timelogger.py`
   - As an executable: `./timelogger` (after building with PyInstaller)
3. Use number keys to switch tasks, `P` to pause/resume, `Q` to quit and save.

## Build as a Standalone Executable (macOS example)
1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
2. Build:
   ```sh
   pyinstaller --onefile timelogger.py
   ```
3. The executable will be in the `dist/` folder. Place `tasks.txt` there.

## Log Files
- `logfile.txt`: Human-readable daily log
- `logfile.csv`: CSV for Excel import

## Example `tasks.txt`
```
TASK1
TASK2
TASK3
TASK4
```

---

MIT License
