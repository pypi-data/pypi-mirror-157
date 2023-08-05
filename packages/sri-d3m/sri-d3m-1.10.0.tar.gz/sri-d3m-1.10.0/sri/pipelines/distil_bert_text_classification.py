from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from d3m.primitives.data_transformation.column_parser import Common as ColumnParser
from d3m.primitives.data_transformation.extract_columns_by_semantic_types import Common as ExtractColumnsBySemanticTypes
from d3m.primitives.data_transformation.dataset_to_dataframe import Common as DatasetToDataFrame
from d3m.primitives.data_preprocessing.dataset_text_reader import DatasetTextReader
from d3m.primitives.data_transformation.construct_predictions import Common as ConstructPredictions
from d3m.primitives.schema_discovery.profiler import Common as SimpleProfiler
from d3m.primitives.classification.bert_classifier import DistilBertTextClassification as DistilBert

from sri.common import constants
from sri.pipelines import datasets
from sri.pipelines.base import BasePipeline


class DistilBertTextClassificationPipeline(BasePipeline):
    def __init__(self):
        super().__init__(('JIDO_SOHR_Articles_1061',), True)

    def _gen_pipeline(self):

        # Create pipeline elements
        step_0_tr = DatasetTextReader(hyperparams={})
        step_1_todf = DatasetToDataFrame(hyperparams=dict(dataframe_resource=None))
        step_2_simple_profiler = SimpleProfiler(hyperparams={})
        step_3_ext_targ = ExtractColumnsBySemanticTypes(hyperparams=dict(semantic_types=(constants.TRUE_TARGET_TYPE,)))
        step_4_cp = ColumnParser(hyperparams={})
        step_5_ext_attr = ExtractColumnsBySemanticTypes(hyperparams=dict(semantic_types=(constants.ATTRIBUTE_TYPE,)))
        step_6_distil_bert = DistilBert(hyperparams={})
        step_7_construct_pred = ConstructPredictions(hyperparams={})

        # Create pipeline instance
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        # Add pipeline steps
        node = self._add_pipeline_step(pipeline, step_0_tr, inputs="inputs.0")
        input_node = self._add_pipeline_step(pipeline, step_1_todf, inputs=node)

        node = self._add_pipeline_step(pipeline, step_2_simple_profiler, inputs=input_node)

        tnode = self._add_pipeline_step(pipeline, step_3_ext_targ, inputs=node)
        node = self._add_pipeline_step(pipeline, step_4_cp, inputs=node)
        node = self._add_pipeline_step(pipeline, step_5_ext_attr, inputs=node)

        node = self._add_pipeline_step(pipeline, step_6_distil_bert, inputs=node, outputs=tnode)
        node = self._add_pipeline_step(pipeline, step_7_construct_pred, inputs=node, reference=input_node)

        # Add pipeline output
        pipeline.add_output(name="Results", data_reference=node)

        return pipeline
