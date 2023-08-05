# SRI Primitives Implementation Repository
This repository contains the code needed to generate primitive definitions and sample pipelines for the SRI D3M
primitives. Following are instructions on how to build these artifacts and merge them into the official D3M 
primitive repository:


What is in this file?
----------------------
This file contains instructions on maintaining SRI's D3M primitives. The intention is to allow JPL to pick up where
SRI left off when their funding runs out in mid 2021.


Support
-------
Please contact Daragh Hartnett (daragh.hartnett@sri.com) for support.


How to generate the SRI primitive definitions and sample pipelines
------------------------------------------------------------------
1. First clone the d3m_sri repository (this repo) where the SRI primitive implementations reside. Also clone your fork 
   of the primitives repo - this is where we will add the updated primitives and make an MR to the main primitives repo 
   (for more information on this process see https://gitlab.com/datadrivendiscovery/primitives).

   ```shell
   git clone https://gitlab.com/daraghhartnett/sri_d3m
   git clone https://gitlab.com/<username>/primitives
   ```

2. Build the SRI primitive library and push it to PyPi (*)

    ```shell
    cd sri_d3m
    python setup.py sdist bdist_wheel
    twine upload dist/*
    ```

    For debugging cycles, instead of pushing to PyPi, install the sri_d3m library directly into the docker image. For
    example:
      
    ```dockerfile
    # Patch the local sri_d3m code into the docker image
    RUN pip3 uninstall -y sri_d3m
    COPY sri_d3m/ /user_dev/sri_d3m
    WORKDIR /user_dev/sri_d3m
    RUN pip3 install -e .
   ```

3. Update: The code now includes a sample Dockerfile that can be used to generate the primitive definitions. It is 
   located here `./docker/Dockerfile`. The Dockerfile is very basic. It is based on one of the recent D3M stable 
   releases. It first uninstalls the existing version of the sri_d3m library and then installs the local version of the
   sri_d3m code from the cloned repository. This docker image can be built with the following command:
   
   ```shell
   docker build -f docker/Dockerfile -t name_of_the_image:tag .
   ```

   Install the built sri_d3m library in the latest stable D3M image. We use the latest SRI Dockerfile
   (https://gitlab.com/daraghhartnett/tpot-ta2/-/blob/master/docker/complete_2020.11.03/Dockerfile) to build a suitable 
   image, but any image based on the stable docker image
   (registry.gitlab.com/datadrivendiscovery/images/primitives:ubuntu-bionic-python36-stable-20201201-223410) can be
   used. To patch the stable image with the latest sri-d3m library, in the Dockerfile first remove the current sri_d3m
   library and then install the version uploaded to PyPi in the previous step:

   ```dockerfile
   RUN pip3 uninstall -y sri-d3m
   RUN pip3 install sri-d3m==1.9.6
   ```

   Alternative 1: In debugging cycles, uploading the sri-d3m library to PyPi can be time consuming - to avoid this you 
   can install a local build of the sri-d3m library into a docker image using the following mechanism

   ```dockerfile
   RUN pip3 uninstall -y sri-d3m
   RUN pip3 install $CODE/sri-d3m-1.9.6.tar.gz
   ```
   
   Alternative 2: You can avoid building the sri_d3m image each time and simply copy the sri_d3m repo directly to where
   the docker image is being built. Here is how you would install it in the Dockerfile:
   
   ```dockerfile
   RUN pip3 uninstall -y sri_d3m
   COPY sri_d3m/ /user_dev/sri_d3m
   WORKDIR /user_dev/sri_d3m
   RUN pip3 install -e .
   ```
   
4. When the docker image is ready to be used to generate the primitive definitions and sample pipelines, update the
   following parameters in sri/common/config.py in the sri_d3m repo:

        * DOCKER_IMAGE: The complete docker image that should be used to run the sample pipelines for each of the sri
                        primitives. For example: registry.datadrivendiscovery.org/j18_ta2eval/sri_tpot:20200518. This is
                        the image built in step 3.
        * DATASET_HOME: The location of the seed datasets on the machine you are running
        * VERSION: The version of our primitives that are being generated (this should match the latest version i.e
                   1.9.6 in step 3)

5. Note 1: The only time you need to perform this step, to update the sri/pipelines/parsed_datasets.py, is when new 
   datasets are added, or when they change (the task type of size for example).\
   Note 2: Only datasets that are used in the sample pipelines need to be included in the sri/pipelines/parsed_datasets.py
   json data structure.\
   The script in step 7 uses a json structure that holds information about the available datasets. See 
   the python module here: sri/pipelines/parsed_datasets.py. This module is generated when the scripts/parse_datasets.py 
   script is run. The output of running the scripts/parse_datasets.py (with the path to the datasets directory as a 
   parameter) is the updated sri/pipelines/parsed_datasets.py. 
   An alternative to running the scripts/parse_datasets.py script is to manually update the json that describes an 
   updated or new dataset. Here is an example of a dataset description from the sri/pipelines/parsed_datasets.py module.
   
   ```json
    {
        "name": "JIDO_SOHR_Articles_1061",
        "dataset_id": "JIDO_SOHR_Articles_1061_dataset",
        "problem_id": "JIDO_SOHR_Articles_1061_problem",
        "task_type": "classification",
        "size": 13188,
        "train_dataset_id": "JIDO_SOHR_Articles_1061_dataset_TRAIN",
        "train_problem_id": "JIDO_SOHR_Articles_1061_problem",
        "test_dataset_id": "JIDO_SOHR_Articles_1061_dataset_TEST",
        "test_problem_id": "JIDO_SOHR_Articles_1061_problem",
        "score_dataset_id": "JIDO_SOHR_Articles_1061_dataset_SCORE",
        "score_problem_id": "JIDO_SOHR_Articles_1061_problem"
    }
   ```

   Here is an example of using the parse_datasets.py script to generate the sri/pipelines/parsed_datasets.py module:

   ```shell
   python scripts/parse_datasets.py /datasets/seed_datasets_current > sri/pipelines/parsed_datasets.py
   ```

6. Before running the following script, you will need to have the latest d3m library installed in the python environment
   you are using:
   
   ```shell
   pip3 install d3m
   ```

   This is used to generate the primitive definitions using the `python3 -m d3m index describe` command

7. Run the following script in the base directory of the sri_d3m library to generate the primitive artifacts, construct
   the sample pipelines, and run them to produce the pipeline runs. 
   Note 1: See the section at the bottom Notes on the HuggingFace Primitive DistilBertTextClassification: 5 about options
   for speeding up this step which currently takes hours on a laptop without a GPU.

    ```shell
    sh scripts/generate_primitive_definitions.sh <absolute path to the clone of the primitives repo>
    For example:
    sh scripts/generate_primitive_definitions.sh /home/projects/d3m/primitives
    ```
   
   Once this script is complete, you will find a new folder in the /home/projects/d3m/primitives folder called `SRI`. 
   This will contain all the required files needed to make an MR to the official D3M primitives repository. For example:
   
   ```shell
   |____SRI
   | |____d3m.primitives.data_transformation.simple_column_parser.DataFrameCommon
   | | |____1.9.6
   | | | |____pipelines
   | | | |____pipeline_runs
   | |____d3m.primitives.classification.bert_classifier.DistilBertTextClassification
   | | |____1.9.6
   | | | |____pipelines
   | | | |____pipeline_runs
   | |____d3m.primitives.data_transformation.conditioner.Conditioner
   | | |____1.9.6
   | | | |____pipelines
   | | | |____pipeline_runs
   | |____d3m.primitives.data_preprocessing.dataset_text_reader.DatasetTextReader
   | | |____1.9.6
   | | | |____pipelines
   | | | |____pipeline_runs
   ```
   

Notes on the HuggingFace Primitive DistilBertTextClassification
---------------------------------------------------------------

1. Useful links for future work:

   * We are currently training just the top layer. To train the representation layer we would need to supply a 
     model_init callable that is based on a template model. This would be a good HP to expose.
   
       * example: https://huggingface.co/blog/how-to-train#3-train-a-language-model-from-scratch
       * API (Look at the ‘model’ and ‘model_init’ args): https://huggingface.co/transformers/_modules/transformers/trainer.htm
       * https://huggingface.co/blog/how-to-train
       * https://stackoverflow.com/questions/66828699/hugging-face-trainer-error-in-the-model-init
   
   * List of all pretrained models: 
       * https://huggingface.co/transformers/pretrained_models.html
       * https://huggingface.co/transformers/model_doc/auto.html?highlight=automodelforsequenceclassification#transformers.AutoModelForSequenceClassification

   
   * Repo with the example code: https://github.com/huggingface/transformers
   
   * Example of text classification in a python notebook: https://colab.research.google.com/github/huggingface/notebooks/blob/master/examples/text_classification.ipynb#scrollTo=u3EtYfeHIrIz

2. Common problems and their causes. While integrating the HF code into the D3M environment, we experienced a few 
   error messages that were not very helpful in determining their cause. These are noted here in the hopes they will
   save someone some time in the future.

   * **Error:** Too many dimensions:

       ```python
           File "/miniconda3/envs/20201103/lib/python3.6/site-packages/transformers/data/data_collator.py", line 65, in default_data_collator
                 batch["labels"] = torch.tensor([f["label"] for f in features], dtype=dtype)
                 ValueError: too many dimensions 'str'
       ```
         
       **Cause:** Need to convert the labels in the pandas df to a numeric before passing it to the dataset.from_panda. 
       Note that we ended up not using the from_panda method due to later incompatibilities - see the following error
       message. If you do want to make the labels numeric - here is an easy way:
     
       ```python
       dataframe['labels'] = pd.to_numeric(dataframe['labels'])
       ```
     
   * **Error:** 'DataFrame' object has no attribute 'features': 
     
       ```python
       File "/Users/daraghhartnett/miniconda3/envs/hugging_face_451/lib/python3.6/site-packages/pandas/core/generic.py", line 5141, in __getattr__
         return object.__getattribute__(self, name)
       AttributeError: 'DataFrame' object has no attribute 'features'
     
       **Cause:** The documentation (https://huggingface.co/docs/datasets/loading_datasets.html) indicates that you can 
       use multiple ways of loading the datasets for training and test. However, the Dataset.from_pandas(df) does not
       populate some metadata that is required by later HF classes that are required to train. I tried adding these 
       manually but it turned into a complicated affair so I cheated by writing the dataframes to csv and used the 
       datasets.load_dataset() method to get the metadata that the later steps needed.
     
   * **Error:** TypeError:
     
       ```python
       File "/Users/daraghhartnett/miniconda3/envs/20201103/lib/python3.6/site-packages/transformers/tokenization_utils_fast.py", line 388, in _batch_encode_plus
           is_pretokenized=is_split_into_words,
       TypeError: TextEncodeInput must be Union[TextInputSequence, Tuple[InputSequence, InputSequence]]
       ```
         
       **Cause:** Records that have empty strings for the text field. 
     
   * **Error:** ValueError: Stream is closed:
     
       ```python
       fp_write('\r' + s + (' ' * max(last_len[0] - len_s, 0)))
        File "/Users/daraghhartnett/miniconda3/envs/20201103/lib/python3.6/site-packages/tqdm/_tqdm.py", line 243, in fp_write
          fp.write(_unicode(s))
        File "/Users/daraghhartnett/miniconda3/envs/20201103/lib/python3.6/site-packages/d3m/utils.py", line 874, in write
          raise ValueError("Stream is closed.")
       ValueError: Stream is closed.
       ```
      
      **Cause:** The D3M logger does not like the tqdm terminal progress bar. This can be disabled by specifying 
      disable_tqdm=True in the TrainingArguments constructor (this is currently in place in the current primitive
      implementation).

3. There is interest in adapting this primitive, or writing another that deals with question answering problems such as
   WikiQA. Here is a tutorial that covers one way to approach this: 
   https://huggingface.co/transformers/usage.html#extractive-question-answering
   

4. Unresolved Warning: In the output when you run the primitive you will notice a couple of exceptions of the form:

      ```shell
      WARNING:d3m.utils:Using global/shared random source using 'random.seed' can make execution not reproducible.
      Stack (most recent call last):
        File "/usr/lib/python3.6/runpy.py", line 193, in _run_module_as_main
          "__main__", mod_spec)
        File "/usr/lib/python3.6/runpy.py", line 85, in _run_code
          exec(code, run_globals)
        File "/src/d3m/d3m/__main__.py", line 6, in <module>
          cli.main(sys.argv)
        File "/src/d3m/d3m/cli.py", line 1264, in main
          handler(arguments, parser)
        File "/src/d3m/d3m/cli.py", line 1146, in handler
          problem_resolver=problem_resolver,
        File "/src/d3m/d3m/cli.py", line 603, in runtime_handler
          problem_resolver=problem_resolver,
        File "/src/d3m/d3m/runtime.py", line 3093, in fit_score_handler
          runtime_environment=runtime_environment,
        File "/src/d3m/d3m/runtime.py", line 1493, in fit
          result = runtime.fit(inputs, outputs_to_expose=outputs_to_expose)
        File "/src/d3m/d3m/deprecate.py", line 140, in wrapper
          return f(*args, **kwargs)
        File "/src/d3m/d3m/runtime.py", line 1251, in fit
          return self._run(inputs, metadata_base.PipelineRunPhase.FIT, outputs_to_expose or return_values)
        File "/src/d3m/d3m/runtime.py", line 1151, in _run
          self._do_run()
        File "/src/d3m/d3m/runtime.py", line 1131, in _do_run
          self._do_run_step(step)
        File "/src/d3m/d3m/runtime.py", line 1114, in _do_run_step
          self._run_step(step)
        File "/src/d3m/d3m/runtime.py", line 1104, in _run_step
          self._run_primitive(step)
        File "/src/d3m/d3m/runtime.py", line 979, in _run_primitive
          multi_call_result = self._call_primitive_method(primitive.fit_multi_produce, fit_multi_produce_arguments)
        File "/src/d3m/d3m/runtime.py", line 1076, in _call_primitive_method
          result = method(**arguments)
        File "/src/d3m/d3m/primitive_interfaces/base.py", line 534, in fit_multi_produce
          return self._fit_multi_produce(produce_methods=produce_methods, timeout=timeout, iterations=iterations, inputs=inputs, outputs=outputs)
        File "/src/d3m/d3m/primitive_interfaces/base.py", line 561, in _fit_multi_produce
          fit_result = self.fit(timeout=timeout, iterations=iterations)
        File "/user_dev/sri_d3m/sri/neural_text/distil_bert_text_classification.py", line 494, in fit
          data_collator=default_data_collator,
        File "/usr/local/lib/python3.6/dist-packages/transformers/trainer.py", line 264, in __init__
          set_seed(self.args.seed)
        File "/usr/local/lib/python3.6/dist-packages/transformers/trainer_utils.py", line 57, in set_seed
          random.seed(seed)
        File "/src/d3m/d3m/utils.py", line 1160, in wrapper
          ignore_modules=ignore_random_warnings,
        File "/src/d3m/d3m/utils.py", line 1617, in log_once
          logger.log(level, msg, *args, **kwargs)
      ```

   This warning is being emitted from the D3M core code with respect to the transformer library using a random seed. I 
   tried setting a seed but the error still occurs - It seems that the D3M code checks for the use of 
   'random.seed(seed)' and does not like it. 
   I am not sure there is anything we can do to prevent the warning without making a change to one of the two libraries 
   (D3M or HuggingFace).

5. On a Mac Laptop with no GPU the HF Text Classification primitive is *slooow*. This is due to the absence of a GPU 
   (we have not tested how much of a speed up this provides but would be interested in knowing if anyone gets a chance
   to do so). 
   As such, running the `scripts/generate_primitive_definitions.sh` takes many hours as it generates a sample pipeline 
   and runs it on the JIDO_SOHR_Articles_1061 seed dataset. There are a few options for accelerating this process:
   
      * Use a GPU. As noted, we have not had a chance to test this but it should make the run time significantly 
         shorter.
      * Reduce the number of epochs. The default number of epochs is 3. Reducing this to 1 will yield a big saving in 
         training time. Here is the line of code where the epochs are specified:

         ```python
            training_args = TrainingArguments(output_dir=self.temporary_directory, seed=self.random_seed,
                                  do_train=True, do_eval=True, num_train_epochs=1, disable_tqdm=True) 
         ```               
         Note: There is a TODO mentioned in the code that the epochs should be exposed as a parameter.

      * Comment out the evaluation step. By default, the fit methond in the primitive code will hold out 5% of the 
         training data to perform an evaluation to get a rough measure of model performance. Here are the lines that 
         can be commented out to avoid this:
         
         ```python
            metrics = self._trainer.evaluate(eval_dataset=eval_dataset)

            max_val_samples = data_args.max_val_samples if data_args.max_val_samples is not None else len(eval_dataset)
            metrics["eval_samples"] = min(max_val_samples, len(eval_dataset))

            self._trainer.log_metrics("eval", metrics)
            self._trainer.save_metrics("eval", metrics)
            print(f"Metrics: {metrics}")
         ```
         
         Note: There is a TODO mentioned in the code that the option of running the evaluation step should be exposed 
         as a parameter.
         

Primitive Test Code:
--------------------
Before the `scripts/generate_primitive_definitions.sh` script was written (see the `How to generate the SRI primitive 
definitions and sample pipelines` section above for details) we used a set of unit tests for the primitives. These
tests are launched by running the `run_tests.sh` script located in this directory. Note, the 
`scripts/generate_primitive_definitions.sh` script is an updated version of this test system and has been adapted to 
recent changes in the D3M code base and dataset formats. As such it is possible that some of the test modules described
below will need to be updated to run properly. We recommend using the `scripts/generate_primitive_definitions.sh` 
instead of these test scripts.\
The `run_tests.sh` script does the following:

    * Build and install the sri_d3m library in the current python environment
    * Create a directory in the `./tests` folder called `data` and clone the entire seed dataset repository to that 
      folder. This script was written about 2.5 years ago when there were far fewer seed datasets and cloning the 
      entire repo was not a big deal.
    * Calls the `run_tests_internal.py` script which runs all tests located in the `./tests` folder. This currently 
      consists of just the `test_pipelines.py` module which generates the pipeline.json for each primitive and runs
      `fit` and then `produce` on each of those pipelines.
    * Note 1: The `test_static_ensembler.py` is a standalone test for a primitive that we never completed. 
    * Note 2: The `util.py` module provides helper methods to the `test_pipelines.py` module.
    * Note 3: This script is designed to be run on a unix system (will not run as is on a mac)
    * Note 4: This script is an early verions replica of the `scripts/generate_primitive_definitions.sh`


   
