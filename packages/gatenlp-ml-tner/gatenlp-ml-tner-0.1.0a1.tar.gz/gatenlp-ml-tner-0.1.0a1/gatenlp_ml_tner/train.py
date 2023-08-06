"""
Module for finetuning transformer models with data exported from GateNLP.
"""
from typing import Optional, Union, List
import os
from typing import Optional
import argparse
import logging
import tner
from gatenlp.utils import init_logger


class TokenClassificationTrainer:
    """
    Train a Tner chunking classifier model.
    """
    def __init__(
            self,
            datadir: Optional[str],
            outdir: str = "./tner_tokenclassification_model",
            transformers_model: str = "dslim/bert-base-NER",
            seed: int = 42,
            learning_rate = 2e-5,
            train_size: float = 0.9,
            eval_size: Optional[float] = None,
            max_steps: int = 5000,
            warmup_steps: int = 700,
            weight_decay: float = 1e-7,
            batch_size: int = 16,
            max_seq_length: int = 128,
            fp16: bool = False,
            max_grad_norm: float = 1.0,
            lower_case: bool = False,
            num_worker: int = 0,
            cache_dir: Optional[str] = None,
    ):
        assert os.path.isdir(datadir)
        assert os.path.isdir(outdir)
        self.seed = seed
        if eval_size is None:
            eval_size = 1.0 - train_size
        self.eval_size = eval_size
        self.learning_rate = learning_rate
        self.datadir = datadir
        self.outdir = outdir
        self.max_seq_length = max_seq_length
        self.train_size = train_size
        self.eval_size = eval_size
        self.max_steps = max_steps
        self.warmup_steps = warmup_steps
        self.weight_decay = weight_decay
        self.batch_size = batch_size
        self.fp16 = fp16
        self.max_grad_norm = max_grad_norm
        self.lower_case = lower_case
        self.num_worker = num_worker
        self.cache_dir = cache_dir
        self.trainer = tner.TrainTransformersNER(
            checkpoint_dir=self.outdir,
            dataset=os.path.join(self.datadir),
            transformers_model=transformers_model,
            random_seed=seed,
            lr=learning_rate,
            total_step=max_steps,
            warmup_step=warmup_steps,
            weight_decay=weight_decay,
            batch_size=batch_size,
            max_seq_length=max_seq_length,
            fp16=fp16,
            max_grad_norm=max_grad_norm,
            lower_case=lower_case,
            num_worker=num_worker,
            cache_dir=cache_dir
        )

    def train(self):
        self.trainer.train(
            monitor_validation=True,
            max_seq_length_validation=self.max_seq_length)


def build_argparser():
    argparser = argparse.ArgumentParser(
        description="Train a Tner chunking classification model."
    )
    argparser.add_argument("datadir", type=str,
                           help="Directory containint the data.conll file"
                           )
    argparser.add_argument("outdir", type=str,
                           help="Directory where the model is being stored. Gets created if it does not exist.")
    argparser.add_argument("--transformers_model", type=str, default="dslim/bert-base-NER",
                           help="Name or location of a pretrained transformers model to use (dslim/bert-base-NER)")
    argparser.add_argument("--seed", type=int, default=42,
                           help="Random seed to use (42)")
    argparser.add_argument("--learning_rate", type=float, default=2e-5,
                           help="Learning rate (2e-5)")
    argparser.add_argument("--train_size", type=float, default=0.9,
                           help="Portion of data to use for the training set (0.9)")
    argparser.add_argument("--eval_size", type=float, default=None,
                           help="Portion of data to use for the eval set (1.0 - train_size)")
    argparser.add_argument("--max_steps", type=int, default=5000,
                           help="Number of training steps (5000)")
    argparser.add_argument("--warmup_steps", type=int, default=700,
                           help="Number of warmup steps for linear warmup (700)")
    argparser.add_argument("--weight_decay", type=float, default=1e-7,
                           help="Weight decay (1e-7)")
    argparser.add_argument("--batch_size", type=int, default=16,
                           help="Batch size (16)")
    argparser.add_argument("--max_seq_length", type=int, default=128,
                           help="Maximum length of model input sequence (transformer tokens plus special codes) (128)")
    argparser.add_argument("--fp16", action="store_true",
                           help="Use FP16")
    argparser.add_argument("--max_grad_norm", type=float, default=1.0,
                           help="Maximum gradient norm (1.0)")
    argparser.add_argument("--lower_case", action="store_true",
                           help="Convert to lower case first (False)")
    argparser.add_argument("--num_worker", type=int, default=0,
                           help="Number of workers to use (0=determine)")
    argparser.add_argument("--cache_dir", type=str, default=None,
                           help="Cache directory to use for transformers (None)")
    argparser.add_argument("--debug", action="store_true",
                           help="Enable debugging mode/logging")
    return argparser


def parse_args():
    parser = build_argparser()
    args = parser.parse_args()
    return args


def run_training():
    args = parse_args()
    if args.debug:
        logger = init_logger(lvl=logging.DEBUG)
    else:
        logger = init_logger()
    kwargs = vars(args)
    del kwargs["debug"]
    trainer = TokenClassificationTrainer(**kwargs)
    logger.info(f"Initialized trainer, running training ... ")
    trainer.train()
    logger.info("Training finished")


if __name__ == "__name__":
    run_training()