#!/usr/bin/python3

# Converts Prom1.x rule format into Prom2.x while keeping formatting
# and comments. This does not work in general. Some valid Prom1 rules
# files might not get converted properly.

import glob
import re

def convert(rules, yaml):
    indent = 2
    in_alert = False
    in_record = False
    in_expr = False
    in_labels = False
    for line in rules:
        if not line: break
        # Keep empty lines. Assume that this always ends a rule.
        if line.strip() == "":
            print(file=yaml)
            if not in_labels and not in_expr:
                in_alert = False
                in_record = False
                indent = 2
            continue
        # Plain comments.
        if line.strip().startswith('#'):
            yaml.write(indent*' ' + line)
            # Assume that an unindented comment ends a rule.
            if line.startswith('#') and not in_labels and not in_expr:
                in_alert = False
                in_record = False
                indent = 2
            continue
        # Continue / end alert.
        if in_alert:
            components = line.split()
            if components[0] == 'IF':
                # Assume that IF is always the start of the expr block.
                in_expr = True
                indent = 4
                print('    expr: |2', file=yaml)
                if len(components) > 1:
                    yaml.write((indent+2)*' ' + ' '.join(components[1:]) + '\n')
                continue
            if components[0] == 'FOR':
                # Assume that FOR is always the FOR entry.
                in_expr = False
                in_labels = False
                indent = 4
                yaml.write('    for: '+ ' '.join(components[1:]) + '\n')
                continue
            if components[0] == 'LABELS':
                # Assume that LABELS is always the start of the labels block.
                in_expr = False
                in_labels = True
                indent = 6
                print('    labels:', file=yaml)
                continue
            if components[0] == 'ANNOTATIONS':
                # Assume that ANNOTATIONS is always the start of the annotations block.
                in_expr = False
                in_labels = True
                indent = 6
                print('    annotations:', file=yaml)
                continue
            if in_expr:
                if line.startswith('  ') or line.startswith(')'):
                    yaml.write(indent*' ' + line)
                    continue
                if line.startswith('    '):
                    yaml.write((indent-2)*' ' + line)
                    continue
                in_expr = False
                indent = 4
            if in_labels:
                if line.strip().startswith('}'):
                    in_labels = False
                    indent = 4
                    continue
                m = re.match(r'\s*(\w+)\s*=\s*(.*?)\s*,?\s*(#[^"'']*)?$', line)
                yaml.write(indent*' ' + m[1] + ': ' + m[2])
                if m[3]:
                    yaml.write('  ' + m[3])  # Trailing comment.
                yaml.write('\n')
                continue
            in_alert = False
            in_expr = False
            in_labels = False
            indent = 2
        # Continue / end record.
        if in_record:
            if line.startswith(' ') or line.startswith(')'):
                # Assumes that continuations start with blank or ')'.
                yaml.write(indent*' ' + line)
                continue
            in_record = False
            indent = 2
        # Alert start.
        if line.startswith('ALERT '):
            in_alert = True
            indent = 4
            yaml.write('  - alert: '+line[6:].strip()+'\n')
        # Record start.
        else:
            in_record = True
            indent = 6
            m = re.match(r'([\w:]+)\s*(?:\{(.*)\})?\s*=\s*(.*)', line.strip())
            yaml.write('  - record: '+m[1].strip()+'\n')
            if m[2]:
                yaml.write('    labels:\n')
                for lp in m[2].split(','):
                    parts = lp.split('=')
                    yaml.write('      %s: %s\n' % (parts[0].strip(), parts[1].strip()))
            yaml.write('    expr: |2\n')
            if m[3]:
                yaml.write(indent*' ' + m[3] + '\n')

for rules_file in glob.iglob('*.rules'):
    name = re.match(r'(.*)\.rules', rules_file)[1]
    with open(name + '.yml', mode='w') as yaml:
      print('groups:', file=yaml)
      print('- name:', name, file=yaml)
      print('  rules:', file=yaml)

      with open(rules_file) as rules:
          convert(rules, yaml)

      
