# D3M libraries
from d3m import container
from d3m.base import utils as base_utils
from d3m.metadata import base as metadata_base, hyperparams as hyperparams, params
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from typing import List, Sequence, Tuple, Any
from d3m.primitive_interfaces.base import CallResult

# Huggingface transformer libraries
from datasets import load_dataset
from dataclasses import dataclass, field
from typing import Optional
from transformers.trainer_utils import get_last_checkpoint

from transformers import (
    TrainingArguments,
    AutoConfig,
    AutoModelForSequenceClassification,
    EvalPrediction,
    AutoTokenizer,
    Trainer,
    default_data_collator,
    DataCollatorWithPadding,
)

# SRI's Primitive config imports:
from sri.common import config
from sri.common import constants as con

# Miscellaneous imports
import pandas as pd
from collections import OrderedDict
import numpy as np


__all__ = ('DistilBertTextClassification',)

Inputs = container.DataFrame
Outputs = container.DataFrame


class Params(params.Params):
    trainer_: Optional[Trainer]
    input_column_names: Optional[pd.core.indexes.base.Index]
    target_names_: Optional[Sequence[Any]]
    training_indices_: Optional[Sequence[int]]
    target_column_indices_: Optional[Sequence[int]]
    target_columns_metadata_: Optional[List[OrderedDict]]


class Hyperparams(hyperparams.Hyperparams):
    # hyperparams for dist bert text classification
    valid_pct = hyperparams.Uniform(
        lower=0,
        upper=1,
        default=0.2,
        description='The Validation Split Percentage',
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/TuningParameter'
            ],
    )
    num_workers = hyperparams.Bounded[int](
        lower=0,
        upper=None,
        default=0,
        description='Number of subprocesses to use for data loading',
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ResourcesUseParameter',
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    bs = hyperparams.Bounded[int](
        lower=1,
        upper=None,
        default=5,
        description='Batch Size',
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/TuningParameter',
        ],
    )
    model = hyperparams.Enumeration[str](
        # Should probably filter the problem type and switch model based on what the problem type is. The default
        # distil bert model is for text classification - we would need to use something else for question answering for
        # example.
        values=['distilbert-base-cased', 'distilbert-base-uncased'],
        default='distilbert-base-cased',
        description="Pre-trained model to be used",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    metrics = hyperparams.Enumeration[str](
        values=['accuracy', 'f1score_micro', 'f1score_macro', 'f1score'],
        default='accuracy',
        description="Metrics to be used for evaluation",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    epochs = hyperparams.Bounded[int](
        lower=1,
        upper=None,
        default=5,
        description="Number of epochs",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/TuningParameter',
        ],
    )
    pretrained = hyperparams.UniformBool(
        default=True,
        description='Pretrain the model',
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    norm = hyperparams.UniformBool(
        default=True,
        description="Normalization",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    # TODO: This will probably need to be changed to something suitable to DB
    loss_fn = hyperparams.Enumeration[str](
        values=[
            'CrossEntropyLossFlat', 'BCEWithLogitsLossFlat',
            'LabelSmoothingCrossEntropy', 'LabelSmoothingCrossEntropyFlat'
        ],
        default='CrossEntropyLossFlat',
        description="Loss Function",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    # TODO: This will probably need to be changed to something suitable to DB
    opt_fn = hyperparams.Enumeration[str](
        values=['Adam', 'RMSProp'],
        default='Adam',
        description="Optimization Function",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    use_inputs_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        description="A set of inputs column indices to force primitive to operate on. If any specified column cannot be used, it is skipped.",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ]
    )
    exclude_inputs_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        description="A set of inputs column indices to not operate on. Applicable only if \"use_columns\" is not provided.",
        semantic_types=[
            'https://metadata.datadrivendiscovery.org/types/ControlParameter'
        ],
    )
    use_outputs_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of outputs column indices to force primitive to operate on.",
    )
    exclude_outputs_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of outputs column indices to not operate on. Applicable only if \"use_columns\" is not provided.",
    )
    return_result = hyperparams.Enumeration(
        values=['append', 'replace', 'new'],
        # Default value depends on the nature of the primitive.
        default='append',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Defines if result columns should append or replace original columns",
    )
    use_semantic_types = hyperparams.UniformBool(
        default=False,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Controls whether semantic_types metadata will be used for filtering columns in input dataframe.",
    )
    add_index_columns = hyperparams.UniformBool(
        default=False,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Also include primary index columns if input data has them. Applicable only if \"return_result\" is set to \"new\".",
    )
    error_on_no_input = hyperparams.UniformBool(
        default=True,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Throw an exception if no input column is selected/provided.",
    )
    return_semantic_type = hyperparams.Enumeration[str](
        values=[
            'https://metadata.datadrivendiscovery.org/types/Attribute',
            'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute',
            'https://metadata.datadrivendiscovery.org/types/PredictedTarget'
        ],
        default='https://metadata.datadrivendiscovery.org/types/PredictedTarget',
        description='Decides what semantic type to attach to generated output',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )


