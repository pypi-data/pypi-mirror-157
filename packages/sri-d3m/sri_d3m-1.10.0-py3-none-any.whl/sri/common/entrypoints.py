ENTRYPOINTS = {
    'd3m.primitives': {
        # SRI Primitives
        'data_transformation.conditioner.Conditioner': 'sri.autoflow.conditioner:Conditioner',
        'data_preprocessing.dataset_text_reader.DatasetTextReader': 'sri.autoflow.dataset_text_reader:DatasetTextReader',
        'data_transformation.simple_column_parser.DataFrameCommon': 'sri.autoflow.simple_column_parser:SimpleColumnParser',
        'classification.bert_classifier.DistilBertTextClassification': 'sri.neural_text.distil_bert_text_classification:DistilBertTextClassification',

        # Eriq's Primitives
        'learner.model.GeneralRelational': 'sri.psl.general_relational:GeneralRelational',
    }
}

def get_entrypoints_definition():
    all_entrypoints = {}

    for (top_level, entrypoints) in ENTRYPOINTS.items():
        points = []

        for (entrypoint, target) in entrypoints.items():
            points.append("%s = %s" % (entrypoint, target))

        all_entrypoints[top_level] = points

    return all_entrypoints

# Get all the entrypoints.
def main():
    for (top_level, entrypoints) in ENTRYPOINTS.items():
        for entrypoint in entrypoints:
            print("%s.%s" % (top_level, entrypoint))

if __name__ == '__main__':
    main()
