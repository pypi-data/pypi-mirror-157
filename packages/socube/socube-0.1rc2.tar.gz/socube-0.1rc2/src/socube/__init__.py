# MIT License
#
# Copyright (c) 2022 Zhang.H.N
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = "0.1rc2"
__author__ = "Zhang.H.N"
__email__ = "zhang.h.n@foxmail.com"
__url__ = "https://github/idrblab/socube/"


def main(*args: str):
    from argparse import ArgumentParser
    parser = ArgumentParser("SoCube")

    parser.add_argument("--version",
                        "-v",
                        action="store_true",
                        help="Print socube version info")
    basic_args = parser.add_argument_group("basic configuration")
    basic_args.add_argument("--input",
                            "-i",
                            type=str,
                            default=None,
                            help='''
                        UMI expression matrix for scRNA-seq, supporting h5 format
                        (pandas DataFrame) and h5ad format (implemented in python
                        package anndata). The rows of the data are cells and the columns
                        are genes, please make sure that the cell ID is unique.
                        ''')
    basic_args.add_argument("--output",
                            "-o",
                            default=None,
                            type=str,
                            help='''
                        The output directory of the processed intermediate files and the
                        final result, if not specified, the default is the same directory as the
                        input file, if the output directory does not exist, a new one will be
                        created, if it already exists, continue to use the existing directory.
                        There are subdirectories embedding for socube embedding features,
                        models, plots and outputs for models, graphs and results generated
                        by model training. The final results are in the outputs subdirectory.
                        ''')
    basic_args.add_argument("--gpu-ids",
                            type=str,
                            default=None,
                            help='''
                        Ids of GPUs for accelerated computing, such as "0,1,2,3"
                        ''')
    basic_args.add_argument("--seed",
                            type=int,
                            default=None,
                            help="Random seed to reproduce, default is not specific")
    basic_args.add_argument("--k",
                            type=int,
                            default=5,
                            help='''
                        The k-fold cross-validation is used in training, and the resulting k models
                        will be ensembled into one model. Default 5.
                        ''')
    basic_args.add_argument("--adj-factor",
                            type=float,
                            default=1.0,
                            help='''
                        The adjustment factor for the doublet expression level. By default it is
                        assumed that the doublet expression level is twice the sinlget, but there
                        are fluctuations in the real situation and the expression level can be
                        changed by adjusting this factor. Default 1.0.
                        ''')
    basic_args.add_argument("--dim",
                            "-d",
                            type=int,
                            default=10,
                            help='''
                        The target dimension for gene degradation is also the number of
                        channels to train the model. Default 10.
                        ''')
    basic_args.add_argument("--cube-id",
                            type=str,
                            default=None,
                            help='''
                        If you want to reuse the socube embedding features obtained earlier,  just
                        specify the embedding ID, which is a string like \"yyyymmdd-HHMMSS-xxx\",
                        along with the original output path.
                        ''')

    model_args = parser.add_argument_group("model training configuration")
    model_args.add_argument("--learning-rate",
                            "-lr",
                            type=float,
                            default=0.001,
                            help="Learning rate of model training. Default 1e-3.")
    model_args.add_argument("--epochs",
                            "-e",
                            type=int,
                            default=100,
                            help="Epochs of model training. Default 100")
    model_args.add_argument("--train-batch-size",
                            type=int,
                            default=64,
                            help="Batch size of model training. Default 64.")
    model_args.add_argument("--vaild-batch-size",
                            type=int,
                            default=512,
                            help="Batch size of model validating. Default 512.")
    model_args.add_argument("--infer-batch-size",
                            type=int,
                            default=400,
                            help="Batch size of model inferring. Default 400.")
    model_args.add_argument("--threshold",
                            "-t",
                            type=float,
                            default=0.5,
                            help='''
                            The classification threshold for doublet detection. The
                            model outputs the probability score of doublet, which
                            is greater than the threshold considered as doublet and
                            vice versa for singlet. user can customize the threshold value.
                            Default 0.5.
                        ''')
    model_args.add_argument("--enable-validation",
                            "-ev",
                            action="store_true",
                            help='''
                        This optional is provided for performance evaluation.
                        You should input h5ad format data, and store label in
                        its `obs` property. `obs` property is a `DataFrame` object
                        and its label column named "type" and value is "doublet"
                        and "singlet".
                        ''')
    model_args.add_argument("--enable-multiprocess",
                            "-mp",
                            action="store_true",
                            help='''
                            Enable multi process to make use of CPU's multiple cores.
                            ''')

    notice_args = parser.add_argument_group("notice configuration")
    notice_args.add_argument(
        "--mail",
        type=str,
        default=None,
        help="Email address to send and receive the notification.")
    notice_args.add_argument(
        "--mail-server",
        type=str,
        default=None,
        help="Email server address. such as smtp.gmail.com")
    notice_args.add_argument("--mail-port",
                             type=int,
                             default=465,
                             help="Email server port, such as 994 for SSL.")
    notice_args.add_argument("--mail-passwd",
                             type=str,
                             default=None,
                             help="Email account password")
    notice_args.add_argument("--enable-ssl",
                             action="store_true",
                             help="Enable SSL for mail service")
    args = parser.parse_args(args if args else None)

    if args.version:
        print("Release v{:s}, Copyright (c) 2022 {:s}".format(
            __version__, __author__))
        return

    if args.input is None and args.cube_id is None:
        parser.print_help()
        return

    # Avoid import libraries at head
    from socube.utils.logging import getJobId, log
    log("Config", "Load required modules")
    import shutil
    import numpy as np
    import scanpy as sc
    import pandas as pd
    import torch

    from concurrent.futures import Future
    from socube.task.doublet import (createTrainData, checkData)
    from socube.data.preprocess import minmax, std
    from socube.utils.exception import ExceptionManager
    from socube.utils.mail import MailService
    from socube.utils.memory import parseGPUs
    from socube.cube import SoCube
    from socube.utils.io import mkDirs, writeCsv, writeHdf, checkExist
    from socube.utils.concurrence import ParallelManager
    from socube.data import filterData
    from socube.task.doublet import fit, infer, checkShape
    from os.path import dirname, join
    from scipy.sparse import issparse

    pd.options.mode.use_inf_as_na = True

    if None not in [
            args.mail, args.mail_server, args.mail_port, args.mail_passwd
    ]:
        log("Config", "Mail service inited for notification")
        mail_service = MailService(sender=args.mail,
                                   passwd=args.mail_passwd,
                                   server=args.mail_server,
                                   port=args.mail_port,
                                   ssl=args.enable_ssl)
    else:
        mail_service = None

    with ExceptionManager(mail_service=mail_service) as em:
        data_path = dirname(args.input) if args.input else "."
        home_path = args.output if args.output is not None else data_path
        cube_id = args.cube_id if args.cube_id else getJobId()
        embedding_path = join(home_path, "embedding", cube_id)
        train_path = join(embedding_path, "traindata")
        my_cube = SoCube.instance(map_type="pca",
                                  data_path=data_path,
                                  home_path=home_path)
        gpu_ids = None
        if torch.cuda.is_available():
            if args.gpu_ids is None:
                log("Config", "Use CPU for training, but GPU is available, specify '--gpu-ids' to use GPU")
            else:
                gpu_ids = parseGPUs(args.gpu_ids)
        else:
            if args.gpu_ids is not None:
                log("Config", "GPU is not available, use CPU for training and ignore '--gpu-ids' setting")

        # If cube id is specified, skip to repeat embedding fit
        if args.cube_id is None or not my_cube.load(embedding_path):
            with ParallelManager():
                if args.input is None:
                    log("Config", "No input file specified")
                    return

                checkExist(args.input)
                mkDirs(embedding_path)

                log("Preprocess", "Load data")
                label = None
                if args.input.endswith(".h5"):
                    samples = pd.read_hdf(args.input)

                elif args.input.endswith(".h5ad"):
                    samples = sc.read_h5ad(args.input)
                    if "type" in samples.obs:
                        label = (
                            samples.obs["type"] == "doublet").astype("int8")

                    samples = pd.DataFrame(samples.X.toarray() if issparse(
                        samples.X) else samples.X,
                                           index=samples.obs_names,
                                           columns=samples.var_names)

                else:
                    raise NotImplementedError("Unsupport file format")

                # if real label not specific, disable validation
                if label is None:
                    label = pd.Series(np.zeros_like(samples.index,
                                                    dtype="int8"),
                                      index=samples.index,
                                      name="type")
                    if args.enable_validation:
                        log(
                            "Config",
                            "Disable '--enable-validation' because no real label found"
                        )
                        args.enable_validation = False

                label.to_csv(join(embedding_path, "ExperimentLabel.csv"),
                             header=None)

                checkData(samples)
                future: Future = createTrainData(samples,
                                                 output_path=embedding_path,
                                                 adj=args.adj_factor,
                                                 seed=args.seed)

                samples = samples.T
                writeHdf(
                    samples,
                    join(
                        embedding_path,
                        f"00-dataByGene[{samples.dtypes.iloc[0].name}][raw].h5"
                    ))

                log("Pre-processing", "Filter data")
                samples = filterData(samples)
                writeHdf(
                    samples,
                    join(
                        embedding_path,
                        "01-dataByGene[{:s}][filter].h5".format(
                            samples.dtypes.iloc[0].name)))

                my_cube.fit(samples,
                            device=gpu_ids[0] if isinstance(gpu_ids, list) and len(gpu_ids)>0 else "cpu",
                            seed=args.seed,
                            latent_dim=args.dim,
                            job_id=cube_id)

            train_data, train_label = future.result()
            log("Post-processing",
                "Processing data with log, std and feature minmax")
            train_data = minmax(std(np.log(train_data + 1)))
            log("Post-processing", "Single channels data is tranforming")

            my_cube.batchTransform(train_data, train_path)
            writeCsv(train_label,
                     join(train_path, "TrainLabel.csv"),
                     header=None)
            if checkExist(join(embedding_path, "ExperimentLabel.csv"),
                          raise_error=False):
                shutil.copyfile(join(embedding_path, "ExperimentLabel.csv"),
                                join(train_path, "ExperimentLabel.csv"))

        elif args.input is not None:
            log("Config", "input is ignored because cube id is specified")

        log("Train", "Data check before training start")
        dim = my_cube._config["latent_dim"]
        checkExist(join(train_path, "TrainLabel.csv"))
        checkShape(train_path, shape=(args.dim, None, None))
        log("Train", f"Data check passed, data path {train_path}")
        model_id = fit(
            home_dir=home_path,
            data_dir=train_path,
            lr=args.learning_rate,
            gamma=0.99,
            epochs=args.epochs,
            train_batch=args.train_batch_size,
            valid_batch=args.vaild_batch_size,
            in_channels=dim,
            transform=None,
            shuffle=True,
            gpu_ids=gpu_ids,
            seed=args.seed,
            label_file="TrainLabel.csv",
            threshold=args.threshold,
            k=args.k,
            once=False,
            use_index=False,
            step=5,
            max_acc_limit=1,
            multi_process=args.enable_multiprocess)

        log("Inference", "Begin doublet detection output")
        infer(data_dir=train_path,
              home_dir=home_path,
              model_id=model_id,
              label_file="ExperimentLabel.csv",
              in_channels=dim,
              k=args.k,
              threshold=args.threshold,
              batch_size=args.infer_batch_size,
              gpu_ids=gpu_ids,
              with_eval=args.enable_validation,
              seed=args.seed,
              multi_process=args.enable_multiprocess)

        em.setNormalInfo("Doublet detection finished")
