# JUPITER Benchmark Suite: Arbor

This benchmark is part of the [JUPITER Benchmark Suite](https://github.com/FZJ-JSC/jubench). See the repository of the suite for some general remarks.

This repository contains the Arbor benchmark, created by CSCS and JSC. [`DESCRIPTION.md`](DESCRIPTION.md) contains details for compilation, execution, and evaluation.

Sources are included as submodules.

## Quickstart using JUBE

```
# Run the benchmark using JUBE
jube run benchmark/jube/default.yaml --tag baseline
jube result -a benchmark/jube/run --id XYZ
```

This will perform a full build and
run the benchmark afterwards. On JUWELS Booster `jube run default.yml --tag
baseline` produces the following output

|   cells | ... | ranks | ... |  t_init |   t_run | n_spike |
|---------|-----|-------|-----|---------|---------|---------|
| 1536000 | ... |    32 | ... | 720.519 | 727.294 | 1549882 |

Some fields omitted for brevity.

Potentially, a platform configuration file (`platform.xml`) for JUBE is needed.

For a more detailed description, see `DESCRIPTION.md`.

## Without JUBE

You will need to build the required software modules in `src/arbor` and
`src/nsuite` such that the `busying` benchmark in `nsuite` links against
`libarbor.a` from `src/arbor`. Refer to the JUBE script on how this is done.
Then, generate the input files for the benchmark using `benchmark/gen-inputs.py
--default` and run `busyring` passing one of the resulting JSON files.

We provide static input files in `benchmark/inputs` for 50 PF and 1 EF, as well
as the baseline. See the JUBE script `benchmark/jube/default.yaml` and
`DESCRIPTION.md` for more details.