@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune from.
    """
    model_name_or_path: str = field(
        # Should probably filter the problem type and switch model based on what the problem type is. The default
        # distil bert model is for text classification - we would need to use something else for question answering for
        # example.
        default='distilbert-base-cased', metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    config_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained config name or path if not the same as model_name"}
    )
    tokenizer_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained tokenizer name or path if not the same as model_name"}
    )
    cache_dir: Optional[str] = field(
        default=None,
        metadata={"help": "Where do you want to store the pretrained models downloaded from huggingface.co"},
    )
    use_fast_tokenizer: bool = field(
        default=True,
        metadata={"help": "Whether to use one of the fast tokenizer (backed by the tokenizers library) or not."},
    )
    model_revision: str = field(
        default="main",
        metadata={"help": "The specific model version to use (can be a branch name, tag name or commit id)."},
    )
    use_auth_token: bool = field(
        default=False,
        metadata={
            "help": "Will use the token generated when running `transformers-cli login` (necessary to use this script "
            "with private models)."
        },
    )


@dataclass
class DataTrainingArguments:
    """
    Arguments pertaining to what data we are going to input our model for training and eval.
    """
    max_eval_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes or quicker training, truncate the number of evaluation examples to this "
            "value if set."
        },
    )
    task_name: Optional[str] = field(
        default=None,
        metadata={"help": "The name of the task to train on. Not used in this context."},
    )
    max_seq_length: int = field(
        default=128,
        metadata={
            "help": "The maximum total input sequence length after tokenization. Sequences longer "
            "than this will be truncated, sequences shorter will be padded."
        },
    )
    overwrite_cache: bool = field(
        default=False, metadata={"help": "Overwrite the cached preprocessed datasets or not."}
    )
    pad_to_max_length: bool = field(
        default=True,
        metadata={
            "help": "Whether to pad all samples to `max_seq_length`. "
            "If False, will pad the samples dynamically when batching to the maximum length in the batch."
        },
    )
    max_train_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes or quicker training, truncate the number of training examples to this "
            "value if set."
        },
    )
    max_val_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes or quicker training, truncate the number of validation examples to this "
            "value if set."
        },
    )
    max_test_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": "For debugging purposes or quicker training, truncate the number of test examples to this "
            "value if set."
        },
    )
    train_file: Optional[str] = field(
        default=None, metadata={"help": "A csv or a json file containing the training data."}
    )
    validation_file: Optional[str] = field(
        default=None, metadata={"help": "A csv or a json file containing the validation data."}
    )
    test_file: Optional[str] = field(default=None, metadata={"help": "A csv or a json file containing the test data."})


class DistilBertTextClassification(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """
    A Wrapper for Distil Bert Text Classification using pretrained models. It uses semantic types to determine which
    columns to operate on.
    """
    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': '58d6d30b-877b-4404-98f0-54aa871f3287',
            'version': config.VERSION,
            'name': "Distil Bert Text Classification Wrapper",
            'description': "Uses pretrained models from HuggingFace DistilBert for text classification problems",
            'python_path': 'd3m.primitives.classification.bert_classifier.DistilBertTextClassification',
            'keywords': ['Classification', 'Text', 'Transformer', 'DistilBert', 'Pretrained', 'HuggingFace'],
            'source': config.SOURCE,
            'installation':  [ config.INSTALLATION ],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.BERT,
            ],
            'primitive_family': metadata_base.PrimitiveFamily.CLASSIFICATION,
            'hyperparams_to_tune': [
                'valid_pct',
                'bs',
                'epochs',
            ]
        }
    )

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, _verbose: int = 0, temporary_directory: str = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, temporary_directory = temporary_directory)
        self._verbose = _verbose
        self._inputs: container.DataFrame
        self._outputs: container.DataFrame
        self._training_indices: List[int] = []
        self._training_inputs: container.DataFrame
        self._training_outputs: container.DataFrame
        self._is_fit = False
        self._target_columns_metadata: List[OrderedDict[Any, Any]] = []
        self._target_column_indices: List[Any]
        self._input_column_names = None
        self._target_names: List[Any]
        self.random_seed = random_seed
        self.temporary_directory = temporary_directory


    def set_training_data(self, *, inputs: container.DataFrame, outputs: container.DataFrame) -> None:
        self._inputs = inputs
        self._outputs = outputs
        self._is_fit = False
        self._new_training_data = True


    def fit(self, *, timeout: float = None, iterations: int = None) -> CallResult[None]:
        if self._inputs is None or self._outputs is None:
            raise ValueError("Missing training data.")
        if not self._new_training_data:
            return CallResult(None)
        self._new_training_data = False
        self._training_inputs, self._training_indices = self._get_columns_to_fit(self._inputs, self.hyperparams)
        self._training_outputs, self._target_names, self._target_column_indices = self._get_targets(self._outputs,
                                                                                                    self.hyperparams)
        self._input_column_names = self._training_inputs.columns.astype(str)

        if len(self._training_indices) > 0 and len(self._target_column_indices) > 0:
            self._target_columns_metadata = self._get_target_columns_metadata(self._training_outputs.metadata,
                                                                              self.hyperparams)
            model_args = ModelArguments()
            data_args = DataTrainingArguments()
            # TODO: Expose these as hyper-parameters
            data_args.pad_to_max_length = True
            data_args.max_seq_length = 128
            training_args = TrainingArguments(output_dir=self.temporary_directory, seed=self.random_seed,
                                              do_train=True, do_eval=True, num_train_epochs=3, disable_tqdm=True)

            labels = self._training_outputs.values[:, 0]
            # Hugging Face can infer the labels and text portion of the data but lets make it easy for it to do the
            # correct thing by using the column headers it prefers
            dataframe = pd.DataFrame({'label': labels, 'sentence': self._inputs.values[:, 0]})
            # Make sure the label column is numeric
            dataframe['label'] = pd.to_numeric(dataframe['label'])

            # Remove any rows with empty text field to avoid hugging face exception
            dataframe['sentence'].replace('', np.nan, inplace=True)
            dataframe.dropna(subset=['sentence'], inplace=True)

            total_rows = len(dataframe.index)

            # Writing the data to csv files first allows us to use the load_dataset method which populates a bunch of
            # metadata fields that HF requires during training. The API indicates you should be able to use
            # Dataset.from_pandas(df) https://huggingface.co/docs/datasets/loading_datasets.html but it does not behave
            # in the same way by populating the dataset object in a way that makes the trainer accept it.
            dataframe.iloc[0:int(total_rows * .95)].to_csv("%s/train_data.csv" % self.temporary_directory, index=False)
            dataframe.iloc[int(total_rows * .95):].to_csv("%s/validation_data.csv" % self.temporary_directory, index=False)
            data_files = {"train": "%s/train_data.csv" % self.temporary_directory,
                          "validation": "%s/validation_data.csv" % self.temporary_directory}
            datasets = load_dataset("csv", data_files=data_files, cache_dir=self.temporary_directory)

            label_list = datasets["train"].unique("label")
            label_list.sort()  # Let's sort it for determinism
            num_labels = len(label_list)

            config = AutoConfig.from_pretrained(
                model_args.config_name if model_args.config_name else model_args.model_name_or_path,
                num_labels=num_labels,
                finetuning_task=None,
                cache_dir=None,
                revision='main',
                use_auth_token=False,
            )
            tokenizer = AutoTokenizer.from_pretrained(
                model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
                cache_dir=model_args.cache_dir,
                use_fast=model_args.use_fast_tokenizer,
                revision=model_args.model_revision,
                use_auth_token=True if model_args.use_auth_token else None,
            )
            model = AutoModelForSequenceClassification.from_pretrained(
                self.hyperparams['model'],
                from_tf=False,
                config=config,
                cache_dir=self.temporary_directory,
                revision='main',
                use_auth_token=None,
            )

            # Padding strategy
            if data_args.pad_to_max_length:
                padding = "max_length"
            else:
                # We will pad later, dynamically at batch creation, to the max sequence length in each batch
                padding = False

            label_to_id = {v: i for i, v in enumerate(label_list)}
            max_seq_length = min(data_args.max_seq_length, tokenizer.model_max_length)

            def preprocess_function(examples):
                # Tokenize the texts
                args = (examples['sentence'],)
                result = tokenizer(*args, padding=padding, max_length=max_seq_length, truncation=True)

                # Map labels to IDs
                if label_to_id is not None and "label" in examples:
                    result["label"] = [(label_to_id[l] if l != -1 else -1) for l in examples["label"]]
                return result

            datasets = datasets.map(preprocess_function, batched=True, load_from_cache_file=not data_args.overwrite_cache)
            if training_args.do_train:
                if "train" not in datasets:
                    raise ValueError("--do_train requires a train dataset")
                train_dataset = datasets["train"]
                if data_args.max_train_samples is not None:
                    train_dataset = train_dataset.select(range(data_args.max_train_samples))

            # TODO: Expose the evaluation step as an option
            if training_args.do_eval:
                if "validation" not in datasets and "validation_matched" not in datasets:
                    raise ValueError("--do_eval requires a validation dataset")
                eval_dataset = datasets["validation"]
                if data_args.max_eval_samples is not None:
                    eval_dataset = eval_dataset.select(range(data_args.max_eval_samples))

            # Log a few samples from the training set:
            for index in range(3):
                print(f"Sample {index} of the training set: {train_dataset[index]}.")

            # For now we only support accuracy
            def compute_metrics(p: EvalPrediction):
                preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
                preds =  np.argmax(preds, axis=1)
                return {"accuracy": (preds == p.label_ids).astype(np.float32).mean().item()}

            # TODO: Consider exposing data collator. For now will default to DataCollatorWithPadding, so we change it
            #  if the padding was already performed
            if data_args.pad_to_max_length:
                data_collator = default_data_collator
            elif training_args.fp16:
                data_collator = DataCollatorWithPadding(tokenizer, pad_to_multiple_of=8)
            else:
                data_collator = None

            # Initialize the Trainer
            self._trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                compute_metrics=compute_metrics,
                tokenizer=tokenizer,
                data_collator=default_data_collator,
            )

            # Training can pick up where it left off in case of interruption
            checkpoint = get_last_checkpoint(self.temporary_directory)
            train_result = self._trainer.train(resume_from_checkpoint=checkpoint)
            metrics = train_result.metrics
            max_train_samples = (
                data_args.max_train_samples if data_args.max_train_samples is not None else len(datasets)
            )
            metrics["train_samples"] = min(max_train_samples, len(datasets))

            # Saves the tokenizer also
            self._trainer.save_model()
            self._trainer.log_metrics("train", metrics)
            self._trainer.save_metrics("train", metrics)
            self._trainer.save_state()

            self._is_fit = True

            # Run the validation dataset to see how the final models perfomance is
            metrics = self._trainer.evaluate(eval_dataset=eval_dataset)

            max_val_samples = data_args.max_val_samples if data_args.max_val_samples is not None else len(eval_dataset)
            metrics["eval_samples"] = min(max_val_samples, len(eval_dataset))

            self._trainer.log_metrics("eval", metrics)
            self._trainer.save_metrics("eval", metrics)
            print(f"Metrics: {metrics}")
        else:
            if self.hyperparams['error_on_no_input']:
                raise RuntimeError("No input columns were selected")
            self.logger.warn("No input columns were selected")
        return CallResult(None)


    def produce(self, *, inputs: container.DataFrame, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        tl_inputs, columns_to_use = self._get_columns_to_fit(inputs, self.hyperparams)

        if len(tl_inputs.columns):
            # Load data by generating csv first
            dataframe = pd.DataFrame({'sentence': tl_inputs.values[:, 0]})
            # Just put a place holder string in there so we have the correct number of predictions at the end
            dataframe['sentence'].replace('', 'empty', inplace=True)

            # Use this to limit how many of the test records you want to score for debugging purposes
            dataframe.to_csv("%s/test_data.csv" % self.temporary_directory, index=False)

            data_files = {"test": "%s/test_data.csv" % self.temporary_directory}
            datasets = load_dataset("csv", data_files=data_files)

            model_args = ModelArguments()
            data_args = DataTrainingArguments()
            data_args.pad_to_max_length = True
            data_args.max_seq_length = 128
            tokenizer = AutoTokenizer.from_pretrained(
                model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
                cache_dir=model_args.cache_dir,
                use_fast=model_args.use_fast_tokenizer,
                revision=model_args.model_revision,
                use_auth_token=True if model_args.use_auth_token else None,
            )

            if data_args.pad_to_max_length:
                padding = "max_length"
            else:
                # We will pad later, dynamically at batch creation, to the max sequence length in each batch
                padding = False

            max_seq_length = min(data_args.max_seq_length, tokenizer.model_max_length)

            def preprocess_function(examples):
                # Tokenize the texts
                args = (examples['sentence'],)
                result = tokenizer(*args, padding=padding, max_length=max_seq_length, truncation=True)

                return result

            datasets = datasets.map(preprocess_function, batched=True, load_from_cache_file=not data_args.overwrite_cache)
            test_dataset = datasets["test"]

            # Log a few samples from the test set:
            for index in range(3):
                print(f"Sample {index} of the test set: {test_dataset[index]}.")

            # Get the predictions for the test records
            predictions = self._trainer.predict(test_dataset=test_dataset).predictions
            # Convert the confidences to discrete predictions (1 or 0)
            predictions = np.argmax(predictions, axis=1)

            if not self._is_fit:
                raise ValueError("Primitive has not been fitted")

            output = self._wrap_predictions(inputs, predictions)

            output.columns = self._target_names
        else:
            if self.hyperparams['error_on_no_input']:
                raise RuntimeError("No input columns were selected")
            self.logger.warn("No input columns were selected")

        outputs = base_utils.combine_columns(
            return_result=self.hyperparams['return_result'],
            add_index_columns=self.hyperparams['add_index_columns'],
            inputs=inputs, column_indices=self._target_column_indices,
            columns_list=[output]
        )

        return CallResult(outputs)


    def get_params(self) -> Params:
        if not self._is_fit:
            return Params(
                trainer_=None,
                input_column_names=self._input_column_names,
                training_indices_=self._training_indices,
                target_names_=self._target_names,
                target_column_indices_=self._target_column_indices,
                target_columns_metadata_=self._target_columns_metadata
            )
        return Params(
            trainer_=self._trainer,
            input_column_names=self._input_column_names,
            training_indices_=self._training_indices,
            target_names_=self._target_names,
            target_column_indices_=self._target_column_indices,
            target_columns_metadata_=self._target_columns_metadata
        )


    def set_params(self, *, params: Params) -> None:
        self._trainer = params['trainer_']
        self._input_column_names = params['input_column_names']
        self._training_indices = params['training_indices_']
        self._target_names = params['target_names_']
        self._target_column_indices = params['target_column_indices_']
        self._target_columns_metadata = params['target_columns_metadata_']
        if params['trainer_'] is not None:
            self._is_fit = True
        return


    @classmethod
    def _get_columns_to_fit(cls, inputs: container.DataFrame, hyperparams: Hyperparams) -> Tuple[
        container.DataFrame, List[int]]:
        if not hyperparams['use_semantic_types']:
            return inputs, list(range(len(inputs.columns)))

        inputs_metadata = inputs.metadata

        def can_produce_column(column_index: int) -> bool:
            return cls._can_produce_column(inputs_metadata, column_index, hyperparams)

        columns_to_produce: List[Any] = []

        columns_to_produce, columns_not_to_produce = base_utils.get_columns_to_use(
            inputs_metadata,
            use_columns=hyperparams['use_inputs_columns'],
            exclude_columns=hyperparams['exclude_inputs_columns'],
            can_use_column=can_produce_column
        )
        return inputs.iloc[:, columns_to_produce], columns_to_produce
        # return columns_to_produce


    @classmethod
    def _can_produce_column(cls, inputs_metadata: metadata_base.DataMetadata, column_index: int,
                            hyperparams: Hyperparams) -> bool:
        column_metadata = inputs_metadata.query((metadata_base.ALL_ELEMENTS, column_index))

        accepted_structural_types = (int, str, np.integer)
        accepted_semantic_types = set()
        accepted_semantic_types.add("https://metadata.datadrivendiscovery.org/types/Attribute")
        if not issubclass(column_metadata['structural_type'], accepted_structural_types):
            return False

        semantic_types = set(column_metadata.get('semantic_types', []))

        if len(semantic_types) == 0:
            cls.logger.warning("No semantic types found in column metadata")
            return False
        # Making sure all accepted_semantic_types are available in semantic_types
        if len(accepted_semantic_types - semantic_types) == 0:
            return True

        return False


    @classmethod
    def _get_targets(cls, data: container.DataFrame, hyperparams: Hyperparams) -> Tuple[container.DataFrame, list, Any]:
        if not hyperparams['use_semantic_types']:
            return data, list(data.columns), list(range(len(data.columns)))
        metadata = data.metadata

        def can_produce_column(column_index: int) -> bool:
            accepted_semantic_types = set()
            accepted_semantic_types.add("https://metadata.datadrivendiscovery.org/types/TrueTarget")
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = set(column_metadata.get('semantic_types', []))
            if len(semantic_types) == 0:
                cls.logger.warning("No semantic types found in column metadata")
                return False
            # Making sure all accepted_semantic_types are available in semantic_types
            if len(accepted_semantic_types - semantic_types) == 0:
                return True
            return False

        target_column_indices, target_columns_not_to_produce = base_utils.get_columns_to_use(
            metadata,
            use_columns=hyperparams['use_outputs_columns'],
            exclude_columns=hyperparams['exclude_outputs_columns'],
            can_use_column=can_produce_column
        )
        targets: container.DataFrame
        if target_column_indices:
            targets = data.select_columns(target_column_indices)
        target_column_names = []
        for idx in target_column_indices:
            target_column_names.append(data.columns[idx])
        return targets, target_column_names, target_column_indices


    @classmethod
    def _get_target_columns_metadata(cls, outputs_metadata: metadata_base.DataMetadata, hyperparams: Hyperparams) -> \
    List[OrderedDict]:
        outputs_length = outputs_metadata.query((metadata_base.ALL_ELEMENTS,))['dimension']['length']

        target_columns_metadata: List[OrderedDict] = []
        for column_index in range(outputs_length):
            column_metadata = OrderedDict(outputs_metadata.query_column(column_index))

            # Update semantic types and prepare it for predicted targets.
            semantic_types = set(column_metadata.get('semantic_types', []))
            semantic_types_to_remove = set(["https://metadata.datadrivendiscovery.org/types/TrueTarget",
                                            "https://metadata.datadrivendiscovery.org/types/SuggestedTarget"])
            add_semantic_types = set(["https://metadata.datadrivendiscovery.org/types/PredictedTarget"])
            add_semantic_types.add(hyperparams["return_semantic_type"])
            semantic_types = semantic_types - semantic_types_to_remove
            semantic_types = semantic_types.union(add_semantic_types)
            column_metadata['semantic_types'] = list(semantic_types)

            target_columns_metadata.append(column_metadata)

        return target_columns_metadata


    @classmethod
    def _update_predictions_metadata(cls, inputs_metadata: metadata_base.DataMetadata, outputs: container.DataFrame,
                                     target_columns_metadata: List[OrderedDict]) -> metadata_base.DataMetadata:
        outputs_metadata = metadata_base.DataMetadata().generate(value=outputs)

        for column_index, column_metadata in enumerate(target_columns_metadata):
            column_metadata.pop("structural_type", None)
            outputs_metadata = outputs_metadata.update_column(column_index, column_metadata)

        return outputs_metadata


    def _wrap_predictions(self, inputs: container.DataFrame, predictions: np.ndarray) -> container.DataFrame:
        outputs = container.DataFrame(predictions, generate_metadata=False)
        outputs.metadata = self._update_predictions_metadata(inputs.metadata, outputs, self._target_columns_metadata)
        return outputs




































