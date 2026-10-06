# turbid-mc

Monte Carlo photon transport for the milk-phantom lab. A He–Ne beam
(632.8 nm) crosses a tank of milk. Part A measures $\mu_s$, $\mu_s'$, and
$g$ with no object in the tank. Part B asks whether a Monte Carlo run that
uses only those numbers predicts the shadow of an opaque rod.

The physics functions are stubs. They document units and raise
`NotImplementedError`. Config loading, result files, and the command-line
scripts are wired up.

## Units

Lengths are millimetres. Optical coefficients ($\mu_a$, $\mu_s$, $\mu_s'$)
are mm$^{-1}$. Angles stored as angles are radians; the Henyey–Greenstein
sampler returns $\cos\theta$. Weights, refractive indices, and $g$ are
dimensionless. Speckle exposures are milliseconds. Viscosity in the
Stokes–Einstein helper stays in pascal-seconds, and that function returns
the radius in millimetres.

The tank has $z = 0$ at the entry face and $z = L$ at the exit face. $x$
runs across the width, from $-W/2$ to $W/2$, and $y$ runs from $-H/2$ to
$H/2$. The rod is an infinite cylinder along $y$.

## How the pieces fit together

The repository is a library under `src/turbid/`, thin command-line scripts, and folders for inputs and outputs. The scripts do not contain the physics. Each one loads a file, calls one library function, and writes the result somewhere other than `data/raw`.

A simulation starts as a YAML file in `configs/`. `scripts/run_mc.py` reads it with `src/turbid/io/config.py`, which checks units and that $g$ agrees with $\mu_s'$ when both are set. It then calls `src/turbid/mc/run.py`. That function is the only place a full run is assembled. It splits the photons into batches, and each batch goes through the rest of `mc/`:

- `sources.py` places the packets on the entry face, either all at one point (pencil beam) or uniformly over a rectangle (wide beam).
- `transport.py` walks each packet. For every step it asks `geometry.py` whether the tank wall or the rod is closer, asks `phase.py` for a Henyey–Greenstein deflection, and applies Fresnel reflection and Russian roulette itself.
- `detectors.py` keeps the packets that leave the exit face inside the camera's acceptance angle, and bins them into a radial profile $I(\rho)$ and a lateral profile $I(x)$.

`run.py` turns the batch-to-batch scatter into the error bars. `io/results.py` writes `runs/<name>/` with `results.npz`, a copy of the config, and `seed.txt`. `runs/` is gitignored.

`run_simulation` currently stops after the config check. The other `mc/` modules are the pieces it will call once they are filled in.

```text
configs/example.yaml
        │
        ▼
scripts/run_mc.py ──► io/config.py ──► mc/run.py
                                          │
                    sources.py ◄──────────┤
                    transport.py ◄────────┤──► phase.py
                         │                └──► geometry.py
                         ▼
                    detectors.py
                         │
                         ▼
                    io/results.py ──► runs/
```

Camera frames go in `data/raw/` and stay there. `io/results.py` refuses to write on that path. `data/lab_log.csv` is the index: one row per dataset, pointing at the raw filename.

`scripts/process_scan.py` reads a frame through `analysis/profiles.py` and writes a 1D profile to `data/processed/`. `analysis/metrics.py` turns that profile into shadow contrast and edge-blur width. `analysis/fitting.py` compares it with a simulated profile using $\chi^2$.

Two scripts are that comparison, repeated:

- `scripts/fit_exit_spread.py` is Part A2. It reruns the Monte Carlo over a grid of $\mu_s'$ until the simulated exit-face spot matches the measured radial profile.
- `scripts/build_lookup.py` is the depth inversion. `analysis/lookup.py` runs the rod at many depths and diameters, stores the normalised profiles, and later picks the depth whose profile best matches a measurement.

`optics/mie.py` turns a measured $g$ into an effective particle radius. `optics/speckle.py` fits speckle contrast against exposure time and converts the decorrelation time into a hydrodynamic radius. Neither one is called by the Monte Carlo. They answer the two stretch questions about particle size.

`tests/` builds config dicts in code and calls `run_simulation` directly, with no YAML file and no camera. The six physics tests are the plan's pass conditions. The config and result-file tests already pass.

`notebooks/` is for poking at a single run. `figures/` and `report/` are the write-up. An analysis the report depends on should end up as a script or a function under `src/turbid/`, so it can be rerun from the raw data and the saved configs.

## Layout

```text
src/turbid/mc/         photon transport (phase, geometry, sources, detectors, transport, run)
src/turbid/optics/     Mie g(r) and speckle contrast
src/turbid/analysis/   image profiles, shadow metrics, chi-squared fits, lookup table
src/turbid/io/         YAML configs and result files
configs/               example simulation YAML
data/raw/              camera frames; gitignored; never overwritten
data/processed/        profiles derived from raw frames
data/lab_log.csv       one row per dataset
runs/                  simulation outputs; gitignored
scripts/               run_mc.py, build_lookup.py, process_scan.py, fit_exit_spread.py
notebooks/             exploration
figures/               report figures
report/                LaTeX write-up
tests/                 validation tests from the project plan
```

## Setup

Python 3.11. From the repository root:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

`pmcx` is an optional extra for a later cross-check against an independent
Monte Carlo code. It is not imported by this package.

```powershell
python -m pip install -e ".[dev,pmcx]"
```

## Tests

```powershell
pytest
```

`tests/test_config.py` and `tests/test_results_io.py` pass now. The six
physics tests call `run_simulation` and raise `NotImplementedError` until
the photon loop is written:

| Test | Pass condition |
| --- | --- |
| `test_absorber.py` | $\mu_s = 0$ transmission equals $\exp(-\mu_a L)$ |
| `test_ballistic.py` | unscattered exit weight equals $\exp(-\mu_t L)$ |
| `test_energy.py` | transmitted + reflected + side escape + absorbed + object $= 1$ |
| `test_similarity.py` | $g = 0$ and $g = 0.9$ agree at equal $\mu_s'$, with $L/l^* \ge 10$ |
| `test_convergence.py` | doubling the photon count shifts transmission by less than three standard errors |
| `test_shadow.py` | clear tank, wide beam: dark strip of width $2a$ |

A practical order is the free-path sampler and Henyey–Greenstein draw
first (their means are $1/\mu_t$ and $g$), then Fresnel and the batch
loop, then `run_simulation`. Make the absorber and ballistic tests pass
before adding the rod.

## Run a simulation

```powershell
python scripts/run_mc.py configs/example.yaml
```

That checks the example config, then raises `NotImplementedError` from
`run_simulation`. When the loop exists, the same command writes
`runs/example_seed1/` containing `results.npz`, a copy of the config, and
`seed.txt`.

Other entry points, also waiting on the stubs they call:

```powershell
python scripts/build_lookup.py configs/example.yaml --depths-mm 10 20 30 --diameters-mm 4 --output runs/lookup.npz
python scripts/process_scan.py data/raw/frame.tif --pixel-size-mm 0.01
python scripts/fit_exit_spread.py configs/example.yaml profile.csv --mu-s-prime 0.04 0.05 0.06 --normalise-at-mm 2 --output runs/spread
```

`process_scan.py` reads raw frames and writes `data/processed`. It will
not write into `data/raw`.

## Lab log

`data/lab_log.csv` has one header row:

`date, sample, concentration, rod_depth, mode, exposure_ms, temperature_C, filename, notes`

Append a line for each dataset. Leave the file named in `filename` untouched
under `data/raw`.
