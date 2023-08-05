# irisml-tasks-training

This is a package for IrisML training-related tasks.

## Tasks

### train
Train a pytorch model. A model object must have "criterion" and "predictor" property. See the documents for the detail. Returns a trained model.

### predict
Run inference with a given pytorch model. Returns prediction results.

### export_onnx
Trace a pytorch model and export it as ONNX using torch.onnx.export(). Throws an exception if it couldn't export. Returns an exported onnx model.

### evaluate_accuracy
Calculate top1 accuracy for given prediction results. It supports only image classification results.

### evaluate_detection_average_precision
Calculate mAP for object detection results.

## Available plugins for train task.
- log_summary
- log_tensorboard
- progressbar
