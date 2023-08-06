A library which provides implementations of the kernel of the Alchemical Integral Transform (AIT) in 1D, 2D, 3D.

PyAlchemy uses [Hartree atomic units](https://en.wikipedia.org/wiki/Hartree_atomic_units).

Instead of calculating electronic energies of systems one at a time, this kernel provides a shortcut. By using an initial system's electron density, one can calculate the energy difference to any other system within the radius of convergence of AIT. A complete explanation and introduction of the concept can be found under https://arxiv.org/abs/2203.13794 .

For tricks like manipulation of convergence behavior and examples, check out my [GitHub page](https://github.com/SimonLeonKrug/pyalchemy) and the corresponding [examples](https://github.com/SimonLeonKrug/pyalchemy/tree/main/examples).
