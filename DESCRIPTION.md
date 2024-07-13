# Arbor

## Purpose

Arbor is a simulation library for networks of morphologically detailed neurons.
Such simulations have two main computational "parts":

1. The time stepping of cell state: Cells are represented as trees of line
   segments, on which partial differential equations (PDEs) for potentials are
   solved using the finite-volume method. Furthermore, on each discretised
   location on the tree, state equations for ion channels and synapses are
   solved. This part of the simulation is computationally intensive, taking
   advantage of SIMD vectorization on CPU cores, and SIMT execution on GPUs.
2. Event driven simulation: Cells generate events called spikes, which are
   communicated globally using MPI. Each MPI rank then generates local events to
   be delivered to cells on that rank. Typically each spike will generate in the
   order of 1000 to 10000 deliverable events, which have to be queued. In
   simulations with simple cells (i.e. cells with low computational overheads),
   the memory and network overheads of event delivery can dominate simulations.

The benchmark is designed to test both parts of the workflow. We use a complex
cell loosely based on a model obtained from the Allen Institute's Mouse Brain
Atlas.

_While this description tries to be agnostic with respect to the benchmarking infrastructure, we consider JUBE as our reference and give examples with it._

## Source

Archive Name: `arbor-bench.tar.gz`

The file holds instructions to run the benchmark, according JUBE scripts, and
configuration files to run Arbor. Sources for the benchmark harness and the Arbor
library are distributed in the `src` directory; they include sources of the following versions:

- Arbor: https://github.com/thorstenhater/arbor (c99070b4cef97b683251becfbf7d9e4958d176d6)
  - feature branch that trades setup time for memory
- NSuite: https://github.com/thorstenhater/nsuite (5a9b429f7a32c5dc2ae3ecddbf3c8ca0ae584d46)
  - feature branch to ensure correct workload for this benchmark

## Building

Arbor can be built for GPU usage and for sole CPU usage. The benchmark is
intended for the GPU version only.

