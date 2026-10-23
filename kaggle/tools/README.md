# kaggle/tools

| File | Use |
|---|---|
| `run_local_steps.ps1` | the desktop steps, in one go: check the selection, copy + SHA-256-verify the 400 videos, `verify_split.py`, all tests, one local commit (**no push**), build + re-check the upload zip. Run: `powershell -ExecutionPolicy Bypass -File D:\sign_avatar_cse498r\kaggle\tools\run_local_steps.ps1` |
| `commit_message.txt` | the message of that commit |
| `build_notebooks.py` | regenerates `../notebooks/*.ipynb` (without outputs) |
