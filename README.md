# promhacks

Feel free to use this as a source of inspiration or as a starting point but do
not use this in production directly.

* `rules-conv.py`: ad-hoc script to convert Prometheus 1.x rules to the
  Prometheus 2.x YAML format. The automatic conversion with `promtool` has the
  problem that it removes comments and formatting. This script makes a _lot_ of
  assumptions of how you have formatted your rules. It does _not_ parse the
  Prometheus 1.x rules format. It essentially just kicks stuff around, and if
  your rules follow all the assumptions it makes, you'll get valid YAML output.