Arbor depends on few other packages; it needs a C++17 capable compiler (for
example GCC), a CUDA toolkit (10.1 or later), an MPI installation, and CMake for
installation (CMake 3.18 or later). See also the [Arbor
documentation](https://docs.arbor-sim.org/en/latest/install/build_install.html)

Note: An experimental HIP version exists.

### Modification

- Changing the workload is not within scope.
- Floating point optimisation must not be set to `--ffast-math` or similar.
- The baseline is derived using the `-O3` options.

### JUBE

The JUBE step `compile` takes care of building the benchmark. It configures and builds the benchmark in accordance with the outlined
flags above.

## Execution

Changing the workload is not within scope.

The main executable of this benchmark is `arbor-busyring` (if built through
JUBE, it is located in the `build-busyring/ring-build/` sub-folder). The
parameter file `input.json` needs to exist in the same directory.

### Multi-Threading

Arbor can be run with different numbers of threads, in the JUBE file, the
parameter `threadspertask` is used.

### Benchmark Variants

The Arbor benchmark is to be executed in two variants.

1. **TCO Baseline**: This benchmark is the benchmark for the default evaluation. The simulation incorporates 1536000 cells; see below.
2. **High-Scaling**: This benchmarks uses a significantly larger amount of cells to explore scalability between a 50 PFLOP/s sub-partition of JUWELS Booster and a 1000 PFLOP/s sub-partition of the Exascale system (with 20x the performance). Four sub-variants are prepared, each utilizing different amounts of A100 GPU memory: _large_ (100% memory, 40 GB minus margin), _medium_ (75%, 30 GB minus margin), _small_ (50%, 20 GB minus margin), and _tiny_ (25%, 10 GB minus margin). 

### Command Line

Please call the benchmark with

```
[mpiexec] ./src/arbor/build-busyring/ring-build/arbor-busyring input.json
```

Different `input.json` files are provided in the `benchmark/inputs/` directory depending on the executed variant:

1. **TCO Baseline**: The `benchmark/inputs/baseline.json` file should be taken, containing 1536000 cells
2. **High-Scaling**: One of the `benchmark/inputs/MEM_50pf.json` files should be taken, with `MEM` being either `large`, `medium`, `small`, or `tiny`. They configure Arbor for simulation of 123264000, 92448000, 61632000, and 28248000 cells, respectively.

### JUBE

The JUBE step `execute` calls the aforementioned command line with the correct
modules. It also cares about the MPI distribution by submitting a script to the
batch system. The latter is achieved by populating a batch submission script
template (via `platform.xml`) with information specified in the top of the
script relating to the number of nodes and tasks per node. Via dependencies, the
JUBE step `execute` calls the JUBE step `compile` automatically.

To submit a self-contained benchmark run to the batch system, call `jube run
benchmark/jube/default.yaml [--tag NAME]`. JUBE will generate the necessary
configuration and files, and submit the benchmark to the batch engine.

The following parameters of the JUBE script might need to be adapted:

- `n_gpu`: GPUs/node
- `taskspernode`: must be equal to `n_gpu`
- `ARB_GPU`: what kind of GPU backend to use; `cuda`, `hip`, and `none` (`hip`
  is still considered experimental and might require significant tuning). Should
  not be set to `none` for this benchmark.
- `cc`/`cxx`: C and C++ compilers to use
- `queue`: SLURM queue to use
- `SIMD`: use explicit SIMDisation? Should be on, if supported.
- `arch`: SIMD architecture to use (supported: SSE, AVX, AVX2, Neon)
- `modules`: to be sourced before building and running

After a run, JUBE can also be used to extract the runtime of the program (with
`jube analyse` and `jube result`).

The following JUBE tags are available to launch the benchmark variants

| Variant      | Sub-Variant   | Reference Node Count | Tag           | Memory      |
|--------------|---------------| -------------------- |---------------|-------------|
| TCO Baseline |               | 8                    | `baseline`    |             |
| High-Scaling | Tiny Memory   | 642                  | `high_tiny`   | 25% memory  |
| High-Scaling | Small Memory  | 642                  | `high_small`  | 50% memory  |
| High-Scaling | Medium Memory | 642                  | `high_medium` | 75% memory  |
| High-Scaling | Large Memory  | 642                  | `high_large`  | 100% memory |


Some additional tags exist within the JUBE script to explore different node counts
with a fixed problem size per node ('weak scaling'). These are

- `scaling_base`
- `scaling_tiny`
- `scaling_small`
- `scaling_medium`
- `scaling_large`


## Verification

The application should run through successfully without any exceptions or error
codes generated. An overview table indicating successful operation is generated,
similar to the following:

```
gpu:      yes
threads:  12
mpi:      yes
ranks:    1

cell stats: 64 cells; 652 branches; 7264 compartments;
running simulation

238 spikes generated at rate of 0.840336 ms between spikes

---- meters -------------------------------------------------------------------------------
meter                         time(s)      memory(MB)
-------------------------------------------------------------------------------------------
model-init                      0.122          12.391
model-run                       1.215           0.046
meter-total                     1.337          12.437
```

The benchmark reports its spike count in the `n_spike` column; these must
match those listed below in the `Baseline` and `Large Scale` sections.

## Results

The benchmark prints a runtime for the `model-run` step. This value is the
metric used. 

### JUBE

Using `jube analyse` and a subsequent `jube result` prints an overview table
with the number of nodes, tasks per node, and runtime. The runtime metric is
shown as `t_run`.

Using `jube result -a` prints an overview table
with the number of nodes, tasks per node, and runtime.

## Commitments

### TCO Baseline

The baseline configuration must be chosen such that the runtime metric is less
than or equal to 750s. This value is achieved with 8 nodes using 4 A100 GPUs per
node on the JUWELS Booster system at JSC. JUWELS Booster produces produces the
following output, given `jube run default.yml --tag baseline`

|   cells | ... | ranks | ... |  t_init |   t_run | n_spike |
|---------|-----|-------|-----|---------|---------|---------|
| 1536000 | ... |    32 | ... | 720.519 | 727.294 | 1549882 |

Some fields omitted for brevity.

### High-Scale

High scale runs probe JUWELS Booster at 642 nodes with a workload to fill the
GPU memory of an A100 to 50%, 75%, and 100% respectively (minus a safety
margin). The relevant tags are `high_tiny`, `high_small`, `high_medium`, and `high_large`. We
obtained:

|     config    |   cells   | ... | ranks | ... |  t_init |  t_run  |  n_spike  |
|---------------|-----------|-----|-------|-----|---------|---------|-----------|
| `high_tiny`   |  28248000 | ... |  2568 | ... | 190.358 | 218.159 |  28506848 |
| `high_small`  |  61632000 | ... |  2568 | ... | 375.444 | 380.202 |  62197827 |
| `high_medium` |  92448000 | ... |  2568 | ... | 620.029 | 622.261 |  93296880 |
| `high_large`  | 123264000 | ... |  2568 | ... | 865.833 | 798.192 | 124397393 |

Some fields omitted for brevity.

Note that this benchmark setting is defined for the hardware currently available
to the JSC (642 nodes x 4 A100 GPUs ~ 50 PFLOP/s). In the JUBE file
`benchmark/jube/default.yaml` these cases were scaled to 1000 PFLOP/s compute by
multiplying the cell count by 20x and prepared through tags `exa_large`, 
`exa_medium`, `exa_small`, and `exa_tiny`; static input files for these exa workloads are available in `benchmark/inputs/`, suffixed with `_1ef.json`. Distribute onto as many nodes as needed to
achieve an accumulated 1000 PFLOP/s performance.
