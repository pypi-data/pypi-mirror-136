from traitlets.config import Config
from metaflow.cards import MetaflowCard
from metaflow import current
import papermill as pm
from pathlib import Path
from nbconvert import HTMLExporter
import nbformat
import json

class NotebookCard(MetaflowCard):

    type = 'notebook'

    def __init__(self, options={'options_dict_nm':'nb_options_dict'}, **kwargs):
        self._attr_options_dict_nm = options.get('options_dict_nm', 'nb_options_dict')


    def render(self, task):
        # Get the options dict from the task
        if not self._attr_options_dict_nm in task:
            raise ValueError(f"Must specify {self._attr_options_dict_nm} in task: {task.parent.pathspec}")
        else:
            self.options = task[self._attr_options_dict_nm].data

        # Validate `input_path`
        if 'input_path' not in self.options or not self.options['input_path']:
            raise ValueError(f"Must specify 'input_path' in {self._attr_options_dict_nm} in task: {task.parent.pathspec}")
        else:
            self.input_path = Path(self.options['input_path'])
            if not self.input_path.name.endswith('.ipynb'):
                raise ValueError(f"input_path must be a notebook file, not {self.input_path}")
            if not self.input_path.exists():
                raise ValueError(f"Input notebook does not exist: {self.input_path}\n The current directory is {Path.cwd()}")

        self.exclude_input = self.options.get('exclude_input', True)

        # Configure rendering options for notebook
        c = Config()
        c.HTMLExporter.exclude_input_prompt = True
        c.HTMLExporter.exclude_output_prompt = True
        c.HTMLExporter.exclude_input = self.exclude_input
        self.html_exporter = HTMLExporter(config=c, template_name = 'lab') #can be lab, classic, or basic
        self.flow_name = current.flow_name

         # inject `run_id`, `task_id` and `flow_name`` into the parameters
        run_id = task.parent.parent.id
        params = self.options.get('parameters', {})
        params.update(dict(run_id=task.parent.parent.id, flow_name=self.flow_name, task_id=task.id))
        self.options['parameters'] = params

        # Calcualate output path and filename if none is given for the rendered notebook
        if 'output_path' not in self.options or not self.options['output_nb']:
            new_fn = f"_rendered_{run_id}_{task.id}_{self.input_path.name}"
            self.output_path = self.input_path.with_name(new_fn)
        else:
            self.output_path = self.options['output_nb']

        # Clean up papermill_options for any conflicting options
        for k in ['input_path', 'output_path']:
            self.options.pop(k, None)

        # Execute the notebook
        pm.execute_notebook(input_path=self.input_path,
                            output_path=self.output_path,
                            **self.options)
        
        # Render the notebook to HTML
        with open(self.output_path, 'r') as f:
            notebook = nbformat.reads(f.read(), as_version=4)
            (body, _) = self.html_exporter.from_notebook_node(notebook)
            return body

CARDS = [NotebookCard]
