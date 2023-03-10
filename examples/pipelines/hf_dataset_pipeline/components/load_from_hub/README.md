This component can be run as follows:

```
python3 main.py --extra-args '{"dataset_name": "lambdalabs/pokemon-blip-captions"}' \
 --output-manifest <local_path> \
  --metadata-args '{"run_id":"test","component_name":"test_component", \
  "artifact_bucket":"soy-audio-379412_kfp-artifacts"}'
```