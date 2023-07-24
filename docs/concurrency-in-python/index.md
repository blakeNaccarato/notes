# Concurrency in Python

Use Python's `asyncio` module to concurrently generate reports from Jupyter notebooks. In this example, we want to process notebooks, for example [this one](example-notebook.ipynb), through a series of stages:

- Clean

## Profile the results

Let's try profiling again. Run `python -m cProfile -o .prof process_nbs.py`. View the profile result with `snakeviz .prof`.

## Scratch

- Look at notebooks, run one for example
- Show an example output HTML and DOCX
- Run it with all notebooks
- Run again and show why logging is important
- Show the kickoff point at the bottom of the script first
- Focus on the main function
- Dive into the first task group, pointing out only the awaits. Back to top level now
- Eventually, delve into implementations
- Use your iPad to sketch some ideas. It's awaits all the way down, until you get to scheduling primitives
- The top is usually fired off by async.run()
- Sketch the current blockered pattern you're using presently, then consider unblocking by bundling serial tasks into a group

```{toctree}
:hidden:
example-notebook
logs
```
