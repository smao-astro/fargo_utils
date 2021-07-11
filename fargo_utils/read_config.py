import csv


def read_config(filepath, delimiter) -> list:
    """Read configuration information from local file.

    Examples:

        read `variables.par`:

        .. code-block:: python

             read_config(variables_path, "\t")

        read `config_local.csv`:

        .. code-block:: python

             read_config(config_local_path, delimiter=" ")

        The format of the file is:

        .. code-block:: bash

            num_epochs 15000
            redraw_every 1000
            train_distribution pseudo
            exact_ICBC
            num_neurons 128
            lr 1e-05
            decay_rate 0.0
            save_dir /project/6004694/symao/pinn/disk2D/job/2020-05-30_13-17-14/training/hp-15/1021_170538_724399


    Args:
        filepath (str):
        delimiter (str):

    Returns:
        list: local configuration arguments.

        Examples:
            ['--num_epochs', '15000',
             '--redraw_every', '1000',
             '--train_distribution', 'pseudo',
             '--exact_ICBC',
             '--num_neurons', '128',
             '--lr', '1e-05',
             '--decay_rate', '0.0',
             '--save_dir', '/project/6004694/symao/pinn/disk2D/job/2020-05-30_13-17-14/training/hp-15
             /1021_170538_724399']

    """
    with open(filepath, "r", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        words = [
            word
            for line in reader
            for word in ["--" + line[0]] + line[1:]
            if len(word) > 0
        ]
    return words
