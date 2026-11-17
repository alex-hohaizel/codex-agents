"""Keep the first worker live at a known checkpoint until the harness interrupts it."""
import time
print("WORKTREE_CHECKPOINT_WAITING", flush=True)
time.sleep(60)
