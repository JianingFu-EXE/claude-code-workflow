# TensorBoard Report Generator

Read TensorBoard event files and generate an Obsidian report.

## Arguments
- $ARGUMENTS: experiment name(s) — folder name(s) under `<TB>/`

## Steps

1. **Find event files**: Look in `<TB>/{experiment_name}/` for `events.out.tfevents.*` files.

2. **Read TB data**: Use the DSAC Python env to extract scalar summaries:
   ```
   <PYTHON> -c "
   from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
   ea = EventAccumulator(r'<TB>/{experiment_name}')
   ea.Reload()
   print('Tags:', ea.Tags()['scalars'])
   for tag in ea.Tags()['scalars']:
       events = ea.Scalars(tag)
       vals = [e.value for e in events[-50:]]
       print(f'{tag}: last={vals[-1]:.4f}, mean_last50={sum(vals)/len(vals):.4f}, min={min(vals):.4f}, max={max(vals):.4f}')
   "
   ```

   > Resolve `<PYTHON>` and `<TB>` from the Key Paths table in CLAUDE.md using the current platform.
   > This command is Windows-only (Python/TensorBoard not available on Mac).

3. **Generate report**: Write an Obsidian markdown report to:
   `<FN>/Meta RL for FTC/Meta-IPC/`

   Report should include:
   - Experiment name, date
   - Summary table of all scalar metrics (last value, mean of last 50, min, max)
   - Per-task reward breakdown if available
   - Training diagnostics (Q-loss, policy loss, alpha/beta if present)
   - Key observations and convergence assessment

4. **Use Obsidian markdown format**: wikilinks, callouts, frontmatter properties.
