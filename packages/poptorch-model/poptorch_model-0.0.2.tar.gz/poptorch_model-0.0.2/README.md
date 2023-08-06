This wrapper is built for pipelining PyTorch model with the annotate function poptorch.BeginBlock. see[[ https://docs.graphcore.ai/projects/poptorch-user-guide/en/latest/overview.html#annotations | PopTorch-annotations ]]

It marks the layers in the model by parsing the layer's path we provide like `model.encoder.layers__1` and we should also provide an `ipu_id` for where the module is placed with the function `set_start_point`
like `obj.set_start_point(('model.encoder.layers__1', 1))`.

Or we can pass multiple annotation point with the function set_start_point_list like `obj.set_start_point_list([('model.encoder.layer__1.layer', 1), ('model.decoder.sub_layer', 2)])`

There are Module and ModuleList for building a PyTorch layer, so we use __{index} to represent a ModuleList and the index.
